"""
Tests for Pitwall memory management functionality.
"""

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

from pitwall.memory import ConversationMemory


class TestConversationMemory:
    """Test conversation memory functionality."""

    def setup_method(self):
        """Set up test with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = ConversationMemory(memory_dir=Path(self.temp_dir))

    def test_create_session(self):
        """Test creating a new session."""
        session_id = self.memory.create_session("test-model")

        assert session_id is not None
        assert self.memory.has_active_session()
        assert self.memory.current_session_id == session_id

        # Check that session files are created
        session_file = self.memory._get_session_file(session_id)
        metadata_file = self.memory._get_session_metadata_file(session_id)

        assert session_file.exists()
        assert metadata_file.exists()

    def test_session_metadata(self):
        """Test session metadata is stored correctly."""
        test_metadata = {"test_key": "test_value"}
        session_id = self.memory.create_session("test-model", metadata=test_metadata)

        summary = self.memory.get_session_summary()

        assert summary is not None
        assert summary["session_id"] == session_id
        assert summary["model"] == "test-model"
        assert summary["metadata"]["test_key"] == "test_value"
        assert "created_at" in summary
        assert "updated_at" in summary

    def test_load_session(self):
        """Test loading an existing session."""
        # Create and save a session
        session_id = self.memory.create_session("test-model")
        original_id = self.memory.current_session_id

        # Clear memory and load the session
        self.memory.clear_session()
        assert not self.memory.has_active_session()

        # Load the session
        loaded = self.memory.load_session(session_id)

        assert loaded is True
        assert self.memory.has_active_session()
        assert self.memory.current_session_id == original_id

    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        loaded = self.memory.load_session("nonexistent-id")
        assert loaded is False
        assert not self.memory.has_active_session()

    def test_list_sessions(self):
        """Test listing all sessions."""
        # Start with no sessions
        sessions = self.memory.list_sessions()
        assert len(sessions) == 0

        # Create a few sessions
        session1 = self.memory.create_session("model1", metadata={"name": "test1"})
        session2 = self.memory.create_session("model2", metadata={"name": "test2"})

        sessions = self.memory.list_sessions()
        assert len(sessions) == 2

        # Should be sorted by updated_at descending (newest first)
        assert sessions[0]["session_id"] == session2  # Most recent
        assert sessions[1]["session_id"] == session1

    def test_delete_session(self):
        """Test deleting a session."""
        session_id = self.memory.create_session("test-model")

        # Verify session exists
        assert self.memory.has_active_session()
        sessions = self.memory.list_sessions()
        assert len(sessions) == 1

        # Delete the session
        deleted = self.memory.delete_session(session_id)

        assert deleted is True
        assert not self.memory.has_active_session()

        sessions = self.memory.list_sessions()
        assert len(sessions) == 0

    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        deleted = self.memory.delete_session("nonexistent-id")
        assert deleted is False

    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        # Create multiple sessions
        self.memory.create_session("model1")
        self.memory.create_session("model2")
        self.memory.create_session("model3")

        sessions = self.memory.list_sessions()
        assert len(sessions) == 3

        # Clear all sessions
        self.memory.clear_all_sessions()

        sessions = self.memory.list_sessions()
        assert len(sessions) == 0
        assert not self.memory.has_active_session()

    def test_export_session(self):
        """Test exporting a session."""
        session_id = self.memory.create_session("test-model", metadata={"test": "data"})

        # Export to temporary file
        export_path = Path(self.temp_dir) / "export.json"
        exported = self.memory.export_session(session_id, export_path)

        assert exported is True
        assert export_path.exists()

        # Verify export content
        with open(export_path, "r") as f:
            export_data = json.load(f)

        assert "metadata" in export_data
        assert "messages" in export_data
        assert export_data["metadata"]["session_id"] == session_id
        assert export_data["metadata"]["model"] == "test-model"

    def test_export_nonexistent_session(self):
        """Test exporting a session that doesn't exist."""
        export_path = Path(self.temp_dir) / "export.json"
        exported = self.memory.export_session("nonexistent-id", export_path)

        assert exported is False
        assert not export_path.exists()

    def test_get_context_summary(self):
        """Test getting conversation context summary."""
        self.memory.create_session("test-model")

        # Test with no messages
        summary = self.memory.get_context_summary()
        assert "No conversation history" in summary

        # Add some mock messages (this would normally come from PydanticAI)
        # For testing, we'll create simple mock objects with the required attributes
        class MockUserMessage:
            role = "user"
            content = "Hello"

        class MockAssistantMessage:
            role = "assistant"
            content = "Hi there!"

        self.memory.current_messages = [MockUserMessage(), MockAssistantMessage()]

        summary = self.memory.get_context_summary()
        assert "Last 2 messages" in summary
        assert "Human: Hello" in summary
        assert "Assistant: Hi there!" in summary

    def test_load_session_with_corrupted_json(self, caplog):
        """Test loading a session with corrupted JSON file."""
        # Create a valid session first
        session_id = self.memory.create_session("test-model")
        session_file = self.memory._get_session_file(session_id)

        # Corrupt the session file with invalid JSON
        with open(session_file, "w") as f:
            f.write("{ invalid json content }")

        # Attempt to load the corrupted session
        with caplog.at_level(logging.ERROR):
            loaded = self.memory.load_session(session_id)

        # Should return False
        assert loaded is False

        # Should log an error about JSON parsing
        assert any(
            "Failed to parse session file" in record.message
            for record in caplog.records
        )
        assert any("corrupted" in record.message for record in caplog.records)

    def test_load_session_with_invalid_datetime(self, caplog):
        """Test loading a session with invalid datetime in message data."""
        # Create a valid session first
        session_id = self.memory.create_session("test-model")
        session_file = self.memory._get_session_file(session_id)

        # Create message data with invalid datetime format
        # This simulates what might happen if Multiviewer returns malformed data
        invalid_message_data = [
            {
                "kind": "request",
                "parts": [{"content": "test"}],
                "timestamp": "not-a-valid-datetime-format",  # Invalid datetime
            }
        ]

        with open(session_file, "w") as f:
            json.dump(invalid_message_data, f)

        # Attempt to load the session with invalid datetime
        with caplog.at_level(logging.ERROR):
            loaded = self.memory.load_session(session_id)

        # Should return False
        assert loaded is False

        # Should log a ValidationError with helpful context
        assert any(
            "Failed to validate messages" in record.message for record in caplog.records
        )
        assert any("MultiViewer" in record.message for record in caplog.records)
        assert any("datetime" in record.message for record in caplog.records)

    def test_load_session_with_file_permission_error(self, caplog):
        """Test loading a session when file read fails unexpectedly."""
        # Create a valid session
        session_id = self.memory.create_session("test-model")

        # Mock the open() call to raise a permission error
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with caplog.at_level(logging.ERROR):
                loaded = self.memory.load_session(session_id)

        # Should return False
        assert loaded is False

        # Should log an unexpected error
        assert any(
            "Unexpected error loading session" in record.message
            for record in caplog.records
        )

    def test_update_metadata_with_corrupted_file(self, caplog):
        """Test updating metadata when metadata file is corrupted."""
        # Create a session
        session_id = self.memory.create_session("test-model")
        self.memory.current_session_id = session_id

        # Corrupt the metadata file
        metadata_file = self.memory._get_session_metadata_file(session_id)
        with open(metadata_file, "w") as f:
            f.write("{ invalid json }")

        # Try to update metadata
        with caplog.at_level(logging.WARNING):
            self.memory._update_session_metadata()

        # Should log a warning
        assert any(
            "Could not update metadata" in record.message for record in caplog.records
        )
        assert any(
            "Failed to parse metadata file" in record.message
            for record in caplog.records
        )

    def test_get_session_summary_with_corrupted_metadata(self, caplog):
        """Test getting session summary when metadata is corrupted."""
        # Create a session
        session_id = self.memory.create_session("test-model")

        # Corrupt the metadata file
        metadata_file = self.memory._get_session_metadata_file(session_id)
        with open(metadata_file, "w") as f:
            f.write("{ not valid json }")

        # Try to get summary
        with caplog.at_level(logging.WARNING):
            summary = self.memory.get_session_summary()

        # Should return None
        assert summary is None

        # Should log a warning
        assert any(
            "Could not read session summary" in record.message
            for record in caplog.records
        )

    def test_list_sessions_with_mixed_valid_and_corrupted(self, caplog):
        """Test listing sessions when some metadata files are corrupted."""
        # Create two valid sessions
        session1 = self.memory.create_session("model1")
        session2 = self.memory.create_session("model2")

        # Corrupt the first session's metadata
        metadata_file1 = self.memory._get_session_metadata_file(session1)
        with open(metadata_file1, "w") as f:
            f.write("{ corrupt }")

        # List sessions (should skip corrupted one)
        with caplog.at_level(logging.DEBUG):
            sessions = self.memory.list_sessions()

        # Should only return the valid session
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == session2

        # Should log debug message about corrupted file
        assert any(
            "Skipping corrupted metadata file" in record.message
            for record in caplog.records
        )

    def test_export_session_with_io_error(self, caplog):
        """Test exporting a session when file I/O fails."""
        # Create a session
        session_id = self.memory.create_session("test-model")

        # Try to export to a read-only location (simulate I/O error)
        export_path = Path("/nonexistent/directory/export.json")

        with caplog.at_level(logging.ERROR):
            result = self.memory.export_session(session_id, export_path)

        # Should return False
        assert result is False

        # Should log an error
        assert any(
            "Failed to export session" in record.message for record in caplog.records
        )
