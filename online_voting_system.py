import streamlit as st
import mysql.connector
import pandas as pd
import altair as alt

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ram@123",
    database="voting_system"
)
cursor = db.cursor()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "vote_verified" not in st.session_state:
    st.session_state.vote_verified = False
if "verified_user_id" not in st.session_state:
    st.session_state.verified_user_id = None

# Utility functions
def is_student_registered(student_id):
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    return cursor.fetchone()

def has_voted(student_id, election_id):
    cursor.execute("SELECT * FROM cast_vote WHERE student_id = %s AND election_id = %s", (student_id, election_id))
    return cursor.fetchone() is not None

def record_vote(student_id, candidate_id, election_id):
    cursor.execute("INSERT INTO cast_vote (student_id, candidate_id, election_id) VALUES (%s, %s, %s)", (student_id, candidate_id, election_id))
    cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE candidate_id = %s", (candidate_id,))
    db.commit()

def authenticate_admin(username, password):
    cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
    return cursor.fetchone()

def register_student(sid, name, email, pw):
    cursor.execute("INSERT INTO students (student_id, name, email, password) VALUES (%s, %s, %s, %s)", (sid, name, email, pw))
    db.commit()

def register_admin(uname, email, pw):
    cursor.execute("INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)", (uname, email, pw))
    db.commit()

def get_active_election():
    cursor.execute("SELECT * FROM elections WHERE election_status = 'Active'")
    return cursor.fetchone()

def get_candidates_by_election(election_id):
    cursor.execute("SELECT * FROM candidates WHERE election_id = %s", (election_id,))
    return cursor.fetchall()

# UI Setup
st.title("🗳️ Student Voting System")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Cast Vote", "Registration", "Admin", "Show Results"])

# Home
if menu == "Home":
    st.subheader("Welcome to the Student Voting System!")
    st.info("Use the sidebar to navigate to voting, registration, or admin options.")

elif menu == "Cast Vote":
    st.subheader("Cast Your Vote")
    active_election = get_active_election()

    if not active_election:
        st.warning("No active election at the moment.")
    else:
        election_id = active_election[0]
        election_name = active_election[1]
        st.write(f"🗳️ Election: **{election_name}**")

        if not st.session_state.vote_verified:
            user_id = st.text_input("Enter your Student ID:")
            password = st.text_input("Enter your Password:", type="password")
            if st.button("Verify"):
                cursor.execute("SELECT * FROM students WHERE student_id = %s AND password = %s", (user_id, password))
                student = cursor.fetchone()

                if not student:
                    st.error("Invalid Student ID or Password.")
                elif has_voted(user_id, election_id):
                    st.warning("You have already voted in this election.")
                else:
                    st.session_state.vote_verified = True
                    st.session_state.verified_user_id = user_id
                    st.success("ID Verified! You can now vote.")
        else:
            candidates = get_candidates_by_election(election_id)
            if candidates:
                candidate_dict = {c[2]: c[0] for c in candidates if c[2]}
                selected_name = st.radio("Select a candidate to vote for:", list(candidate_dict.keys()))

                if st.button("Submit Vote"):
                    candidate_id = candidate_dict.get(selected_name)
                    if candidate_id:
                        record_vote(st.session_state.verified_user_id, candidate_id, election_id)
                        st.session_state.vote_verified = False
                        st.session_state.verified_user_id = None
                        st.success("✅ Vote submitted successfully!")
                        st.session_state.menu = "Home"  # Redirect to Home menu
                    else:
                        st.error("Invalid candidate selection.")
            else:
                st.error("No candidates found for this election.")

