"""LightMem-inspired dual-track memory implementation.

This module implements the dual-stage memory update mechanism:
1. Online Stage: Lightweight soft updates for real-time response.
2. Offline Stage: Sleep-time reflective consolidation for memory maintenance.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from .base import Memory, MemoryEntry
from ..llm import BaseLLM

logger = logging.getLogger(__name__)

class LightMemory(Memory):
    """
    LightMemory implements a dual-track memory system.
    
    It maintains a buffer of 'unconsolidated' recent experiences and
    a store of 'consolidated' long-term knowledge.
    """

    def __init__(
        self,
        max_size: int = 1000,
        buffer_threshold: int = 10,
        **kwargs
    ):
        super().__init__(max_size=max_size, **kwargs)
        self.buffer_threshold = buffer_threshold
        self.unconsolidated_entries: List[MemoryEntry] = []
        self.consolidated_entries: List[MemoryEntry] = []

    def add(self, entry: MemoryEntry) -> bool:
        """
        Online Phase: Soft update.
        Simply adds the entry to the unconsolidated buffer.
        """
        # Call base add to keep everything in the main entry list for backward compatibility
        # and simple retrieval.
        success = super().add(entry)
        if success:
            self.unconsolidated_entries.append(entry)
        return success

    def get_unconsolidated_count(self) -> int:
        """Get the number of entries waiting for consolidation."""
        return len(self.unconsolidated_entries)

    def consolidate(self, llm: BaseLLM) -> Dict[str, Any]:
        """
        Offline Phase: Sleep-time updates / Reflective consolidation.
        
        This process:
        1. Groups recent experiences.
        2. Uses LLM to reflect and merge them.
        3. Resolves logic conflicts.
        4. Updates the long-term memory store.
        """
        if not self.unconsolidated_entries:
            return {"status": "skipped", "message": "No unconsolidated entries."}

        logger.info(f"Starting memory consolidation for {len(self.unconsolidated_entries)} entries.")
        
        # 1. Selection & Grouping (Simple heuristic: by similarity or domain)
        # For now, we process them in batches.
        batches = self._group_entries(self.unconsolidated_entries)
        
        new_consolidated_count = 0
        merged_count = 0
        
        for batch in batches:
            if len(batch) == 1:
                # Single entry, just mark as consolidated
                self.consolidated_entries.append(batch[0])
                new_consolidated_count += 1
                continue
                
            # 2. Reflection & Consolidation
            merged_entry = self._reflect_and_merge(llm, batch)
            if merged_entry:
                # Remove original entries from the main memory to replace with merged one
                for entry in batch:
                    self.remove(entry.task_id)
                
                # Add the new merged entry
                self.add_consolidated(merged_entry)
                merged_count += 1
            else:
                # If merging fails, just keep them as they are but mark consolidated
                self.consolidated_entries.extend(batch)
                new_consolidated_count += len(batch)

        # Clear the buffer
        self.unconsolidated_entries.clear()
        
        return {
            "status": "success",
            "processed": len(self.unconsolidated_entries),
            "merged": merged_count,
            "new_consolidated": new_consolidated_count,
        }

    def add_consolidated(self, entry: MemoryEntry) -> bool:
        """Add a consolidated entry to memory."""
        # Bypass the unconsolidated buffer
        success = super().add(entry)
        if success:
            self.consolidated_entries.append(entry)
            # Ensure it doesn't end up in unconsolidated if added via this method
            if entry in self.unconsolidated_entries:
                self.unconsolidated_entries.remove(entry)
        return success

    def _group_entries(self, entries: List[MemoryEntry]) -> List[List[MemoryEntry]]:
        """
        Group entries for consolidation.
        Heuristic: Group by input similarity or metadata (e.g., domain).
        """
        # Simple implementation: group by task similarity or just batch by 5
        # In a real implementation, we'd use embedding clustering.
        batch_size = 5
        return [entries[i:i + batch_size] for i in range(0, len(entries), batch_size)]

    def _reflect_and_merge(self, llm: BaseLLM, entries: List[MemoryEntry]) -> Optional[MemoryEntry]:
        """Use LLM to reflect on multiple entries and merge them into one."""
        experiences_text = "\n\n".join([
            f"Experience {i+1}:\n{e.to_text()}" 
            for i, e in enumerate(entries)
        ])
        
        prompt = f"""You are a memory consolidation module. Below are several recent experiences.
Your task is to:
1. Identify common patterns, successful strategies, and recurring mistakes.
2. Resolve any logical conflicts between these experiences.
3. Synthesize them into a single, high-quality "Consolidated Memory Entry" that captures the essence of what was learned.

Recent Experiences:
{experiences_text}

Provide the consolidated entry in the following format:
Summary: <A concise summary of the learned knowledge>
Input Template: <A generalized description of the task type>
Best Practice: <The most effective approach identified>
Caveats: <Conflicts resolved or things to avoid>
"""

        try:
            response = llm.generate(prompt=prompt)
            content = response.content
            
            # Parse the response and create a new MemoryEntry
            # This is a simplified parsing logic
            summary = self._extract_field(content, "Summary")
            input_template = self._extract_field(content, "Input Template")
            best_practice = self._extract_field(content, "Best Practice")
            caveats = self._extract_field(content, "Caveats")
            
            merged_entry = MemoryEntry(
                task_id=f"merged_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                input_text=input_template or "Consolidated Knowledge",
                output_text=best_practice or "No specific practice identified.",
                feedback=f"Summary: {summary}\nCaveats: {caveats}",
                metadata={
                    "type": "consolidated",
                    "original_task_ids": [e.task_id for e in entries],
                    "consolidation_time": datetime.now().isoformat()
                },
                is_successful=True # Consolidated knowledge is assumed to be useful
            )
            return merged_entry
        except Exception as e:
            logger.error(f"Failed to merge entries: {e}")
            return None

    def _extract_field(self, text: str, field_name: str) -> str:
        """Helper to extract fields from LLM response."""
        import re
        pattern = rf"{field_name}:\s*(.*?)(?=\n[A-Z][a-z]+:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
