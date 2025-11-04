import socket, ssl, threading, base64
from nacl.public import PrivateKey, PublicKey, Box

HOST = '127.0.0.1'
PORT = 8888

# Generate server keypair
server_private = PrivateKey.generate()
server_public = server_private.public_key

clients = []  # list of (conn, box)

def handle_client(conn, addr, box):
    print(f"[+] Client connected: {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            print(f"[Encrypted from {addr}] {base64.b64encode(data).decode()}")
            try:
                plaintext = box.decrypt(data).decode()
                print(f"[Decrypted] {plaintext}")
            except Exception as e:
                print(f"[Decrypt Error] {e}")
                continue

            # broadcast plaintext (re-encrypt with each client's box)
            for c, b in clients[:]:
                if c != conn:
                    try:
                        c.send(b.encrypt(plaintext.encode()))
                    except Exception as e:
                        print(f"[Send Error] {e}, removing client")
                        clients.remove((c, b))
    finally:
        print(f"[-] Client disconnected: {addr}")
        clients.remove((conn, box))
        conn.close()

def client_thread(ssl_conn, addr):
    # Step 1: exchange public keys
    ssl_conn.send(server_public.encode())  # send server public key
    client_pub = PublicKey(ssl_conn.recv(32))  # receive client public key
    box = Box(server_private, client_pub)
    clients.append((ssl_conn, box))
    handle_client(ssl_conn, addr, box)

def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"[*] Server listening on {HOST}:{PORT}")
        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
