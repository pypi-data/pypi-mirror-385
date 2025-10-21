import re
import yt_dlp as youtube_dl
from ..utils.logging_util import logger


class YouTubeDownloader:
    """Handles YouTube downloads with robust error handling and format fallbacks"""

    def __init__(self):
        self.ydl_opts_base = {
            "outtmpl": "./%(title).100s - %(uploader)s.%(ext)s",
            "noplaylist": True,
            "continuedl": True,
            "nooverwrites": True,
            "writethumbnail": True,
            "embedthumbnail": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "ignoreerrors": True,
            "no_warnings": False,
            "quiet": False,
            "extractaudio": False,  # Let format selection handle this
        }

    def _get_safe_format(self, url: str, download_video: bool = False) -> str:
        """Get a safe format that's actually available"""
        try:
            # First, try to get available formats
            ydl_opts = self.ydl_opts_base.copy()
            ydl_opts["listformats"] = True
            ydl_opts["quiet"] = True

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = info.get("formats", [])
            logger.debug(f"Available formats: {len(formats)}")

            if not formats:
                return "best"  # Fallback to default

            # Filter out formats without URLs (the problematic ones)
            valid_formats = [f for f in formats if f.get("url")]
            logger.debug(f"Valid formats with URLs: {len(valid_formats)}")

            if not valid_formats:
                # If no valid formats, try the original best option
                return "best"

            if download_video:
                # For video, prefer formats that have both video and audio
                combined_formats = [
                    f
                    for f in valid_formats
                    if f.get("vcodec") != "none" and f.get("acodec") != "none"
                ]
                if combined_formats:
                    # Get the best combined format
                    return combined_formats[-1]["format_id"]

                # Fallback: get best video and best audio separately
                video_formats = [f for f in valid_formats if f.get("vcodec") != "none"]
                audio_formats = [f for f in valid_formats if f.get("acodec") != "none"]

                if video_formats and audio_formats:
                    # Use a format selection that combines best video + best audio
                    return f"{video_formats[-1]['format_id']}+{audio_formats[-1]['format_id']}"
                elif video_formats:
                    return video_formats[-1]["format_id"]
                else:
                    return "best"
            else:
                # For audio only
                audio_formats = [f for f in valid_formats if f.get("acodec") != "none"]
                if audio_formats:
                    return audio_formats[-1]["format_id"]
                else:
                    return "bestaudio/best"

        except Exception as e:
            logger.warning(f"Could not determine safe format, using default: {e}")
            return "best" if download_video else "bestaudio/best"

    def download_song(
        self, query: str, download_video: bool = False, quality: str = "best"
    ) -> bool:
        """Download song/video from YouTube with robust error handling"""
        try:
            # Clean query for filename safety
            safe_query = self._clean_filename(query)
            search_query = f"ytsearch:{query}"

            ydl_opts = self.ydl_opts_base.copy()
            ydl_opts["outtmpl"] = f"./{safe_query}.%(ext)s"

            # Create downloads directory
            # os.makedirs("downloads", exist_ok=True)

            # Use adaptive format selection that checks availability
            if download_video:
                # For video downloads, use a more conservative approach
                ydl_opts["format"] = self._get_video_format_safe(quality)
                logger.debug(f"Using video format: {ydl_opts['format']}")
            else:
                # For audio, use reliable audio extraction
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ]
                logger.debug("Using audio extraction with MP3 conversion")

            logger.info(f"Downloading: \033[1;94m{query}\033[0m")

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    # First, try the preferred method
                    ydl.download([search_query])
                    logger.info("Download completed successfully!")
                    return True

                except youtube_dl.utils.DownloadError as e:
                    if "Requested format is not available" in str(e):
                        logger.warning(
                            "Preferred format not available, trying fallback..."
                        )
                        return self._download_with_adaptive_format(
                            ydl, search_query, download_video
                        )
                    else:
                        logger.error(f"Download error: {e}")
                        return False
                except Exception as e:
                    logger.error(f"Unexpected download error: {e}")
                    return False

        except Exception as e:
            logger.error(f"Download setup failed: {e}")
            return False

    def _get_video_format_safe(self, quality: str) -> str:
        """Get safe video format preferences that work around YouTube restrictions"""
        # Use format combinations that are more likely to work
        format_preferences = {
            "best": "best[height<=1080]",  # Limit to 1080p to avoid problematic 4K formats
            "high": "best[height<=1080]",
            "medium": "best[height<=720]",
            "low": "best[height<=480]",
        }
        return format_preferences.get(quality, "best[height<=1080]")

    def _download_with_adaptive_format(
        self, ydl: youtube_dl.YoutubeDL, search_query: str, download_video: bool
    ) -> bool:
        """Try multiple format strategies until one works"""
        format_strategies = []

        if download_video:
            format_strategies = [
                "best[height<=1080]",  # Limited resolution
                "best[height<=720]",  # Lower resolution
                "bestvideo[height<=1080]+bestaudio/best",  # Combined
                "bestvideo[height<=720]+bestaudio/best",
                "best",  # Ultimate fallback
            ]
        else:
            format_strategies = [
                "bestaudio/best",
                "worstaudio/worst",  # Sometimes smaller files work
                "best",  # General fallback
            ]

        for i, format_strat in enumerate(format_strategies):
            try:
                logger.info(
                    f"Trying format strategy {i + 1}/{len(format_strategies)}: {format_strat}"
                )
                ydl.params["format"] = format_strat

                # Remove postprocessors for video downloads in fallback
                if download_video and "postprocessors" in ydl.params:
                    del ydl.params["postprocessors"]

                ydl.download([search_query])
                logger.info(f"Success with format: {format_strat}")
                return True

            except Exception as e:
                logger.debug(f"Format {format_strat} failed: {e}")
                continue

        logger.error("All format strategies failed")
        return False

    def _clean_filename(self, filename: str) -> str:
        """Clean filename to be filesystem-safe"""
        # Remove or replace problematic characters
        cleaned = re.sub(r'[<>:"/\\|?*]', "", filename)
        # Remove emojis and other non-ASCII characters that might cause issues
        cleaned = re.sub(r"[^\x00-\x7F]+", "", cleaned)
        # Limit length
        return cleaned.strip()[:100]
