import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ..utils.logging_util import logger


class SearchHistory:
    """Manages search history"""

    def __init__(self, history_file: str = "search_history.json"):
        self.history_file = Path().home() / ".musicrecon" / history_file
        # Ensure directory exists
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_history_file()

    def _ensure_history_file(self) -> None:
        """Ensure history file exists"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, "w") as f:
                json.dump([], f, indent=2)

    def save_search(self, song_info: Dict[str, Any]) -> bool:
        """Save search result to history"""
        try:
            timestamp = datetime.now().isoformat()
            entry = {"timestamp": timestamp, "song_info": song_info}

            with open(self.history_file, "r+") as f:
                history = json.load(f)
                history.append(entry)
                f.seek(0)
                json.dump(history, f, indent=2)
                f.truncate()

            logger.debug("Search saved to history")
            return True

        except Exception as e:
            logger.error(f"Failed to save search: {e}")
            return False

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent search history"""
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
            return history[-limit:]
        except Exception as e:
            logger.error(f"Failed to read history: {e}")
            return []
