import socket, ssl, threading, tkinter as tk
from nacl.public import PrivateKey, PublicKey, Box

HOST = '127.0.0.1'
PORT = 8888

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat")

        # Two chat areas
        self.text_local = tk.Text(root, height=15, width=40, bg="lightyellow")
        self.text_remote = tk.Text(root, height=15, width=40, bg="lightblue")
        self.text_local.grid(row=0, column=0, padx=5, pady=5)
        self.text_remote.grid(row=0, column=1, padx=5, pady=5)

        self.entry = tk.Entry(root, width=60)
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.send_btn = tk.Button(root, text="Send", command=self.send_msg)
        self.send_btn.grid(row=1, column=2, padx=5)

        self.sock = None
        self.box = None
        self.connect()

    def connect(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = context.wrap_socket(raw_sock, server_hostname=HOST)
        self.sock.connect((HOST, PORT))

        # key exchange
        client_private = PrivateKey.generate()
        client_public = client_private.public_key
        server_pub = PublicKey(self.sock.recv(32))
        self.sock.send(bytes(client_public))
        self.box = Box(client_private, server_pub)

        threading.Thread(target=self.receive_msgs, daemon=True).start()

    def send_msg(self):
        msg = self.entry.get()
        if msg:
            self.text_local.insert(tk.END, f"You: {msg}\n")
            self.entry.delete(0, tk.END)
            ciphertext = self.box.encrypt(msg.encode())
            self.sock.send(ciphertext)

    def receive_msgs(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = self.box.decrypt(data).decode()
                self.text_remote.insert(tk.END, f"Peer: {msg}\n")
            except Exception:
                break

if __name__ == "__main__":
    root = tk.Tk()  # main window

# first chat client
client1 = ChatClient(root)

# second chat window
second_window = tk.Toplevel(root)  # new popup
client2 = ChatClient(second_window)

root.mainloop()

