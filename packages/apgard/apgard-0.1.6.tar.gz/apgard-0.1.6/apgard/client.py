import requests
from typing import Optional, Dict
from dotenv import load_dotenv
from dataclasses import dataclass
from uuid import UUID
import json
load_dotenv()


@dataclass
class BreakStatus:
    break_due: bool
    message: Optional[str] = None
    # thread_id: Optional[str] = None


class BreakTracker:
    """Take-a-break feature: handles break tracking and session management."""

    def __init__(self, client, break_time_minutes: int = 180):
        self.client = client
        self.break_time_minutes = break_time_minutes

    def activity(
        self,
        user_id: str,
        # thread_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> BreakStatus:
        """
        Records user activity and returns break status.
        """
        payload = {
            "user_id": user_id,
            "break_time_minutes": self.break_time_minutes,
            "metadata": metadata or None
        }
        # if thread_id:
        #     payload["thread_id"] = thread_id
        
        try:
            resp = self.client.session.post(f"{self.client.base_url}/api/sessions/activity", json=payload)
            resp.raise_for_status()
            data = resp.json()
            break_due = bool(data.get("break_due", False))
            message = str(data.get("message", "Time to take a break! Reminder: this chatbot is AI-generated, not human."))

            return BreakStatus(
                break_due=break_due,
                message=message,
                # thread_id=data.get("thread_id", thread_id)
            )

        except Exception as e:
            print(f"Warning: Failed to fetch break status: {e}")
            return BreakStatus(
                break_due=False,
                message="Time to take a break! Reminder: this chatbot is AI-generated, not human.",
                # thread_id=thread_id
            )


class ContentTracker:
    """Content tracking feature: logs conversation messages for moderation, analytics, or AI evaluation."""

    def __init__(self, client):
        self.client = client

    def record_message(
        self,
        user_id: str,
        content: str,
        role: str = "user",  # 'user' or 'model'
        content_type: str = "text",
        thread_id: Optional[str] = None, # client-provided external thread
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Record a single message in a conversation.

        Args:
            user_id: ID of the end user
            content: The message text
            role: 'user' for user input, 'model' for AI output
            content_type: Type of content ('text', 'image', 'video', etc.)
            thread_id: Optional client-provided external thread ID
            metadata: Optional additional data

        Returns:
            dict: Server response including status, errors, and thread/session info
        """
        if role not in ("user", "model"):
            raise ValueError("role must be 'user' or 'model'")
        # validate metadata is valid json

        if content_type not in ("text"):
            # 'image', 'video', 'audio'
            raise ValueError("content_type must be one of: 'text'")

        # --- Validate metadata is valid JSON ---
        if metadata is not None:
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    raise ValueError("metadata must be valid JSON (string could not be parsed)")
            elif not isinstance(metadata, dict):
                raise ValueError("metadata must be a dictionary or JSON string")

        payload = {
            "user_id": user_id,
            "content": content,
            "role": role,
            "content_type": content_type,
            "metadata": metadata or None,
        }

        if thread_id:
            payload["external_thread_id"] = thread_id


        try:
            resp = self.client.session.post(
                f"{self.client.base_url}/api/messages",
                json=payload
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Warning: Failed to record message: {e}")
            return {"error": str(e), "role": role, "content": content}


class ApgardClient:
    """Public SDK client for Apgard features."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000"
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })

        self.user_id: Optional[str] = None

        # Initialize feature modules
        self.breaks = BreakTracker(self)
        self.content = ContentTracker(self)

        self._verify_api_key()

    def _verify_api_key(self):
        try:
            resp = self.session.get(f"{self.base_url}/api/auth/verify")
            if resp.status_code == 401:
                raise ValueError("Invalid API key")
            resp.raise_for_status()
            data = resp.json()
            self.user_id = data.get("user_id")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API key verification failed: {e}")

    def get_or_create_user_id(self, external_user_id: str) -> UUID:
        payload = {"external_user_id": str(external_user_id)}
        resp = self.session.post(f"{self.base_url}/api/end-users/get-or-create", json=payload)
        resp.raise_for_status()
        user_id = resp.json()["user_id"]
        self.user_id = user_id
        return user_id