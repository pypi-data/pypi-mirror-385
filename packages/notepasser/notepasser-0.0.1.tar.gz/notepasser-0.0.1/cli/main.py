import socket
import threading
import time
from core.networking.discovery_manager import DiscoveryManager
from core.networking.network_manager import NetworkManager
from core.storage.credentials_manager import CredentialsManager
from core.storage.storage_manager import StorageManager
from core.storage.user_manager import UserManager
from core.debug.debugging import log
from core.globals import running


def main():
    storage = StorageManager()
    user_manager = UserManager(storage)
    credentials = CredentialsManager(storage)

    discovery_port = 33311
    ip = socket.gethostbyname(socket.gethostname())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, 0))
    port = sock.getsockname()[1]
    sock.close()

    print(f"[INIT] Local IP: {ip}:{port}")

    network = NetworkManager(ip, port, credentials, user_manager, input)
    discovery = DiscoveryManager(
        ip=ip,
        port=port,
        discovery_port=discovery_port,
        verify_key=credentials.get_signing_key().verify_key,
        user_manager=user_manager,
        max_broadcast_number=3
    )

    discovery.start_listening()
    discovery.start_broadcast()
    print("[DISCOVERY] Started listening and broadcasting...")

    try:
        while running:
            print("\nCOMMANDS:")
            print("discover - Show discovered peers")
            print("connect - Connect to a peer by index")
            print("exit - Quit program")
            print("--------------------------")
            cmd = input("> ").strip().lower()

            if cmd == "exit":
                print("[EXIT] Shutting down...")
                break

            elif cmd == "discover":
                peers = user_manager.discovered
                if not peers:
                    print("[DISCOVERY] No peers found yet.")
                else:
                    for i, p in enumerate(peers):
                        print(f"[{i}] {p}")

            elif cmd == "connect":
                peers = user_manager.discovered
                if not peers:
                    print("[CONNECT] No peers discovered.")
                    continue

                print("Select peer index:")
                for i, p in enumerate(peers):
                    print(f"[{i}] {p}")
                try:
                    idx = int(input("> "))
                    target = peers[idx]
                except (ValueError, IndexError):
                    print("[ERROR] Invalid index.")
                    continue

                peer = network.connect_to_peer(target)
                if not peer:
                    print("[CONNECT] Failed to connect.")
                    continue

                print(f"[CONNECTED] Messaging session started with {target}.")
                print("Commands inside chat: |exit|")

                chat_active = True

                def display_messages():
                    while running and chat_active:
                        while not peer.message_queue.empty():
                            addr, message = peer.message_queue.get()
                            print(f"\n[{addr[0]}]: {message['message']}")
                            print("> ", end="", flush=True)
                        time.sleep(0.1)

                msg_thread = threading.Thread(target=display_messages, daemon=True)
                msg_thread.start()

                while running:
                    msg = input("> ")
                    if msg == "|exit|":
                        print("[CHAT] Ending session...")
                        chat_active = False
                        peer.disconnect()
                        break
                    elif msg.strip():
                        peer.send_message(msg)

            else:
                print("[ERROR] Unknown command.")

    except KeyboardInterrupt:
        print("\n[EXIT] Interrupted by user.")
    finally:
        print("[CLEANUP] Disconnecting all peers...")
        for peer in list(network.peers.values()):
            peer.disconnect()
        discovery.running = False
        print("[EXIT] Shutdown complete.")


if __name__ == "__main__":
    main()