# Registration
elif menu == "Registration":
    st.subheader("Register as Student or Admin")
    reg_type = st.selectbox("Register as", ["Student", "Admin"])

    if reg_type == "Student":
        sid = st.text_input("Student ID (max 20 chars)")
        name = st.text_input("Name")
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Register Student"):
            if sid and name and email and pw:
                if is_student_registered(sid):
                    st.error("Student ID already registered.")
                else:
                    register_student(sid[:20], name, email, pw)
                    st.success("Student registered successfully!")
            else:
                st.error("All fields are required.")

    elif reg_type == "Admin":
        uname = st.text_input("Username (max 20 chars)")
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        if st.button("Register Admin"):
            if uname and email and pw:
                cursor.execute("SELECT * FROM admins WHERE username = %s", (uname,))
                if cursor.fetchone():
                    st.error("Username already exists.")
                else:
                    register_admin(uname[:20], email, pw)
                    st.success("Admin registered successfully!")

# Admin
elif menu == "Admin":
    st.subheader("Admin Panel")

    if not st.session_state.logged_in:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_admin(u, p):
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Login failed.")
    else:
        st.success("Welcome, Admin!")
        admin_option = st.selectbox("Options", ["Create Election", "End Election"])

        if admin_option == "Create Election":
            name = st.text_input("Election Name")
            total = st.number_input("Total Number of Candidates", min_value=2, max_value=5, step=1)

            if "candidate_names" not in st.session_state or len(st.session_state.candidate_names) != total:
                st.session_state.candidate_names = ["" for _ in range(total)]

            for i in range(total):
                st.session_state.candidate_names[i] = st.text_input(f"Candidate {i+1} Name", value=st.session_state.candidate_names[i])

            if st.button("Start Election"):
                cursor.execute("UPDATE elections SET election_status = 'Ended' WHERE election_status = 'Active'")
                db.commit()
                cursor.execute("INSERT INTO elections (election_name, election_status) VALUES (%s, %s)", (name, 'Active'))
                db.commit()
                election_id = cursor.lastrowid

                for cname in st.session_state.candidate_names:
                    if cname.strip():
                        cursor.execute("INSERT INTO candidates (election_id, name, votes) VALUES (%s, %s, %s)", (election_id, cname.strip(), 0))
                db.commit()

                st.success(f"Election '{name}' created successfully!")

        elif admin_option == "End Election":
            active = get_active_election()
            if not active:
                st.warning("No active election.")
            else:
                election_id = active[0]
                election_name = active[1]

                cursor.execute("SELECT name, votes FROM candidates WHERE election_id = %s", (election_id,))
                for name, votes in cursor.fetchall():
                    cursor.execute(
                        "INSERT INTO election_results (election_id, election_name, candidate_name, votes) VALUES (%s, %s, %s, %s)",
                        (election_id, election_name, name, votes))

                cursor.execute("UPDATE elections SET election_status = 'Ended' WHERE election_id = %s", (election_id,))
                db.commit()

                cursor.execute("DELETE FROM candidates")
                db.commit()

                st.success("Election ended and results saved successfully!")
        
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.success("Logged out successfully!")
            st.rerun()

# Show Results
elif menu == "Show Results":
    st.subheader("Voting Results")

    cursor.execute("SELECT election_name, candidate_name, votes FROM election_results ORDER BY result_time DESC")
    results = cursor.fetchall()

    if not results:
        st.info("No election data available.")
    else:
        df = pd.DataFrame(results, columns=["Election", "Candidate", "Votes"])

        for election in df["Election"].unique():
            st.markdown(f"### 🗳️ {election}")
            election_df = df[df["Election"] == election]

            # Bar chart
            bar_chart = alt.Chart(election_df).mark_bar(size=20).encode(
                x=alt.X('Candidate:N', sort='-y'),
                y='Votes:Q',
                tooltip=['Candidate', 'Votes']
            ).properties(width=600, height=400)

            st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("---")
    st.markdown("### ⚠️ Admin Control: Clear Votes & Results")
    if st.checkbox("I want to clear all votes and results"):
        admin_user = st.text_input("Admin Username")
        admin_pass = st.text_input("Admin Password", type="password")
        
        if st.button("Confirm and Clear"):
            cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (admin_user, admin_pass))
            if cursor.fetchone():
                try:
                    cursor.execute("DELETE FROM cast_vote")
                    cursor.execute("DELETE FROM election_results")
                    db.commit()
                    st.success("✅ All votes and results have been cleared.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.error("❌ Invalid admin credentials.")
