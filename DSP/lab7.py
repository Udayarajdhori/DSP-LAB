import streamlit as st
import hashlib
import base64

# --- Core Functions ---

def generate_text_hashes(text: str, algorithms: list) -> dict:
    """Generates multiple hashes for a given text string."""
    text_bytes = text.encode()
    hashes = {}
    for algo in algorithms:
        hasher = hashlib.new(algo)
        hasher.update(text_bytes)
        hashes[algo] = hasher.hexdigest()
    return hashes

def generate_file_hashes(file_obj, algorithms: list) -> dict:
    """
    BUG FIX: Efficiently generates multiple hashes for a file-like object.
    - Reads the file in small chunks (4KB) to keep memory usage low.
    - Computes all hashes in a single pass over the file for better performance.
    """
    hashers = {algo: hashlib.new(algo) for algo in algorithms}
    # Ensure the file read starts from the beginning
    file_obj.seek(0)
    
    # Read the file in chunks
    while chunk := file_obj.read(4096):
        for hasher in hashers.values():
            hasher.update(chunk)
            
    # Return a dictionary of the final hex digests
    return {algo: hasher.hexdigest() for algo, hasher in hashers.items()}

def obfuscate_code(code: str) -> str:
    """Obfuscates Python code using Base64 encoding."""
    try:
        encoded_code = base64.b64encode(code.encode()).decode()
        # The obfuscated code is a simple loader that decodes and executes the original script
        return f'import base64\nexec(base64.b64decode("{encoded_code}").decode())'
    except Exception as e:
        return f"Error during obfuscation: {e}"

# --- Streamlit User Interface ---

st.set_page_config(layout="wide")
st.title("🛡️ Hash & Code Obfuscator")
st.write("A simple tool for generating hashes from text/files and obfuscating Python code.")

# --- Sidebar Navigation ---
with st.sidebar:
    st.header("Controls")
    choice = st.radio("Select Mode", ["Hash Generator", "Code Obfuscator"])

# --- Main App Logic ---

# Mode 1: Hash Generator
if choice == "Hash Generator":
    st.header("Hash Generator")
    input_type = st.radio("Select input type", ["Text", "File"], horizontal=True)
    
    # Supported hash algorithms
    available_algos = sorted(hashlib.algorithms_guaranteed)
    selected_algos = st.multiselect("Select Hash Algorithms", available_algos, default=["md5", "sha256"])

    if not selected_algos:
        st.warning("Please select at least one hash algorithm.")
    
    # Hashing for Text Input
    elif input_type == "Text":
        txt_input = st.text_area("Enter text to hash", height=200)
        if st.button("Generate Hashes", type="primary") and txt_input:
            with st.spinner("Hashing..."):
                hashes = generate_text_hashes(txt_input, selected_algos)
                st.subheader("Results")
                for algo, h in hashes.items():
                    col1, col2 = st.columns([1, 4])
                    col1.code(algo)
                    col2.text_input(f"{algo}_hash", h, label_visibility="collapsed")

    # Hashing for File Input
    elif input_type == "File":
        file_input = st.file_uploader("Upload a file to hash")
        if st.button("Generate Hashes", type="primary") and file_input:
            with st.spinner(f"Hashing {file_input.name}..."):
                hashes = generate_file_hashes(file_input, selected_algos)
                st.subheader("Results")
                for algo, h in hashes.items():
                    col1, col2 = st.columns([1, 4])
                    col1.code(algo)
                    col2.text_input(f"{algo}_hash", h, label_visibility="collapsed")

# Mode 2: Code Obfuscator
else:
    st.header("Code Obfuscator")
    st.warning("Note: This is a very basic form of obfuscation and can be easily reversed. It is not a robust security measure.", icon="⚠️")
    
    code_input = st.text_area("Paste your Python code here", height=300)
    
    if st.button("Obfuscate Code", type="primary") and code_input.strip():
        obfuscated = obfuscate_code(code_input)
        st.subheader("Obfuscated Code")
        st.code(obfuscated, language="python")
