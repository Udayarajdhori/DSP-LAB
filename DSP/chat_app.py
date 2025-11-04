import streamlit as st
import socket
import threading
import queue

# =============================
# Global Message Queue (Thread-Safe)
# =============================
message_queue = queue.Queue()

# =============================
# Chat Receiver Thread
# =============================
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            msg = data.decode("utf-8")
            # Put message into queue (safe for threads)
            message_queue.put(("Friend", msg))
        except:
            break

# =============================
# Main Function
# =============================
def main():
    st.title("🔗 Encrypted Chat App")

    # Init session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "sock" not in st.session_state:
        st.session_state["sock"] = None
    if "connected" not in st.session_state:
        st.session_state["connected"] = False
    if "input" not in st.session_state:
        st.session_state["input"] = ""

    # Connection setup inputs (unique keys)
    host = st.text_input("Enter host (use 127.0.0.1 for local)", "127.0.0.1", key="host_input")
    port = st.number_input("Enter port", 3000, 65535, 5000, key="port_input")
    role = st.radio("Choose Role", ["Server", "Client"], key="role_radio")

    # Connect Button
    if not st.session_state["connected"]:
        if st.button("Connect", key="connect_btn"):
            if role == "Server":
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.bind((host, port))
                server_sock.listen(1)
                conn, addr = server_sock.accept()
                st.session_state["sock"] = conn
            else:  # Client
                client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_sock.connect((host, port))
                st.session_state["sock"] = client_sock

            st.session_state["connected"] = True
            threading.Thread(target=receive_messages, args=(st.session_state["sock"],), daemon=True).start()
            st.rerun()

    # =============================
    # Chat Section
    # =============================
    if st.session_state["connected"]:
        st.subheader("💬 Chat Window")

        # ✅ Process queued messages safely
        while not message_queue.empty():
            sender, msg = message_queue.get()
            st.session_state["messages"].append((sender, msg))

        # Show chat history
        for sender, msg in st.session_state["messages"]:
            if sender == "Me":
                st.markdown(f"**🟢 Me:** {msg}")
            else:
                st.markdown(f"**🔵 Friend:** {msg}")

        # Message input (unique key)
        message = st.text_input("Type a message", value=st.session_state["input"], key="message_input")

        if st.button("Send", key="send_btn"):
            if message.strip():
                try:
                    st.session_state["sock"].sendall(message.encode("utf-8"))
                    st.session_state["messages"].append(("Me", message))
                except:
                    st.error("❌ Connection lost.")
                # Clear input safely
                st.session_state["input"] = ""
                st.rerun()

# =============================
# Run
# =============================
if __name__ == "__main__":
    main()
