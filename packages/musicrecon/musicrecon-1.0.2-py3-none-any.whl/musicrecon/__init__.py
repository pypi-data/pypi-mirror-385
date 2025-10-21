from .cli.main import main
from .core.cloud import ACRCloudRecognizer
from .core.downloader import YouTubeDownloader
from .core.recognizer import MusicRecognizer
from .core.processor import AudioProcessor
from .managers.history import SearchHistory
from .managers.secrets import SecretManager

__version__ = "1.0.2"

__all__ = [
    "ACRCloudRecognizer",
    "YouTubeDownloader",
    "MusicRecognizer",
    "AudioProcessor",
    "SearchHistory",
    "SecretManager",
]
