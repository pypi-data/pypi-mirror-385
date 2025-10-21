import json
from typing import List

from .base import LogHandler
from ..client.models import LogEntry


class ConsoleHandler(LogHandler):
    """Handler for console output"""

    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to console"""
        try:
            for entry in entries:
                if self.config.format == "json":
                    if self.config.pretty_print:
                        # Pretty print JSON for development
                        print(json.dumps(entry.to_dict(), indent=2, default=str))
                        print("-" * 80)  # Separator for readability
                    else:
                        print(entry.to_json())
                else:
                    print(
                        f"[{entry.timestamp}] {entry.level.value} {entry.logger}: {entry.message}"
                    )
            return True
        except Exception as e:
            print(f"Error writing to console: {e}")
            return False

    async def flush(self) -> bool:
        """Console output doesn't need flushing"""
        return True
