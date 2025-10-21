import socket
import threading
import time

from core.storage.credentials_manager import CredentialsManager
from core.globals import running
from core.networking.peer import Peer
from core.storage.user_manager import UserManager
from core.debug.debugging import log


class NetworkManager:
    def __init__(self, ip, port, credentials_manager: CredentialsManager, user_manager: UserManager, get_trusted_token_input):
        self.credentials_manager = credentials_manager
        self.user_manager = user_manager
        self.get_trusted_token_input = get_trusted_token_input
        self.peers = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(5)

        threading.Thread(target=self.listen_for_peers, daemon=True).start()

    def listen_for_peers(self):
        while running:
            conn, addr = self.sock.accept()
            log("accepted peer " + str(addr))
            if addr in self.peers:
                log("already exists")
                return
            self.peers[addr] = Peer(self, self.user_manager, conn, addr, self.credentials_manager.get_signing_key(), self.get_trusted_token_input)

    def connect_to_peer(self, verify_key):
        user = self.user_manager.get_user(verify_key)
        peer_ip, peer_port = user.addr
        log("trying to connect to " + str(user.addr))

        for peer in self.peers.values():
            timeout = 5
            start = time.time()
            while peer.peer_information is None and time.time() - start < timeout:
                time.sleep(0.1)
            print(bytes(peer.peer_information['verify_key']).hex(), verify_key)
            if peer.peer_information and bytes(peer.peer_information['verify_key']).hex() == verify_key:
                return peer

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((peer_ip, peer_port))

            self.peers[(peer_ip, peer_port)] = Peer(self, self.user_manager, conn, (peer_ip, peer_port), self.credentials_manager.get_signing_key(), self.get_trusted_token_input)
            log("connected to " + str((peer_ip, peer_port)))
            return self.peers[(peer_ip, peer_port)]
        except Exception as e:
            log(e)

    def disconnect_peer(self, addr):
        if addr in self.peers:
            del self.peers[addr]
            log(f"disconnected peer {addr}")