import socket
import fileCheck
import CLibs
from dotenv import load_dotenv
import os

load_dotenv()
PORT = 8080


def send_all(sock : socket.socket, data: bytes):
    """Send exactly len(data) bytes."""
    total = 0
    while total < len(data):
        sent = sock.send(data[total:])
        if sent == 0:
            raise RuntimeError("Socket connection broken during send")
        total += sent


def recv_exact(sock : socket.socket, length: int) -> bytes:
    """Receive exactly `length` bytes."""
    buf = b''
    while len(buf) < length:
        chunk = sock.recv(min(4096, length - len(buf)))
        if not chunk:
            raise RuntimeError("Socket connection broken during recv")
        buf += chunk
    return buf


def recv_line(sock : socket.socket) -> str:
    """Receive a newline-terminated length header."""
    buf = b''
    while True:
        byte = sock.recv(1)
        if not byte:
            raise RuntimeError("Socket connection broken reading header")
        if byte == b'\n':
            return buf.decode('utf-8').strip()
        buf += byte


def send_length(sock : socket.socket, length: int):
    """Send an integer length as a newline-terminated string."""
    send_all(sock, f"{length}\n".encode('utf-8'))


def start(TARGET : str ="127.0.0.1"):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Connecting to {TARGET}:{PORT}...")
        client_sock.connect((TARGET, PORT))
        print("Connected.")

        # 1. Receive greeting
        greeting = recv_line(client_sock)
        print(greeting)

        # 2. Get file list from server
        file_amnt = int(recv_line(client_sock))
        send_all(client_sock, b'ACK')

        server_files = []
        for _ in range(file_amnt):
            name_len = int(recv_line(client_sock))
            send_all(client_sock, b'Ready')
            name = recv_exact(client_sock, name_len).decode('utf-8')
            server_files.append(name)
            send_all(client_sock, b'Received')  # fixed typo: was 'Recieved'

        # 3. Check which files are missing locally
        missing_files = fileCheck.checkMissingFiles(server_files)
        print(f"Server has {len(server_files)} files. We are missing {len(missing_files)}.")

        # 4. Send list of missing files to server
        send_length(client_sock, len(missing_files))
        recv_line(client_sock)  # Wait for ACK_AMNT

        for missing_file in missing_files:
            file_encoded = missing_file.encode('utf-8')
            send_length(client_sock, len(file_encoded))
            recv_line(client_sock)              # Wait for ACK_LEN
            send_all(client_sock, file_encoded)
            recv_line(client_sock)              # Wait for ACK_NAME

        print("Missing file list sent successfully.")

        # 5. Receive the actual file contents
        base_path = CLibs.PathTools.getPath()
        for missing_file in missing_files:
            file_len = int(recv_line(client_sock))
            send_all(client_sock, b'Received')

            if file_len == 0:
                print(f"Warning: Server could not provide: {missing_file}")
                continue

            # recv_exact guarantees the full file is received, not just one chunk
            file_data = recv_exact(client_sock, file_len)
            send_all(client_sock, b'Received')

            out_path = os.path.join(base_path, missing_file)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(file_data)
            print(f"Received: {missing_file} ({file_len} bytes)")

    except ConnectionRefusedError:
        print(f"Error: Could not connect to {TARGET}:{PORT}. Is the server running?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_sock.close()


if __name__ == "__main__":
    target_ip = os.getenv('TARGET') or "127.0.0.1"
    try:
        target_ip = socket.gethostbyname(target_ip)
    except Exception:
        pass
    start(TARGET=target_ip)