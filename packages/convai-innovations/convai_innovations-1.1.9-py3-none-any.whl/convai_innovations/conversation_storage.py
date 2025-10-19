"""
Conversation Storage Manager for ConvAI Innovations
Saves and loads conversation history locally for progress tracking.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib


class ConversationEntry:
    """Represents a single conversation entry"""

    def __init__(self, session_id: str, user_input: str, ai_response: str = "",
                 code_snippet: str = "", timestamp: Optional[str] = None):
        self.session_id = session_id
        self.user_input = user_input
        self.ai_response = ai_response
        self.code_snippet = code_snippet
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'code_snippet': self.code_snippet,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationEntry':
        """Create from dictionary"""
        return cls(
            session_id=data.get('session_id', ''),
            user_input=data.get('user_input', ''),
            ai_response=data.get('ai_response', ''),
            code_snippet=data.get('code_snippet', ''),
            timestamp=data.get('timestamp')
        )


class ConversationStorage:
    """Manages local storage of conversation history"""

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize conversation storage

        Args:
            storage_dir: Directory to store conversation history.
                        Defaults to ~/.convai/conversations
        """
        if storage_dir is None:
            # Use user's home directory
            home = Path.home()
            storage_dir = home / '.convai' / 'conversations'

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Create sessions index file
        self.index_file = self.storage_dir / 'sessions_index.json'
        self._ensure_index_file()

    def _ensure_index_file(self):
        """Ensure the sessions index file exists"""
        if not self.index_file.exists():
            self._save_index({})

    def _load_index(self) -> Dict:
        """Load the sessions index"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_index(self, index: Dict):
        """Save the sessions index"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving index: {e}")

    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a specific learning session"""
        # Sanitize session_id for filename
        safe_id = "".join(c if c.isalnum() or c in '_-' else '_' for c in session_id)
        return self.storage_dir / f"{safe_id}.json"

    def save_conversation(self, entry: ConversationEntry):
        """
        Save a conversation entry

        Args:
            entry: ConversationEntry to save
        """
        session_file = self._get_session_file(entry.session_id)

        # Load existing conversations for this session
        conversations = []
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversations = data.get('conversations', [])
            except Exception:
                conversations = []

        # Add new entry
        conversations.append(entry.to_dict())

        # Save back
        session_data = {
            'session_id': entry.session_id,
            'last_updated': datetime.now().isoformat(),
            'conversation_count': len(conversations),
            'conversations': conversations
        }

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # Update index
            self._update_index(entry.session_id, session_data)
        except Exception as e:
            print(f"Error saving conversation: {e}")

    def _update_index(self, session_id: str, session_data: Dict):
        """Update the sessions index with session info"""
        index = self._load_index()
        index[session_id] = {
            'last_updated': session_data['last_updated'],
            'conversation_count': session_data['conversation_count']
        }
        self._save_index(index)

    def load_session_history(self, session_id: str) -> List[ConversationEntry]:
        """
        Load conversation history for a specific session

        Args:
            session_id: ID of the learning session

        Returns:
            List of ConversationEntry objects
        """
        session_file = self._get_session_file(session_id)

        if not session_file.exists():
            return []

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conversations = data.get('conversations', [])
                return [ConversationEntry.from_dict(conv) for conv in conversations]
        except Exception as e:
            print(f"Error loading session history: {e}")
            return []

    def get_all_sessions(self) -> Dict[str, Dict]:
        """
        Get summary of all sessions

        Returns:
            Dictionary mapping session_id to session metadata
        """
        return self._load_index()

    def clear_session(self, session_id: str):
        """
        Clear conversation history for a specific session

        Args:
            session_id: ID of the session to clear
        """
        session_file = self._get_session_file(session_id)

        if session_file.exists():
            try:
                session_file.unlink()

                # Update index
                index = self._load_index()
                if session_id in index:
                    del index[session_id]
                    self._save_index(index)
            except Exception as e:
                print(f"Error clearing session: {e}")

    def export_session(self, session_id: str, output_file: str):
        """
        Export a session's conversation history to a file

        Args:
            session_id: ID of the session to export
            output_file: Path to save the exported data
        """
        history = self.load_session_history(session_id)

        export_data = {
            'session_id': session_id,
            'exported_at': datetime.now().isoformat(),
            'total_conversations': len(history),
            'conversations': [entry.to_dict() for entry in history]
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error exporting session: {e}")

    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get statistics for a session

        Args:
            session_id: ID of the session

        Returns:
            Dictionary containing session statistics
        """
        history = self.load_session_history(session_id)

        if not history:
            return {
                'total_entries': 0,
                'code_snippets': 0,
                'first_interaction': None,
                'last_interaction': None
            }

        code_count = sum(1 for entry in history if entry.code_snippet)

        return {
            'total_entries': len(history),
            'code_snippets': code_count,
            'first_interaction': history[0].timestamp if history else None,
            'last_interaction': history[-1].timestamp if history else None
        }


# Global instance for easy access
_storage_instance = None


def get_storage(storage_dir: Optional[str] = None) -> ConversationStorage:
    """
    Get or create the global conversation storage instance

    Args:
        storage_dir: Optional custom storage directory

    Returns:
        ConversationStorage instance
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ConversationStorage(storage_dir)
    return _storage_instance
