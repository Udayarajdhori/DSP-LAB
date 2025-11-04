import streamlit as st
import jwt
import datetime
import hashlib
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# --- UTILITY FUNCTIONS ---

def hash_password(password, salt):
    """Hashes a password with a given salt using SHA256."""
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    return hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000).hex()

def verify_password(stored_hash, salt, provided_password):
    """Verifies a provided password against a stored hash and salt."""
    return stored_hash == hash_password(provided_password, salt)

# --- INITIALIZE SESSION STATE ---
# Robustly initialize all keys needed for the app's state.
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'token' not in st.session_state:
    st.session_state.token = None
if 'private_key' not in st.session_state:
    st.session_state.private_key = None
if 'public_key' not in st.session_state:
    st.session_state.public_key = None
if 'signature' not in st.session_state:
    st.session_state.signature = None
# BUG FIX: Use a randomly generated secret key for JWT, don't hardcode it.
if 'secret_key' not in st.session_state:
    st.session_state.secret_key = os.urandom(32).hex()


st.set_page_config(layout="wide")
st.title("🔐 Digital Signatures & Authentication Demo")

option = st.sidebar.selectbox(
    "Choose a concept to explore",
    ["Digital Signatures", "Authentication & Authorization (JWT)"]
)

# --- PAGE 1: DIGITAL SIGNATURES ---
if option == "Digital Signatures":
    st.header("Digital Signatures with RSA")
    st.markdown("""
    A digital signature provides three guarantees:
    - **Authentication:** Proves who signed the message.
    - **Integrity:** Ensures the message wasn't altered after signing.
    - **Non-repudiation:** The signer cannot later deny having signed the message.
    
    This is achieved by signing a message with a **private key** and verifying it with the corresponding **public key**.
    """)

    if st.button("1. Generate RSA Key Pair", type="primary"):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        st.session_state.private_key = key
        st.session_state.public_key = key.public_key()
        st.success("New RSA 2048-bit key pair generated!")

    if st.session_state.private_key:
        with st.expander("View Generated Keys"):
            # Serialize keys to PEM format for display
            pem_private = st.session_state.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            pem_public = st.session_state.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            st.text_area("Private Key (Keep this secret!)", pem_private, height=250)
            st.text_area("Public Key (Share this freely)", pem_public, height=150)

        msg_to_sign = st.text_area("Enter a message to sign:", "Hello, Streamlit!")
        if st.button("2. Sign Message with Private Key"):
            if not msg_to_sign:
                st.warning("Please enter a message to sign.")
            else:
                signature = st.session_state.private_key.sign(
                    msg_to_sign.encode(),
                    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                    hashes.SHA256()
                )
                st.session_state.signature = signature
                st.success("Message signed successfully!")
                st.text_area("Generated Signature (Base64)", base64.b64encode(signature).decode(), height=100)
        
        st.markdown("---")
        st.subheader("Verification")
        msg_to_verify = st.text_area("Enter message to verify:", "Hello, Streamlit!")
        if st.button("3. Verify Signature with Public Key"):
            if not st.session_state.signature:
                st.error("You must sign a message first!")
            elif not msg_to_verify:
                st.warning("Please enter the message that was signed.")
            else:
                try:
                    st.session_state.public_key.verify(
                        st.session_state.signature,
                        msg_to_verify.encode(),
                        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                        hashes.SHA256()
                    )
                    st.success("✅ Valid Signature! The message is authentic and has not been tampered with.")
                except Exception:
                    st.error("❌ Invalid Signature! The message may have been altered or the signature is incorrect.")

# --- PAGE 2: AUTHENTICATION & AUTHORIZATION ---
else:
    st.header("Authentication & Authorization with JWT")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. User Registration")
        with st.expander("Register a new user", expanded=True):
            reg_user = st.text_input("Username", key="reg_user")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")

            if st.button("Register"):
                if not all([reg_user, reg_pass, reg_pass_confirm]):
                     st.error("All fields are required.")
                elif reg_pass != reg_pass_confirm:
                    st.error("Passwords do not match.")
                elif reg_user in st.session_state.users:
                    st.error("Username already exists.")
                else:
                    # BUG FIX: Hash the password with a new salt. Never store plain text.
                    salt = os.urandom(16).hex()
                    hashed_pw = hash_password(reg_pass, salt)
                    st.session_state.users[reg_user] = {'hash': hashed_pw, 'salt': salt}
                    st.success(f"User '{reg_user}' registered successfully!")
                    st.info("You can now log in with your new credentials.")

    with col2:
        st.subheader("2. User Login")
        with st.expander("Login", expanded=True):
            if not st.session_state.logged_in:
                login_user = st.text_input("Username", key="login_user")
                login_pass = st.text_input("Password", type="password", key="login_pass")

                if st.button("Login"):
                    user_data = st.session_state.users.get(login_user)
                    if user_data and verify_password(user_data['hash'], user_data['salt'], login_pass):
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        # Create JWT token
                        payload = {
                            'sub': login_user,
                            'iat': datetime.datetime.utcnow(),
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                        }
                        token = jwt.encode(payload, st.session_state.secret_key, algorithm="HS256")
                        st.session_state.token = token
                        st.rerun() # Rerun to update the UI
                    else:
                        st.error("Invalid username or password.")
            
            if st.session_state.logged_in:
                st.success(f"Logged in as **{st.session_state.username}**.")
                st.text_area("Your Session JWT Token:", st.session_state.token, height=100)
                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.token = None
                    st.rerun() # Rerun to update the UI

    st.markdown("---")
    st.subheader("3. Authorization (Protected Content)")
    if st.session_state.logged_in:
        st.markdown(f"Welcome, **{st.session_state.username}**! You can see this because you are logged in.")
        try:
            # Verify the token to grant access
            decoded_payload = jwt.decode(st.session_state.token, st.session_state.secret_key, algorithms=["HS256"])
            st.success("✅ Your JWT is valid.")
            with st.expander("View decoded token payload"):
                st.json(decoded_payload)
            st.image("https://static.streamlit.io/examples/cat.jpg", caption="Here is a cat for authorized users.")
        except jwt.ExpiredSignatureError:
            st.error("❌ Your session token has expired. Please log in again.")
            st.session_state.logged_in = False # Force logout
        except jwt.InvalidTokenError:
            st.error("❌ Invalid token. Please log in again.")
            st.session_state.logged_in = False # Force logout
    else:
        st.warning("You must be logged in to view this content.")

