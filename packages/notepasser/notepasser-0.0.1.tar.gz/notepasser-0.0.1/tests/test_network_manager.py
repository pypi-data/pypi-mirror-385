import time

from core.storage.credentials_manager import CredentialsManager
from core.networking.network_manager import NetworkManager
from core.storage.storage_manager import StorageManager


def test_send_and_receive():
    nm1 = NetworkManager("127.0.0.1", 32313, CredentialsManager(StorageManager()))
    nm2 = NetworkManager("127.0.0.1", 32314, CredentialsManager(StorageManager()))

    time.sleep(0.5)

    nm1.connect_to_peer(("127.0.0.1", 32314))
    peer1 = nm1.peers[("127.0.0.1", 32314)]
    while not peer1.my_box:
        time.sleep(0.1)

    peer2 = list(nm2.peers.values())[0]

    peer1.send_message("hello1")
    peer2.send_message("hello2")

    time.sleep(0.5)

    print("------")
    print(peer1.message_queue.get())
    print(peer1.message_queue.get())
    print("------")
    print(peer2.message_queue.get())
    print(peer2.message_queue.get())