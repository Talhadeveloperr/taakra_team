# user/session_manager.py

import os
import json
from datetime import datetime

BASE_PATH = r"D:\projects\taakra hackathon\chatbot\flask_server\user"
SESSIONS_PATH = os.path.join(BASE_PATH, "sessions")
RAW_FILE_PATH = os.path.join(BASE_PATH, "data", "raw.json")

os.makedirs(SESSIONS_PATH, exist_ok=True)
os.makedirs(os.path.dirname(RAW_FILE_PATH), exist_ok=True)


class SessionManager:

    def _get_session_file(self, uuid: str):
        return os.path.join(SESSIONS_PATH, f"{uuid}.json")

    def create_if_not_exists(self, uuid: str):
        path = self._get_session_file(uuid)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

    def get_last_messages(self, uuid: str, limit=5):
        path = self._get_session_file(uuid)
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data[-limit:]

    def append_entry(self, uuid, user_message, model_response, model_used):
        path = self._get_session_file(uuid)
        self.create_if_not_exists(uuid)

        timestamp = datetime.utcnow().isoformat()

        entry = {
            "timestamp": timestamp,
            "user_uuid": uuid,
            "user_message": user_message,
            "model_response": model_response,
            "model_used": model_used
        }

        with open(path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        self._append_to_raw(entry)

    def _append_to_raw(self, entry):
        if not os.path.exists(RAW_FILE_PATH):
            with open(RAW_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)

        with open(RAW_FILE_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()