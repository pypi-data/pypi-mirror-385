import json
import queue
import threading
import time
from json import JSONDecodeError
from socket import socket, timeout

from nacl.exceptions import BadSignatureError
from nacl.public import PrivateKey, Box, PublicKey
from nacl.signing import SigningKey, VerifyKey

from core.globals import running
from core.storage.user_manager import UserManager
from core.debug.debugging import log


class Peer:
    def __init__(self, network_manager, user_manager: UserManager, conn, addr, my_sign: SigningKey, get_trusted_token):
        self.network_manager = network_manager
        self.user_manager = user_manager
        self.conn = conn
        self.addr = addr

        self.trusted = False

        self.my_sign = my_sign
        self.my_verify = my_sign.verify_key
        self.my_sk = PrivateKey.generate()
        self.my_pk = self.my_sk.public_key
        self.my_box = None
        self.message_queue = queue.Queue()
        self.events_queue = queue.Queue()
        self.get_trusted_token = get_trusted_token

        self.peer_information = None
        self.user_information = {
            "verify_key": self.my_verify,
            "trusted_token": None
        }

        payload = {
            "type": "connection".encode().hex(),
            "encryption_key": bytes(self.my_pk).hex(),
            "signature": self.my_sign.sign(bytes(self.my_pk)).signature.hex(),
            "verify_key": bytes(self.my_verify).hex(),
            "trusted_token_exists": bool(self.user_information.get("trusted_token"))
        }

        threading.Thread(target=self.listen_for_connection_information, daemon=True).start()

        conn.sendall(json.dumps(payload).encode())

    def listen_for_connection_information(self):
        while running and not self.peer_information:
            try:
                data = json.loads(self.conn.recv(4096).decode("utf-8"))

                peer_encryption_key = bytes.fromhex(data["encryption_key"])
                peer_signature = bytes.fromhex(data["signature"])
                peer_verify_key = VerifyKey(bytes.fromhex(data["verify_key"]))
                peer_trusted_token_exists = bool(data["trusted_token_exists"])

                peer_verify_key.verify(peer_encryption_key, peer_signature)

                peer_pk = PublicKey(peer_encryption_key)
                self.my_box = Box(self.my_sk, peer_pk)

                self.peer_information = {
                    "verify_key": peer_verify_key,
                    "public_key": peer_pk,
                    "addr": self.addr,
                    "trusted_token_exists": peer_trusted_token_exists
                }

                self.reload_user_information()
                self.resolve_trusted_state()
            except Exception:
                self.disconnect()

        if self.my_box:
            threading.Thread(target=self.listen_for_messages, daemon=True).start()

    def listen_for_messages(self):
        while running:
            if not self.my_box:
                time.sleep(0.01)
                continue
            try:
                encrypted = self.conn.recv(4096)
                if not encrypted:
                    log(f"{self.addr} disconnected")
                    break
                message = json.loads(self.my_box.decrypt(encrypted).decode())
                log(f"[{self.addr}] {message}")

                match message["type"]:
                    case "message":
                        self.message_queue.put([self.addr, message])
                    case "trusted_token":
                        self.events_queue.put([self.addr, message])
                    case "disconnect":
                        log(f"disconnect gracefully")
                        break
                    case _:
                        log("broke")
                        self.disconnect()
            except Exception as e:
                log(e)
                self.disconnect()

    def resolve_trusted_state(self):
        me_trust_peer = bool(self.user_information.get("trusted_token"))
        peer_trust_me = self.peer_information.get("trusted_token_exists")

        trusted = False

        if me_trust_peer or peer_trust_me:
            log("me trust peer: " + str(me_trust_peer), "peer trust me: " + str(peer_trust_me))
            trusted = True

        self.trusted = trusted

    def start_token_request(self):
        return True # IM OUT OF TIME BELOW DOESNT WORK MOSTLY

        if not self.my_box:
            log("handshake not complete: start_token_request")
            return

        def listen_for_token_packet(peer_self=self, token_timeout=100):
            log("here!1")
            start_time = time.time()
            while time.time() - start_time < token_timeout:
                try:
                    if not peer_self.events_queue.empty():
                        log("here!3")
                        addr, message = peer_self.events_queue.get()
                        peer_token = message.get("token")
                        log(f"[{peer_self.addr}] Received peer token: {peer_token}")
                        peer_self.peer_information["trusted_token_exists"] = True
                        peer_self.resolve_trusted_state()
                        return
                except Exception as e:
                    log(e)
                    continue
                time.sleep(0.05)

            log(f"[{self.addr}] Timed out waiting for peer token.")

        threading.Thread(target=listen_for_token_packet, daemon=True).start()

        token = self.get_trusted_token()

        if not token:
            return

        peer_verify_key = self.peer_information.get("verify_key")
        user = self.user_manager.get_user(peer_verify_key)
        user.trusted_token = token
        self.user_manager.contacts[peer_verify_key] = user

        payload = {"type": "trusted_token", "token": bool(token)}
        self.conn.sendall(self.my_box.encrypt(json.dumps(payload).encode()))

        self.resolve_trusted_state()

    def reload_user_information(self):
        self.user_information = self.user_manager.get_user(self.user_information.get("verify_key")).serialize()

    def send_message(self, message):
        if not self.my_box:
            log("handshake not complete: send_message")
            return
        message = {
            "type": "message",
            "message": message,
        }
        try:
            self.conn.sendall(self.my_box.encrypt(json.dumps(message).encode()))
            self.message_queue.put([self.addr, message])
        except Exception:
            log(f"connection lost")
            self.disconnect()

    def send_disconnect(self):
        if self.my_box:
            try:
                payload = {"type": "disconnect"}
                self.conn.sendall(self.my_box.encrypt(json.dumps(payload).encode()))
            except:
                pass

    def disconnect(self):
        try:
            self.send_disconnect()
            self.conn.close()
        except:
            pass