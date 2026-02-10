import socket
import threading
import os

HOST = "0.0.0.0"
PORT = 9090
SHARE_DIR = "shared"


def handle_client(conn, addr):
    print(f"[CONNECT] {addr}")

    try:
        request = recv_line(conn)

        if request == "LIST":
            files = os.listdir(SHARE_DIR)
            response = "\n".join(files) + "\n"
            conn.sendall(response.encode())
            conn.close()
            return

        if request.startswith("GET "):
            filename = request.split(" ", 1)[1]
            filepath = os.path.join(SHARE_DIR, filename)

            if not os.path.isfile(filepath):
                conn.sendall(b"ERROR File not found\n")
                conn.close()
                return

            filesize = os.path.getsize(filepath)
            conn.sendall(f"OK {filesize}\n".encode())

            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)

            print(f"[DONE] Sent {filename}")
            conn.close()
            return

        conn.sendall(b"ERROR Unknown command\n")

    except Exception as e:
        print("Error:", e)

    conn.close()


def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        part = sock.recv(1)
        if not part:
            break
        data += part
    return data.decode().strip()


def start_server():
    if not os.path.exists(SHARE_DIR):
        os.mkdir(SHARE_DIR)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)

    print(f"[SERVER] Running on port {PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
