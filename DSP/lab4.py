# vulnerable.py
import hashlib
import os

# --- Example of hardcoded secret ---
api_key = "12345-SECRET-API-KEY"

# --- Example of weak hashing algorithm ---
def weak_hash(password):
    return hashlib.md5(password.encode()).hexdigest()   # ❌ Vulnerable

# --- Example of dangerous eval ---
def run_code(user_input):
    eval(user_input)   # ❌ Remote code execution risk

# --- Example of exec ---
def run_exec(cmd):
    exec(cmd)          # ❌ Remote code execution risk

# --- Example of insecure os.system call ---
def run_system(cmd):
    os.system(cmd)     # ❌ Command injection risk

# --- Example of pickle load (unsafe deserialization) ---
import pickle
def load_data(data):
    return pickle.loads(data)   # ❌ Arbitrary code execution

print("Vulnerable code loaded!")
