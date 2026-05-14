"""Sleep-time update manager for LightMemory.

Manages the background or scheduled consolidation of memory entries.
"""

import time
import threading
import logging
from typing import Optional, Dict, Any

from .light_memory import LightMemory
from ..llm import BaseLLM

logger = logging.getLogger(__name__)

class SleepManager:
    """
    SleepManager handles the offline consolidation phase of LightMemory.
    
    It can run as a background thread or be triggered manually.
    """

    def __init__(
        self,
        memory: LightMemory,
        llm: BaseLLM,
        check_interval: int = 60,
        min_entries_for_consolidation: int = 5,
    ):
        self.memory = memory
        self.llm = llm
        self.check_interval = check_interval
        self.min_entries_for_consolidation = min_entries_for_consolidation
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start_background(self):
        """Start the background consolidation thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("SleepManager background thread is already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("SleepManager background thread started.")

    def stop_background(self):
        """Stop the background consolidation thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("SleepManager background thread stopped.")

    def trigger_consolidation(self) -> Dict[str, Any]:
        """Manually trigger consolidation."""
        logger.info("Manually triggering memory consolidation.")
        return self.memory.consolidate(self.llm)

    def _run_loop(self):
        """Main loop for background consolidation."""
        while not self._stop_event.is_set():
            try:
                unconsolidated_count = self.memory.get_unconsolidated_count()
                if unconsolidated_count >= self.min_entries_for_consolidation:
                    logger.info(f"Background consolidation triggered: {unconsolidated_count} entries.")
                    self.memory.consolidate(self.llm)
                
                # Sleep and check periodically
                # Using wait on event for cleaner shutdown
                self._stop_event.wait(self.check_interval)
            except Exception as e:
                logger.error(f"Error in SleepManager background loop: {e}")
                time.sleep(10) # Wait a bit before retrying
