import socket
import threading
import time

from core.globals import VERSION
from core.storage.credentials_manager import CredentialsManager
from core.debug.debugging import log


class DiscoveryManager:
    def __init__(self, ip, port, discovery_port, verify_key, user_manager, max_broadcast_number):
        self.ip = ip
        self.port = port
        self.discovery_port = discovery_port
        self.verify_key = bytes(verify_key).hex()
        self.user_manager = user_manager
        self.max_broadcast_number = max_broadcast_number
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.discovery_port))

        self.replied_to = set()
        self.reply_timeout = 3

    def get_broadcast_string(self):
        return f"NOTEPASSER|{VERSION}|{self.verify_key}|{self.ip}|{self.port}"

    def start_broadcast(self):
        def broadcast():
            log("discovery broadcast started")
            self.user_manager.discovered = []
            for i in range(0, self.max_broadcast_number):
                message = self.get_broadcast_string()
                log("sending discovery packet " + message)
                self.sock.sendto(message.encode("utf-8"), ("255.255.255.255", self.discovery_port))
                time.sleep(1.5)

        threading.Thread(target=broadcast, daemon=True).start()

    def start_listening(self):
        def listen():
             log("discovery listen started")
             while True:
                 try:
                     data, addr = self.sock.recvfrom(4096)
                     text = data.decode("utf-8", errors="replace").split("|")
                     if len(text) != 5:
                         log("discovered invalid user")
                         continue
                     prefix, version, peer_verify_key, ip, port = text
                     peer_addr = (ip, int(port))
                     if prefix != "NOTEPASSER" or version != VERSION:
                         log("different version or irrelevant packet")
                         continue
                     if peer_verify_key == self.verify_key:
                         log("discovered self")
                         continue
                     log("discovered user " + peer_verify_key + " with address " + str(peer_addr))
                     self.user_manager.on_user_discovered(peer_verify_key, peer_addr)
                     self.respond_to_discovery_request(peer_verify_key)
                 except socket.timeout:
                     continue
                 except ConnectionResetError:
                     log("windows badness")
                     continue

        threading.Thread(target=listen, daemon=True).start()

    def respond_to_discovery_request(self, peer_verify_key):
        if peer_verify_key in self.replied_to: return
        log("sending discovery packet")
        self.sock.sendto(self.get_broadcast_string().encode("utf-8"), ("255.255.255.255", self.discovery_port)) # this should really have some kind of limiter
        self.replied_to.add(peer_verify_key)
        self.remove_from_replied_to_after_delay(peer_verify_key)

    def remove_from_replied_to_after_delay(self, peer_verify_key):
        def remove():
            nonlocal peer_verify_key
            time.sleep(self.reply_timeout)
            if not peer_verify_key in self.replied_to: return
            self.replied_to.remove(peer_verify_key)

        threading.Thread(target=remove, daemon=True).start()
