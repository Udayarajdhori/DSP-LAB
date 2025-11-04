import streamlit as st
import hashlib
import itertools
import string
import time
import pandas as pd
import io

# A small, simple dictionary for demonstration purposes
COMMON_PASSWORDS = ["password", "Shrihari@2004","123456", "qwerty", "dragon", "admin", "secret", "test", "football", "welcome", "secure"]

def check_password_strength(password):
    """
    Analyzes a password and categorizes its strength.
    Criteria: length, character mix, and dictionary check.
    """
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    
    # Check against a small list of common passwords
    is_dictionary_word = password.lower() in [p.lower() for p in COMMON_PASSWORDS]
    
    # Score based on criteria
    score = 0
    if length >= 8:
        score += 1
    if has_upper and has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_symbol:
        score += 1
    
    # Categorize based on score
    if is_dictionary_word or length < 4:
        return "Weak"
    if score >= 3 and length >= 12:
        return "Strong"
    if score >= 2 and length >= 8:
        return "Medium"
    return "Weak"

def dictionary_attack(target, is_hash_attack, dictionary_list):
    """
    Simulates a dictionary attack, either on plaintext or a hash.
    Returns the cracked password or a failure message.
    """
    if is_hash_attack:
        st.subheader("Attacking Hash Value")
        st.info("Searching for a dictionary word whose hash matches the target hash...")
    else:
        st.subheader("Attacking Plaintext")
        st.info("Searching for a dictionary word that matches the plaintext...")
        
    start_time = time.time()
    
    for password_candidate in dictionary_list:
        if is_hash_attack:
            # Hash the candidate and compare
            hashed_candidate = hashlib.sha256(password_candidate.encode()).hexdigest()
            if hashed_candidate == target:
                end_time = time.time()
                elapsed = round(end_time - start_time, 4)
                st.success(f"🔓 *SUCCESS!* Cracked password is: {password_candidate} (Time taken: {elapsed} seconds)")
                return password_candidate
        else:
            # Direct plaintext comparison
            if password_candidate == target:
                end_time = time.time()
                elapsed = round(end_time - start_time, 4)
                st.success(f"🔓 *SUCCESS!* Cracked password is: {password_candidate} (Time taken: {elapsed} seconds)")
                return password_candidate
    
    end_time = time.time()
    elapsed = round(end_time - start_time, 4)
    st.error(f"❌ *FAILURE!* Password not found in the dictionary. (Time taken: {elapsed} seconds)")
    return None

def brute_force_simulation(target_password, character_set, max_length):
    """
    Simulates a brute-force attack with a real-time progress bar.
    This is computationally expensive; be cautious with max_length.
    """
    st.subheader("Brute-Force Attack")
    st.info(f"Attempting to crack the password by trying all combinations (max length {max_length}).")
    st.warning("Warning: This can take a very long time for longer passwords!")
    
    found = False
    password_found = ""
    start_time = time.time()
    
    # Real-time progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for length in range(1, max_length + 1):
        total_combinations = len(character_set) ** length
        current_attempt = 0
        
        for attempt in itertools.product(character_set, repeat=length):
            current_attempt += 1
            password_candidate = "".join(attempt)
            
            # Update progress bar every 10,000 attempts for performance
            if current_attempt % 10000 == 0:
                progress = current_attempt / total_combinations if total_combinations > 0 else 1
                progress_bar.progress(progress)
                status_text.text(f"Trying combinations of length {length}... (Attempt {current_attempt}/{total_combinations})")
            
            if password_candidate == target_password:
                found = True
                password_found = password_candidate
                break
        
        if found:
            break
            
    progress_bar.progress(1.0)
    end_time = time.time()
    elapsed = round(end_time - start_time, 4)
    
    if found:
        status_text.success(f"🔓 *SUCCESS!* Brute-force cracked password: {password_found} (Time taken: {elapsed} seconds)")
    else:
        status_text.error(f"❌ *FAILURE!* Password not found up to length {max_length}. (Time taken: {elapsed} seconds)")
        
def create_report(df, file_format):
    """
    Generates a report string in either TXT or CSV format from a DataFrame.
    """
    if file_format == 'txt':
        report_string = "Password Analysis Report\n" + "="*25 + "\n\n"
        for _, row in df.iterrows():
            report_string += f"Password: {row['Password']}\n"
            report_string += f"Strength: {row['Strength']}\n"
            report_string += "-"*15 + "\n"
        return report_string
    
    elif file_format == 'csv':
        return df.to_csv(index=False)
    
