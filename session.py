# session.py
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """A message in a conversation."""
    role: str
    content: str
    timestamp: str
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"],
            tool_calls=data.get("tool_calls"),
            tool_results=data.get("tool_results")
        )


class Session:
    """Manages a conversation session."""

    def __init__(self, session_id: str, messages: List[Message] = None):
        self.session_id = session_id
        self.messages = messages or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def add_message(self, message: Message) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.to_dict() for m in self.messages]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        session = cls(data["session_id"], messages)
        session.created_at = data.get("created_at", datetime.now().isoformat())
        session.updated_at = data.get("updated_at", datetime.now().isoformat())
        return session


class SessionManager:
    """Manages all sessions with JSONL storage."""

    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = session_dir
        os.makedirs(session_dir, exist_ok=True)

    def _get_session_path(self, session_id: str) -> str:
        return os.path.join(self.session_dir, f"{session_id}.jsonl")

    def create_session(self) -> Session:
        """Create a new session."""
        session_id = str(uuid.uuid4())[:8]
        session = Session(session_id)
        self.save_session(session)
        return session

    def save_session(self, session: Session) -> None:
        """Save session to JSONL file."""
        path = self._get_session_path(session.session_id)
        with open(path, "w", encoding="utf-8") as f:
            for msg in session.messages:
                f.write(json.dumps(msg.to_dict(), ensure_ascii=False) + "\n")

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from JSONL file."""
        path = self._get_session_path(session_id)
        if not os.path.exists(path):
            return None
        messages = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    messages.append(Message.from_dict(json.loads(line)))
        session = Session(session_id, messages)
        return session

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with metadata."""
        sessions = []
        for filename in os.listdir(self.session_dir):
            if filename.endswith(".jsonl"):
                session_id = filename[:-6]
                path = os.path.join(self.session_dir, filename)
                stat = os.stat(path)
                session = self.load_session(session_id)
                sessions.append({
                    "session_id": session_id,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                    "message_count": len(session.messages),
                    "size_bytes": stat.st_size
                })
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        path = self._get_session_path(session_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    def add_message_to_session(self, session_id: str, message: Message) -> None:
        """Append a message to a session file."""
        path = self._get_session_path(session_id)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(message.to_dict(), ensure_ascii=False) + "\n")
