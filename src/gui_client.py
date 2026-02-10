import sys
import socket
import threading
import time

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        part = sock.recv(1)
        if not part:
            break
        data += part
    return data.decode().strip()


class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        ui_file = QFile("client.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.ui.btn_connect.clicked.connect(self.connect_server)
        self.ui.btn_refresh.clicked.connect(self.load_file_list)
        self.ui.btn_download.clicked.connect(self.download_selected)

        self.sock = None
        self.ui.show()

    # ---------------------------- CONNECT ----------------------------
    def connect_server(self):
        ip = self.ui.line_ip.text()
        port = int(self.ui.line_port.text())

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            self.sock.close()

            self.log(f"Connected to {ip}:{port}")
        except Exception as e:
            self.log(f"Connection error: {e}")
            QMessageBox.critical(self, "Error", str(e))

    # ---------------------------- LIST FILES ----------------------------
    def load_file_list(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ui.line_ip.text(), int(self.ui.line_port.text())))
            s.sendall(b"LIST\n")

            data = s.recv(4096).decode().split("\n")
            s.close()

            self.ui.list_files.clear()
            for f in data:
                if f.strip():
                    self.ui.list_files.addItem(f)

            self.log("File list updated.")
        except Exception as e:
            self.log(f"Error loading list: {e}")

    # ---------------------------- DOWNLOAD ----------------------------
    def download_selected(self):
        item = self.ui.list_files.currentItem()
        if not item:
            QMessageBox.warning(self, "No file", "Select a file first!")
            return

        filename = item.text()
        self.log(f"Downloading {filename}...")

        threading.Thread(
            target=self._download_thread,
            args=(filename,),
            daemon=True
        ).start()

    def _download_thread(self, filename):
        try:
            ip = self.ui.line_ip.text()
            port = int(self.ui.line_port.text())
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(f"GET {filename}\n".encode())

            header = recv_line(s)

            if not header.startswith("OK "):
                self.log(f"Server error: {header}")
                return

            filesize = int(header.split()[1])
            received = 0
            start = time.time()

            with open(filename, "wb") as f:
                while received < filesize:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    self.update_download_progress(filename, received, filesize, start)

            s.close()
            self.log(f"Download finished: {filename}")

        except Exception as e:
            self.log(f"Download error: {e}")

    # ---------------------------- TABLE UPDATE ----------------------------
    def update_download_progress(self, filename, received, total, start):
        row = self.find_table_row(filename)
        if row == -1:
            row = self.ui.table_downloads.rowCount()
            self.ui.table_downloads.insertRow(row)
            self.ui.table_downloads.setItem(row, 0, QTableWidgetItem(filename))

        percent = int(received / total * 100)
        speed = received / (time.time() - start + 0.1)
        speed = f"{speed/1024:.1f} KB/s"
        elapsed = int(time.time() - start)

        self.ui.table_downloads.setItem(row, 1, QTableWidgetItem(f"{percent}%"))
        self.ui.table_downloads.setItem(row, 2, QTableWidgetItem(speed))
        self.ui.table_downloads.setItem(row, 3, QTableWidgetItem(f"{elapsed}s"))

    def find_table_row(self, filename):
        for i in range(self.ui.table_downloads.rowCount()):
            if self.ui.table_downloads.item(i, 0) and \
               self.ui.table_downloads.item(i, 0).text() == filename:
                return i
        return -1

    def log(self, msg):
        self.ui.text_log.append(msg)


app = QApplication(sys.argv)
window = ClientGUI()
sys.exit(app.exec())
