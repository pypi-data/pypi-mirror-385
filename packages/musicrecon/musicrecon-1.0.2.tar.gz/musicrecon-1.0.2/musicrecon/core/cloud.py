import os
import time
import hmac
import base64
import hashlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
from ..utils.logging_util import logger
from .processor import AudioProcessor


class ACRCloudRecognizer:
    """Handles song recognition using ACRCloud API"""

    def __init__(self, access_key: str, access_secret: str, region_url: str):
        self.access_key = access_key
        self.access_secret = access_secret
        self.requrl = region_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create resilient HTTP session with retries"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def recognize_song(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Recognize song from audio file"""
        try:
            # Validate and preprocess audio
            duration = AudioProcessor.get_audio_duration(file_path)
            if duration > 20:
                logger.info("Audio too long, trimming...")
                file_path = AudioProcessor.trim_audio(file_path)

            # Prepare request
            timestamp = str(time.time())
            string_to_sign = self._create_signature_string(timestamp)
            signature = self._generate_signature(string_to_sign)

            file_size = os.path.getsize(file_path)
            logger.debug(f"File size: {file_size / 1024:.1f} KB")

            files, data = self._prepare_request_data(
                file_path, file_size, timestamp, signature
            )

            # Send request
            logger.info("Identifying song...")
            response = self.session.post(
                self.requrl, files=files, data=data, timeout=30
            )
            response.encoding = "utf-8"
            result = response.json()

            return self._parse_response(result)

        except Exception as e:
            logger.error(f"Recognition failed: {e}")
            return None

    def _create_signature_string(self, timestamp: str) -> str:
        """Create signature string for ACRCloud API"""
        return "\n".join(
            ["POST", "/v1/identify", self.access_key, "audio", "1", timestamp]
        )

    def _generate_signature(self, string_to_sign: str) -> str:
        """Generate HMAC signature"""
        sign = hmac.new(
            self.access_secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha1,
        ).digest()
        return base64.b64encode(sign).decode("utf-8")

    def _prepare_request_data(
        self, file_path: str, file_size: int, timestamp: str, signature: str
    ) -> tuple:
        """Prepare files and data for API request"""
        files = [
            (
                "sample",
                (os.path.basename(file_path), open(file_path, "rb"), "audio/wav"),
            )
        ]

        data = {
            "access_key": self.access_key,
            "sample_bytes": file_size,
            "timestamp": timestamp,
            "signature": signature,
            "data_type": "audio",
            "signature_version": "1",
        }

        return files, data

    def _parse_response(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse ACRCloud API response"""
        if result.get("status", {}).get("code") == 0 and "metadata" in result:
            music_data = result["metadata"]["music"][0]
            song_info = {
                "title": music_data.get("title", "Unknown"),
                "artist": music_data.get("artists", [{}])[0].get("name", "Unknown"),
                "album": music_data.get("album", {}).get("name", "Unknown"),
                "release_date": music_data.get("release_date", "Unknown"),
                "genres": [
                    genre.get("name", "") for genre in music_data.get("genres", [])
                ],
                "external_ids": music_data.get("external_ids", {}),
            }
            logger.info(f"🎵 Found: {song_info['title']} by {song_info['artist']}")
            return song_info
        else:
            error_msg = result.get("status", {}).get("msg", "Unknown error")
            logger.warning(f"Recognition failed: {error_msg}")
            return None