# --- Main Streamlit App ---

st.title("Password Security Analyzer")
st.markdown("A simple tool to demonstrate common password attacks and check password strength.")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dictionary Attack", "Brute-Force Attack", "Password Strength Checker", "Analyze Passwords File"])

# --- Main Page Content ---

if page == "Dictionary Attack":
    st.header("Dictionary Attack Simulation")
    st.markdown("A dictionary attack tries to crack a password by comparing it to a list of common words.")
    
    attack_type = st.radio("Select Attack Type:", ["Plaintext", "Hash Value"])
    
    if attack_type == "Plaintext":
        plaintext_password = st.text_input("Enter a plaintext password to attack:", "password")
        if st.button("Run Dictionary Attack"):
            dictionary_attack(plaintext_password, False, COMMON_PASSWORDS)
            
    else: # Hash Value
        hash_value = st.text_input("Enter a SHA-256 hash value to attack:", hashlib.sha256("password".encode()).hexdigest())
        if st.button("Run Dictionary Attack"):
            dictionary_attack(hash_value, True, COMMON_PASSWORDS)

elif page == "Brute-Force Attack":
    st.header("Brute-Force Attack Simulation")
    st.markdown("A brute-force attack tries every possible combination of characters until it finds a match.")
    
    target_password = st.text_input("Enter a password to crack:", "abc")
    max_length = st.slider("Max password length to check:", 1, 10, 4)
    character_set_choice = st.selectbox("Character Set:", ["Lowercase letters", "Lowercase + Digits", "All Ascii"])
    
    char_set = ""
    if character_set_choice == "Lowercase letters":
        char_set = string.ascii_lowercase
    elif character_set_choice == "Lowercase + Digits":
        char_set = string.ascii_lowercase + string.digits
    else:
        char_set = string.ascii_letters + string.digits + string.punctuation
        
    st.info(f"Target password: {target_password}")
    st.markdown(f"*Selected character set:* {char_set}")
    
    if st.button("Start Brute-Force"):
        brute_force_simulation(target_password, char_set, max_length)

elif page == "Password Strength Checker":
    st.header("Password Strength Checker")
    st.markdown("This tool checks if a password is weak, medium, or strong based on its complexity.")
    
    password_to_check = st.text_input("Enter a password to check its strength:", type="password")
    
    if password_to_check:
        strength = check_password_strength(password_to_check)
        if strength == "Weak":
            st.error(f"🔴 Your password is *{strength}*.")
            st.markdown("⚠ *Tip:* Avoid common words and use a mix of characters and longer lengths.")
        elif strength == "Medium":
            st.warning(f"🟡 Your password is *{strength}*.")
            st.markdown("⚠ *Tip:* Consider adding more characters or a symbol for better security.")
        elif strength == "Strong":
            st.success(f"🟢 Your password is *{strength}*.")
            st.markdown("✅ *Great!* This password is well-protected against common attacks.")
            
elif page == "Analyze Passwords File":
    st.header("Analyze & Export Password Report")
    st.markdown("Upload a file with one password per line to analyze and export a report.")
    
    uploaded_file = st.file_uploader("Choose a TXT file", type="txt")
    
    if uploaded_file:
        file_content = uploaded_file.getvalue().decode("utf-8")
        passwords = [line.strip() for line in file_content.splitlines() if line.strip()]
        
        results = []
        with st.spinner("Analyzing passwords..."):
            for pwd in passwords:
                strength = check_password_strength(pwd)
                results.append({"Password": pwd, "Strength": strength})
        
        df = pd.DataFrame(results)
        
        st.subheader("Analysis Results")
        st.dataframe(df)
        
        # Create export buttons
        st.markdown("---")
        st.subheader("Export Report")
        
        col1, col2 = st.columns(2)
        
        # TXT export
        txt_report_content = create_report(df, 'txt')
        col1.download_button(
            label="Download as TXT",
            data=txt_report_content,
            file_name="password_analysis_report.txt",
            mime="text/plain"
        )
        
        # CSV export
        csv_report_content = create_report(df, 'csv')
        col2.download_button(
            label="Download as CSV",
            data=csv_report_content,
            file_name="password_analysis_report.csv",
            mime="text/csv"
        )