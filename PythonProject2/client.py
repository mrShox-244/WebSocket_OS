import socket

IP = '192.168.0.106'
PORT = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((IP, PORT))
    print("Connected to server")
except Exception as e:
    print("Connection error:", e)
    exit()

while True:
    try:
        msg = input("Enter your message: ")
        s.send(msg.encode())

        reply = s.recv(1024)
        if not reply:
            print("Server closed connection")
            break

        print("Server says:", reply.decode())

    except KeyboardInterrupt:
        print("\nClient stopped.")
        break

    except Exception as e:
        print("Error:", e)
        break

s.close()
