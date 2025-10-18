from ytfetcher._youtube_dl import get_fetcher
from ytfetcher.models.channel import ChannelData, DLSnippet
from ytfetcher._transcript_fetcher import TranscriptFetcher
from ytfetcher.config.http_config import HTTPConfig
from youtube_transcript_api.proxies import ProxyConfig
from typing import Iterable

class YTFetcher:
    """
    YTFetcher is a high-level interface for fetching YouTube video metadata and transcripts.

    It supports two modes of initialization:
    - From a channel handle (via `from_channel`)
    - From a list of specific video IDs (via `from_video_ids`)

    Internally, it uses the yt-dlp to retrieve video snippets and metadata,
    and the `youtube_transcript_api` (with optional proxy support) to fetch transcripts.

    Args:
        http_config (HTTPConfig): Configuration for HTTP client behavior.
        max_results (int): Maximum number of videos to fetch.
        video_ids (list[str]): List of specific video IDs to fetch.
        channel_handle (str | None): Optional YouTube channel handle (used when fetching from channel).
        proxy_config (ProxyConfig | None): Optional proxy settings for transcript fetching.
    """
    def __init__(self, max_results: int, video_ids: list[str] | None, playlist_id: str | None = None, channel_handle: str | None = None, proxy_config: ProxyConfig | None = None, http_config: HTTPConfig = HTTPConfig(), languages: Iterable[str] = ("en", )):
        self.http_config = http_config
        self.proxy_config = proxy_config
        self.languages = languages

        self.youtube_dl = get_fetcher(channel_handle, playlist_id, video_ids, max_results)
        self.snippets = self.youtube_dl.fetch()

        self.fetcher = TranscriptFetcher(self._get_video_ids(), http_config=self.http_config, proxy_config=self.proxy_config, languages=self.languages)
    
    @classmethod
    def from_channel(cls, channel_handle: str, max_results: int = 50, http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None, languages: Iterable[str] = ("en",)) -> "YTFetcher":
        """
        Create a fetcher that pulls up to max_results from the channel.
        """
        return cls(http_config=http_config, max_results=max_results, video_ids=None, channel_handle=channel_handle, proxy_config=proxy_config, languages=languages)
    
    @classmethod
    def from_video_ids(cls, video_ids: list[str] = [], http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None, languages: Iterable[str] = ("en",)) -> "YTFetcher":
        """
        Create a fetcher that only fetches from given video ids.
        """
        return cls(http_config=http_config, max_results=len(video_ids), video_ids=video_ids, channel_handle=None, proxy_config=proxy_config, languages=languages)
    
    @classmethod
    def from_playlist_id(cls, playlist_id: str, max_results: int = 50, http_config: HTTPConfig = HTTPConfig(), proxy_config: ProxyConfig | None = None, languages: Iterable[str] = ("en",)) -> "YTFetcher":
        """
        Create a fetcher tthat fetches from given playlist id.
        """
        return cls(http_config=http_config, playlist_id=playlist_id, proxy_config=proxy_config, languages=languages, max_results=max_results, video_ids=None)

    async def fetch_youtube_data(self) -> list[ChannelData]:
        """
        Asynchronously fetches transcript and metadata for all videos retrieved from the channel or video IDs.

        Returns:
            list[ChannelData]: A list of objects containing transcript text and associated metadata.
        """

        transcripts = await self.fetcher.fetch()
        
        for transcript, snippet in zip(transcripts, self.snippets):
            transcript.metadata = snippet
        
        return transcripts
    
    async def fetch_transcripts(self) -> list[ChannelData]:
        """
        Returns only the transcripts from cached or freshly fetched YouTube data.

        Returns:
            list[ChannelData]: Transcripts only with video_id (excluding metadata).
        """
        
        return await self.fetcher.fetch()

    async def fetch_snippets(self) -> list[ChannelData] | None:
        """
        Returns the raw snippet data (metadata and video IDs) retrieved from the YouTube Data API.

        Returns:
            list[ChannelData] | None: An object containing video metadata and IDs.
        """

        return [
            ChannelData(
                video_id=snippet.video_id,
                transcripts=None,
                metadata=snippet
            )
            for snippet in self.snippets
        ]

    @property
    def video_ids(self) -> list[str]:
        """
        List of video IDs fetched from the YouTube channel or provided directly.

        Returns:
            list[str]: Video ID strings.
        """
        
        return self._get_video_ids()

    @property
    def metadata(self) -> list[DLSnippet] | None:
        """
        Metadata for each video, such as title, duration, and description.

        Returns:
            list[DLSnippet] | None: List of Snippet objects containing video metadata.
        """
        return [snippet for snippet in self.snippets]
    
    def _get_video_ids(self) -> list[str]:
        """
        Returns list of channel video ids.
        """
        return [snippet.video_id for snippet in self.snippets]