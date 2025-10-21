import sounddevice as sd
import wavio
from pathlib import Path
from ..utils.logging_util import logger


class AudioProcessor:
    """Handles audio processing operations"""

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Get audio duration in seconds"""
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(file_path)
            duration = audio.duration_seconds
            logger.info(f"Audio duration: {duration:.2f} seconds")
            return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            raise

    @staticmethod
    def trim_audio(file_path: str, start_min: float = 0, end_min: float = 0.25) -> str:
        """Trim audio file to specified segment"""
        try:
            from pydub import AudioSegment

            logger.debug("Trimming audio to 15 seconds")
            audio = AudioSegment.from_file(file_path)

            start_ms = int(start_min * 60 * 1000)
            end_ms = int(end_min * 60 * 1000)

            # Ensure we don't exceed audio length
            end_ms = min(end_ms, len(audio))

            trimmed_audio = audio[start_ms:end_ms]

            # Create output filename
            file_ext = Path(file_path).suffix
            output_path = f"{Path(file_path).stem}_trimmed{file_ext}"

            trimmed_audio.export(output_path, format=file_ext[1:])
            logger.info(f"Trimmed audio saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error trimming audio: {e}")
            raise

    @staticmethod
    def record_audio(
        file_path: str, duration: int = 10, sample_rate: int = 44100
    ) -> None:
        """Record audio from microphone"""
        try:
            logger.info(f"Recording {duration} seconds of audio...")
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=2,
                dtype="int16",
            )
            sd.wait()
            wavio.write(file_path, recording, sample_rate, sampwidth=2)
            logger.info(f"Recording saved to: {file_path}")
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise
