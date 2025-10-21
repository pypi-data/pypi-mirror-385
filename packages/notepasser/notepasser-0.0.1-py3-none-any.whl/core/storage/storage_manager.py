import json
from pathlib import Path


class StorageManager:
    def __init__(self, storage_directory=".notepasser"):
        self.storage_path = Path.home() / storage_directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.files = {
            "contacts": self.storage_path / "contacts.json",
            "credentials": self.storage_path / "credentials.json"
        }

        for file_path in self.files.keys():
            self.ensure_file_exists(file_path)

    def ensure_file_exists(self, file_id):
        file_path = self.files.get(file_id)
        if not file_path.exists() or not file_path.is_file():
            file_path.write_text("{}")

    # FILE OPERATIONS
    def read_file(self, file_id):
        with open(self.files.get(file_id), 'r') as f:
            return json.load(f)

    def write_file(self, file_id, new_content):
        with open(self.files.get(file_id), 'w') as f:
            json.dump(new_content, f)
