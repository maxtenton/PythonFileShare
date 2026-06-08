import socket
import fileCheck
import os
import CLibs

PORT = 80
BASE_DIR = CLibs.PathTools.getPath()  # server's base file directory


def send_all(conn, data: bytes):
    """Send exactly len(data) bytes."""
    total = 0
    while total < len(data):
        sent = conn.send(data[total:])
        if sent == 0:
            raise RuntimeError("Socket connection broken during send")
        total += sent


def recv_exact(conn, length: int) -> bytes:
    """Receive exactly `length` bytes."""
    buf = b''
    while len(buf) < length:
        chunk = conn.recv(min(4096, length - len(buf)))
        if not chunk:
            raise RuntimeError("Socket connection broken during recv")
        buf += chunk
    return buf


def recv_line(conn) -> str:
    """Receive a newline-terminated length header."""
    buf = b''
    while True:
        byte = conn.recv(1)
        if not byte:
            raise RuntimeError("Socket connection broken reading header")
        if byte == b'\n':
            return buf.decode('utf-8').strip()
        buf += byte


def send_length(conn, length: int):
    """Send an integer length as a newline-terminated string."""
    send_all(conn, f"{length}\n".encode('utf-8'))


def SendFiles(TARGET_IP=CLibs.NetTools.getLocalIP()):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_sock.bind((TARGET_IP, PORT))
        server_sock.listen(5)
        print(f"Server listening on {TARGET_IP}:{PORT}")

        while True:
            conn, clt_address = server_sock.accept()
            print(f"Received connection from {clt_address}")

            try:
                # 1. Send greeting
                send_all(conn, b'Connection established\n')

                # 2. Send file list
                files = fileCheck.getFullFileTree()
                send_length(conn, len(files))
                conn.recv(1024)  # Wait for ACK

                for file in files:
                    file_encoded = file.encode('utf-8')
                    send_length(conn, len(file_encoded))
                    conn.recv(1024)          # Wait for "Ready"
                    send_all(conn, file_encoded)
                    conn.recv(1024)          # Wait for "Received"

                # 3. Receive list of missing files from client
                file_amnt = int(recv_line(conn))
                send_all(conn, b'ACK_AMNT\n')

                missing_files = []
                for _ in range(file_amnt):
                    length = int(recv_line(conn))
                    send_all(conn, b'ACK_LEN\n')
                    name = recv_exact(conn, length).decode('utf-8')
                    send_all(conn, b'ACK_NAME\n')
                    missing_files.append(name)

                print(f"Client requested {len(missing_files)} files: {missing_files}")

                # 4. Send the actual file contents
                for missing_file in missing_files:
                    # Map client-relative path to server's real path
                    full_path = os.path.join(BASE_DIR, missing_file)
                    try:
                        with open(full_path, 'rb') as f:
                            data = f.read()
                        send_length(conn, len(data))   # Send file size (not str(data)!)
                        conn.recv(1024)                # Wait for ACK
                        send_all(conn, data)           # Send actual bytes
                        conn.recv(1024)                # Wait for ACK
                        print(f"Sent: {missing_file} ({len(data)} bytes)")
                    except FileNotFoundError:
                        print(f"Warning: File not found on server: {full_path}")
                        send_length(conn, 0)           # Signal 0 bytes so client doesn't hang
                        conn.recv(1024)

            except Exception as e:
                print(f"Error handling client: {e}")
            finally:
                conn.close()
                print("Connection closed. Waiting for next client...")

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_sock.close()


if __name__ == "__main__":
    SendFiles()