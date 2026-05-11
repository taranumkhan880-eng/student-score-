import streamlit as st
import joblib
import pandas as pd
import hashlib
import json
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Student Score Predictor", page_icon="🎓", layout="centered")

# =========================
# USER DATABASE (JSON FILE)
# =========================
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = hash_password(password)
    save_users(users)
    return True, "Account created successfully! Please log in."

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found."
    if users[username] != hash_password(password):
        return False, "Incorrect password."
    return True, "Login successful!"

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# =========================
# CUSTOM STYLES
# =========================
st.markdown("""
    <style>
        .auth-title {
            font-size: 2rem;
            font-weight: 700;
            color: #4A90D9;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .auth-sub {
            text-align: center;
            color: #888;
            margin-bottom: 1.5rem;
            font-size: 0.95rem;
        }
        .welcome-box {
            background: linear-gradient(135deg, #4A90D9, #6C63FF);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            font-size: 1.05rem;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOGIN PAGE
# =========================
def show_login():
    st.markdown('<div class="auth-title">🎓 Student Score Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Login to access your predictor</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                success, msg = login_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("---")
    st.markdown("<div style='text-align:center'>Don't have an account?</div>", unsafe_allow_html=True)
    if st.button("➕ Create an Account", use_container_width=True):
        st.session_state.page = "signup"
        st.rerun()

# =========================
# SIGNUP PAGE
# =========================
def show_signup():
    st.markdown('<div class="auth-title">📝 Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Join to start predicting student scores</div>', unsafe_allow_html=True)

    with st.form("signup_form"):
        new_username = st.text_input("👤 Choose a Username")
        new_password = st.text_input("🔒 Choose a Password", type="password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up", use_container_width=True)

        if submitted:
            if not new_username or not new_password or not confirm_password:
                st.error("Please fill in all fields.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, msg = register_user(new_username, new_password)
                if success:
                    st.success(msg)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("---")
    st.markdown("<div style='text-align:center'>Already have an account?</div>", unsafe_allow_html=True)
    if st.button("🔑 Back to Login", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()

# =========================
# MAIN PREDICTOR PAGE
# =========================
def show_predictor():
    # Welcome header
    st.markdown(
        f'<div class="welcome-box">👋 Welcome back, <strong>{st.session_state.username}</strong>! Ready to predict?</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("🎓 Student Score Predictor")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = "login"
            st.rerun()

    st.markdown("---")

    # =========================
    # LOAD MODEL
    # =========================
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
    except FileNotFoundError:
        st.error("⚠️ Model files not found. Please ensure `student_model.pkl` and `model_columns.pkl` are in the same directory.")
        return

    # =========================
    # INPUT FIELDS
    # =========================
    st.subheader("📋 Enter Student Details")

    col1, col2 = st.columns(2)

    with col1:
        hours = st.number_input("Hours Studied", 0.0, 24.0)
        attendance = st.number_input("Attendance (%)", 0.0, 100.0)
        previous = st.number_input("Previous Score", 0.0, 100.0)
        sleep = st.number_input("Sleep Hours", 0.0, 12.0)
        motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"])
        teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
        school = st.selectbox("School Type", ["Public", "Private"])

    with col2:
        internet = st.selectbox("Internet Access", ["Yes", "No"])
        income = st.selectbox("Family Income", ["Low", "Medium", "High"])
        parent = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
        education = st.selectbox("Parent Education", ["School", "College"])
        peer = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"])
        resources = st.selectbox("Learning Resources", ["Low", "Medium", "High"])
        activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])

    st.markdown("---")

    # =========================
    # PREDICTION BUTTON
    # =========================
    if st.button("🔍 Predict Score", use_container_width=True):
        data = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Sleep_Hours": sleep,
            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type": school,
            "Internet_Access": internet,
            "Family_Income": income,
            "Parental_Involvement": parent,
            "Parental_Education_Level": education,
            "Peer_Influence": peer,
            "Learning_Resources": resources,
            "Extracurricular_Activities": activities
        }

        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        prediction = model.predict(input_df)
        final_score = max(40, min(100, prediction[0]))
        final_score = int(round(final_score))

        # Color-coded result
        if final_score >= 80:
            color = "🟢"
            grade = "Excellent"
        elif final_score >= 60:
            color = "🟡"
            grade = "Average"
        else:
            color = "🔴"
            grade = "Needs Improvement"

        st.success(f"🎯 Predicted Exam Score: **{final_score}/100**")
        st.info(f"{color} Performance Level: **{grade}**")

# =========================
# ROUTING
# =========================
if st.session_state.logged_in:
    show_predictor()
elif st.session_state.page == "signup":
    show_signup()
else:
    show_login()
