from nacl.signing import SigningKey

from core.storage.storage_manager import StorageManager


class CredentialsManager:
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager
        self.ensure_credentials_exist()

    def ensure_credentials_exist(self):
        if "signing_key" in self.storage_manager.read_file("credentials").keys(): return

        payload = {
            "signing_key": bytes(SigningKey.generate()).hex()
        }
        self.storage_manager.write_file("credentials", payload)

    def get_signing_key(self):
        self.ensure_credentials_exist()
        return SigningKey(bytes.fromhex(self.storage_manager.read_file("credentials").get("signing_key")))
