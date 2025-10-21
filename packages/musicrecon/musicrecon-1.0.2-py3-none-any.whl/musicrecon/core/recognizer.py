import os
from ..utils.logging_util import logger
from .processor import AudioProcessor
from .cloud import ACRCloudRecognizer
from .downloader import YouTubeDownloader
from ..managers.history import SearchHistory
from ..managers.secrets import SecretManager


class MusicRecognizer:
    """Main application class"""

    def __init__(self):
        # ACRCloud configuration
        self.secrets = SecretManager().load_secrets()

        self.recognizer = ACRCloudRecognizer(
            access_key=self.secrets.get("access_key", None),
            access_secret=self.secrets.get("access_secret", None),
            region_url="https://identify-eu-west-1.acrcloud.com/v1/identify",
        )
        self.downloader = YouTubeDownloader()
        self.history = SearchHistory()
        self.audio_processor = AudioProcessor()

    def recognize_from_file(
        self, file_path: str, download: bool = False, download_video: bool = False
    ) -> None:
        """Recognize song from audio file"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return

        song_info = self.recognizer.recognize_song(file_path)
        if song_info:
            self.history.save_search(song_info)
            if download:
                query = f"{song_info['title']} {song_info['artist']}"
                self.downloader.download_song(query, download_video)

    def recognize_from_recording(
        self, duration: int = 10, download: bool = False, download_video: bool = False
    ) -> None:
        """Record audio and recognize song"""
        file_path = "recording.wav"
        try:
            self.audio_processor.record_audio(file_path, duration)
            self.recognize_from_file(file_path, download, download_video)
        finally:
            # Clean up recording file
            if os.path.exists(file_path):
                os.remove(file_path)

    def show_history(self, limit: int = 10) -> None:
        """Display search history"""
        history = self.history.get_history(limit)
        if not history:
            logger.info("No search history found")
            return

        logger.info(f"Last {len(history)} searches:")
        for entry in reversed(history):
            song_info = entry.get("song_info", "--No Info--")
            timestamp = entry.get("timestamp", "--No Timestamp--")
            title = (
                song_info.get("title", "--No Title--")
                if isinstance(song_info, dict)
                else "--No Title--"
            )
            artist = (
                song_info.get("artist", "--No Artist--")
                if isinstance(song_info, dict)
                else "--No Artist--"
            )
            print(f"  {timestamp}: {title} - {artist}")

    def download_song(
        self, query: str, download_video: bool = False, quality: str = "best"
    ) -> None:
        """Download specific song by query"""
        logger.info(f"Downloading: {query}")
        success = self.downloader.download_song(query, download_video, quality)
        if success:
            logger.info("Download completed successfully!")
        else:
            logger.error("Download failed")
