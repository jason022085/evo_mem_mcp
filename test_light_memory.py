"""Test script for LightMemory dual-track mechanism.
"""

import unittest
from unittest.mock import MagicMock
from datetime import datetime

from evo_memory.memory.base import MemoryEntry
from evo_memory.memory.light_memory import LightMemory
from evo_memory.llm.base import BaseLLM, LLMResponse

class MockLLM(BaseLLM):
    def __init__(self):
        super().__init__(model_name="mock-model")

    def _generate(self, messages, **kwargs):
        return LLMResponse(
            content="""Summary: Successfully learned to navigate a kitchen.
Input Template: Navigation tasks in indoor environments.
Best Practice: Always check for obstacles before moving.
Caveats: Resolved conflict between 'run' and 'walk' speed; 'walk' is safer.""",
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 50}
        )

class TestLightMemory(unittest.TestCase):
    def setUp(self):
        self.memory = LightMemory()
        self.llm = MockLLM()

    def test_online_update(self):
        """Test that adding entries works and they go to the unconsolidated buffer."""
        entry = MemoryEntry(
            task_id="task1",
            input_text="Move to the fridge",
            output_text="Action: move north",
            is_successful=True
        )
        self.memory.add(entry)
        
        self.assertEqual(len(self.memory), 1)
        self.assertEqual(self.memory.get_unconsolidated_count(), 1)
        self.assertEqual(len(self.memory.consolidated_entries), 0)

    def test_offline_consolidation(self):
        """Test the consolidation process."""
        # Add multiple similar entries
        for i in range(3):
            entry = MemoryEntry(
                task_id=f"task_{i}",
                input_text=f"Move to target {i}",
                output_text=f"Action: move {i}",
                is_successful=True
            )
            self.memory.add(entry)

        self.assertEqual(self.memory.get_unconsolidated_count(), 3)
        
        # Trigger consolidation
        # In our implementation, batches of 5 are merged. 
        # Since we have 3, they will be merged into 1 (if we modify the grouping or just let it merge all)
        # Wait, the current _group_entries batches by 5. So 3 will be in one batch.
        
        result = self.memory.consolidate(self.llm)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.memory.get_unconsolidated_count(), 0)
        
        # Should have 1 merged entry
        self.assertEqual(len(self.memory.consolidated_entries), 1)
        merged_entry = self.memory.consolidated_entries[0]
        self.assertTrue(merged_entry.task_id.startswith("merged_"))
        self.assertIn("Navigation tasks", merged_entry.input_text)
        self.assertIn("Summary: Successfully learned", merged_entry.feedback)

if __name__ == "__main__":
    unittest.main()
