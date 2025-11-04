import streamlit as st
import hashlib
import time

# --- Confidentiality Simulation ---
def caesar_cipher_encrypt(text, shift):
    """Encrypts text using a simple Caesar cipher."""
    result = ""
    for char in text:
        if 'a' <= char.lower() <= 'z':
            start = ord('a') if char.islower() else ord('A')
            shifted_char = chr(start + (ord(char) - start + shift) % 26)
            result += shifted_char
        else:
            result += char
    return result

def caesar_cipher_decrypt(text, shift):
    """Decrypts text encrypted with a Caesar cipher."""
    return caesar_cipher_encrypt(text, -shift)

def confidentiality_simulation():
    """Confidentiality section of the app."""
    st.header("1. Confidentiality Simulation 🔒")
    st.markdown("Use a simple Caesar cipher to encrypt and decrypt data.")
    
    col1, col2 = st.columns(2)
    with col1:
        message = st.text_input("Enter your secret message:")
        shift = st.slider("Select Shift Value", 1, 25, 3)
        if st.button("Encrypt"):
            if message:
                st.session_state.encrypted_message = caesar_cipher_encrypt(message, shift)
                st.session_state.cipher_shift = shift
                st.success("Message Encrypted!")
                
    with col2:
        if "encrypted_message" in st.session_state and st.session_state.encrypted_message:
            st.code(st.session_state.encrypted_message, language='text')
            
            if st.button("Decrypt"):
                decrypted_message = caesar_cipher_decrypt(st.session_state.encrypted_message, st.session_state.cipher_shift)
                st.info(f"Decrypted Message: {decrypted_message}")

# --- Integrity Simulation ---
def integrity_simulation():
    """Integrity section of the app."""
    st.header("2. Integrity Simulation ✅")
    st.markdown("Use SHA-256 hashing to check for data tampering.")
    
    initial_data = st.text_input("Enter data to protect:", "The secret is in the hash.")
    
    if st.button("Generate Hash"):
        st.session_state.original_hash = hashlib.sha256(initial_data.encode()).hexdigest()
        st.code(f"Original Hash: {st.session_state.original_hash}", language="text")

    if "original_hash" in st.session_state:
        modified_data = st.text_input("Modify the data to see the hash change:", initial_data)
        current_hash = hashlib.sha256(modified_data.encode()).hexdigest()
        st.code(f"Current Hash: {current_hash}", language="text")
        
        if current_hash == st.session_state.original_hash:
            st.success("Integrity Check: Data is unchanged! 👍")
        else:
            st.error("Integrity Check: Data has been tampered with! 🚨")

# --- Availability Simulation ---
def availability_simulation():
    """Availability section of the app."""
    st.header("3. Availability Simulation ⏰")
    st.markdown("Simulate a DoS attack to see how it affects a service.")
    
    if "service_status" not in st.session_state:
        st.session_state.service_status = "Available"
        st.session_state.requests_per_second = 0
        
    status_placeholder = st.empty()
    
    def update_status():
        status_placeholder.write(f"Service Status: *{st.session_state.service_status}*")
        status_placeholder.metric("Current Load", st.session_state.requests_per_second)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Simulate DoS Attack"):
            if st.session_state.service_status == "Available":
                st.session_state.service_status = "Under Attack"
                st.session_state.requests_per_second = 1000
                st.warning("Service is under attack! 💣")
                update_status()
                time.sleep(1) # Simulate service degradation
                st.session_state.service_status = "Unavailable"
                update_status()
                
    with col2:
        if st.button("Mitigate Attack"):
            st.session_state.service_status = "Available"
            st.session_state.requests_per_second = 10
            st.success("Attack mitigated. Service restored! 🎉")
            update_status()

    # Initial status display
    update_status()

# --- Main App Logic ---
def main():
    """Main Streamlit app function."""
    st.title("Exploring CIA Triad with Simulations")
    st.markdown("A simple demonstration of Confidentiality, Integrity, and Availability.")
    
    st.sidebar.title("Simulations")
    selection = st.sidebar.radio("Go to:", ["Confidentiality", "Integrity", "Availability"])
    
    if selection == "Confidentiality":
        confidentiality_simulation()
    elif selection == "Integrity":
        integrity_simulation()
    elif selection == "Availability":
        availability_simulation()

if __name__ == "_main_":
    main()