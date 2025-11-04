import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def extract_features(url):
    """Extracts features from a given URL."""
    return {
        "url_length": len(url),
        "has_at": int("@" in url),
        "has_https": int(url.startswith("https")),
        "num_dots": url.count("."),
        "has_hyphen": int("-" in url)
    }

@st.cache_data
def load_data():
    """Loads and preprocesses the dataset."""
    # In a real-world scenario, this data would be loaded from a CSV file.
    data = {
        "url": [
            "http://example.com", 
            "https://secure-login.com", 
            "http://phishing.com@evil.com",
            "http://paypal.login.verify.com", 
            "https://google.com", 
            "http://192.168.0.1/login",
            "https://microsoft.com", 
            "http://update-your-bank.com",
            "https://facebook-support-case-12345.com",
            "http://amazon-deals.net",
            "https://en.wikipedia.org/wiki/Phishing"
        ],
        "label": [0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0] # 0 for legitimate, 1 for phishing
    }
    df = pd.DataFrame(data)
    # Apply the feature extraction to each URL
    features = df["url"].apply(lambda url: pd.Series(extract_features(url)))
    # Combine the original data with the new features
    return pd.concat([df, features], axis=1)

# BUG FIX: This function was calculating accuracy on the entire dataset,
# including training data, which is incorrect. It's now fixed to evaluate
# on a separate test set.
@st.cache_resource
def train_model(df):
    """Splits data, trains a model, and returns the model and its accuracy."""
    feature_columns = ["url_length", "has_at", "has_https", "num_dots", "has_hyphen"]
    X = df[feature_columns]
    y = df["label"]

    # 1. Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # 2. Train the model ONLY on the training data
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # 3. Evaluate the model's accuracy on the unseen test data
    y_pred_test = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred_test)
    
    return model, acc

# --- Streamlit App ---

st.title("🎣 Phishing Website Detector")

# Load data and train the model
df = load_data()
model, acc = train_model(df)

st.sidebar.header("Model Performance")
st.sidebar.info(f"Accuracy on Test Set: {acc*100:.2f}%")

st.write(
    "Enter a URL below to check if it's likely a phishing website. "
    "This simple demo uses a Logistic Regression model trained on basic URL features."
)

url_input = st.text_input("Enter URL to check:", placeholder="https://www.google.com")

if st.button("Check URL", type="primary"):
    if url_input.strip():
        # Extract features from the user's input and create a DataFrame
        user_features = extract_features(url_input)
        X_new = pd.DataFrame([user_features])
        
        # Make a prediction
        prediction = model.predict(X_new)[0]
        prediction_proba = model.predict_proba(X_new)[0]

        # Display the result
        if prediction == 1:
            st.error(f"🚨 This URL is likely a **Phishing Site** (Confidence: {prediction_proba[1]*100:.2f}%)")
        else:
            st.success(f"✅ This URL seems to be **Legitimate** (Confidence: {prediction_proba[0]*100:.2f}%)")

        # Show the features that the model used for its decision
        with st.expander("🔍 See Features"):
            st.json(user_features)
    else:
        st.warning("Please enter a URL.")