import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9090


def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        part = sock.recv(1)
        if not part:
            break
        data += part
    return data.decode().strip()


def download(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, SERVER_PORT))

    s.sendall(f"GET {filename}\n".encode())

    header = recv_line(s)

    if not header.startswith("OK "):
        print("Server error:", header)
        return

    filesize = int(header.split()[1])
    print(f"Downloading {filename} ({filesize} bytes)")

    received = 0

    with open(filename, "wb") as f:
        while received < filesize:
            chunk = s.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
            print(f"\rProgress: {received * 100 / filesize:.1f}%", end="")

    print("\nCompleted!")
    s.close()


if __name__ == "__main__":
    file = input("Enter file name: ")
    download(file)
