import streamlit as st
import mysql.connector

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="voting_system"
)
cursor = db.cursor()

# Initialize session
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "verified_user_id" not in st.session_state:
    st.session_state.verified_user_id = None

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("Cast Vote"):
    st.session_state.menu = "Cast Vote"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"

# Functions
def is_valid_student(student_id):
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    return cursor.fetchone() is not None

def has_already_voted(student_id):
    cursor.execute("SELECT * FROM votes WHERE student_id = %s", (student_id,))
    return cursor.fetchone() is not None

def record_vote(student_id, candidate_id):
    # Insert vote
    cursor.execute("INSERT INTO votes (student_id, candidate_id) VALUES (%s, %s)", (student_id, candidate_id))
    # Update vote count with corrected column name
    cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE candidate_id = %s", (candidate_id,))
    db.commit()

def authenticate_admin(username, password):
    cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
    return cursor.fetchone() is not None

# Pages
st.title("🗳️ Student Election System")

# Home Page
if st.session_state.menu == "Home":
    st.subheader("Welcome to the Voting System!")
    st.write("Use the sidebar to navigate.")

# Cast Vote Page
elif st.session_state.menu == "Cast Vote":
    st.subheader("Cast Your Vote")

    if not st.session_state.verified_user_id:
        student_id = st.text_input("Enter your Student ID")

        if st.button("Verify"):
            if not is_valid_student(student_id):
                st.error("Student ID does not exist.")
            elif has_already_voted(student_id):
                st.warning("You have already voted.")
            else:
                st.success("Student verified!")
                st.session_state.verified_user_id = student_id
    else:
        # Show candidates
        cursor.execute("SELECT candidate_id, name FROM candidates")
        candidates = cursor.fetchall()
        for cid, name in candidates:
            st.write(f"{cid}. {name}")

        vote = st.number_input("Enter Candidate ID", min_value=1, step=1)

        if st.button("Submit Vote"):
            try:
                record_vote(st.session_state.verified_user_id, vote)
                st.success("Vote cast successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
            st.session_state.verified_user_id = None  # Reset after vote

# Admin Panel Page
elif st.session_state.menu == "Admin Panel":
    if not st.session_state.logged_in:
        username = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_admin(username, password):
                st.session_state.logged_in = True
                st.success("Logged in successfully.")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials.")
    else:
        st.subheader("Admin Dashboard")
        st.write("Create election, view results, or manage candidates.")
        # You can extend this area for admin tools like adding candidates, viewing votes, etc.
