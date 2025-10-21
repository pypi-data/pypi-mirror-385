#!/usr/bin/python3
import argparse
import sys
from ..utils.logging_util import logger, logging
from ..core.recognizer import MusicRecognizer


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Song Recognition Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --record                    # Record and identify song
  %(prog)s --search song.wav           # Identify from audio file
  %(prog)s --search song.wav --download # Identify and download
  %(prog)s --download "Song Name Artist" # Download specific song
  %(prog)s --history                   # Show search history
        """,
    )

    parser.add_argument(
        "--search", "-s", type=str, help="Path to audio file for recognition"
    )
    parser.add_argument(
        "--record", "-r", action="store_true", help="Record audio for recognition"
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=10,
        help="Recording duration in seconds (default: 10)",
    )
    parser.add_argument(
        "--download",
        "-D",
        nargs="?",
        const=True,
        default=False,
        help="Download song. Use without value to download identified song, or provide song name to download specific song",
    )
    parser.add_argument(
        "--video", "-v", action="store_true", help="Download video instead of audio"
    )
    parser.add_argument(
        "--quality",
        "-q",
        choices=["best", "high", "medium", "low"],
        default="best",
        help="Video quality preference",
    )
    parser.add_argument(
        "--history", "-H", action="store_true", help="Show search history"
    )
    parser.add_argument(
        "--verbose", "-V", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    app = MusicRecognizer()

    try:
        if args.history:
            app.show_history()
        elif isinstance(args.download, str):
            # Direct download of specified song
            return app.download_song(
                query=args.download, download_video=args.video, quality=args.quality
            )
        elif args.record:
            app.recognize_from_recording(
                duration=args.duration,
                download=bool(args.download),
                download_video=args.video,
                # quality=args.quality,
            )
        elif args.search:
            app.recognize_from_file(
                file_path=args.search,
                download=bool(args.download),
                download_video=args.video,
                # quality=args.quality,
            )
        elif args.download is True:
            # --download used without search/record
            logger.error(
                "--download requires either --search, --record, or a song name"
            )
            parser.print_help()
            sys.exit(1)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
