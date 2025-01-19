import random
import sqlite3
import datetime
import streamlit as st

# Initialize SQLite database
def initialize_database():
    conn = sqlite3.connect('iin_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            iin TEXT PRIMARY KEY,
            name TEXT,
            dob TEXT,
            nationality TEXT,
            sex TEXT,
            marital_status TEXT,
            education TEXT,
            qualification TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Update database schema to ensure all required columns exist
def update_database_schema():
    conn = sqlite3.connect('iin_database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN sex TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN marital_status TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN education TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN qualification TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

# Generate IIN
def generate_iin(nationality):
    if len(nationality) < 2:
        raise ValueError("Nationality must be at least 2 characters long.")
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(10)])  # Generate a 10-digit random number
    country_code = nationality[:2].upper()  # Use first 2 letters of nationality
    iin = f"{country_code}{random_part}"
    return iin

# Store user data
def store_user(iin, name, dob, nationality, sex, marital_status, education, qualification):
    try:
        conn = sqlite3.connect('iin_database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE iin = ?', (iin,))
        existing_user = cursor.fetchone()
        if existing_user:
            st.error("User has already been registered.")
            return False
        cursor.execute('''
            INSERT INTO users (iin, name, dob, nationality, sex, marital_status, education, qualification) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (iin, name, dob, nationality, sex, marital_status, education, qualification))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error storing user data: {e}")
        return False
    try:
        conn = sqlite3.connect('iin_database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (iin, name, dob, nationality, sex, marital_status, education, qualification) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (iin, name, dob, nationality, sex, marital_status, education, qualification))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error storing user data: {e}")
        return False

# Retrieve user data
def retrieve_user(iin):
    conn = sqlite3.connect('iin_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE iin = ?', (iin,))
    user = cursor.fetchone()
    conn.close()
    if user is None or len(user) < 8:
        return None  # Handle incomplete or missing records
    return user

# Get last 5 users (history)
def get_last_5_users():
    conn = sqlite3.connect('iin_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY rowid DESC LIMIT 5')
    users = cursor.fetchall()
    conn.close()
    return users

# Delete user data
def delete_user(iin):
    try:
        conn = sqlite3.connect('iin_database.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE iin = ?', (iin,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting user data: {e}")
        return False

# Streamlit App
initialize_database()
update_database_schema()
st.title("International Identity Number (IIN) System")

menu = st.sidebar.selectbox("Menu", ["Register User", "Retrieve User", "View History"])

if menu == "Register User":
    st.subheader("Register a New User")
    with st.form("register_form"):
        name = st.text_input("Name")
        dob = st.date_input(
    "Date of Birth",
    value=None,
    min_value=datetime.date(1925, 1, 1),
    max_value=datetime.date.today()
)
        nationality = st.text_input("Nationality (e.g., India, UAE)")
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        marital_status = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed"])
        education = st.text_input("Education Level")
        qualification = st.text_input("Professional Qualification")
        submit = st.form_submit_button("Register")

        if submit:
            if name and dob and nationality and sex and marital_status and education and qualification:
                dob_str = dob.strftime('%Y-%m-%d')
                try:
                    iin = generate_iin(nationality)
                    if store_user(iin, name, dob_str, nationality, sex, marital_status, education, qualification):
                        st.success(f"User Registered Successfully! IIN: {iin}")
                    else:
                        st.error("Failed to register user.")
                except ValueError as e:
                    st.error(str(e))
            else:
                st.error("Please fill in all fields.")

elif menu == "Retrieve User":
    st.subheader("Retrieve User by IIN")
    with st.form("retrieve_form"):
        iin = st.text_input("Enter IIN")
        retrieve = st.form_submit_button("Retrieve")

        if retrieve:
            if iin:
                user = retrieve_user(iin)
                if user:
                    st.write(f"**IIN**: {user[0]}")
                    st.write(f"**Name**: {user[1]}")
                    st.write(f"**Date of Birth**: {user[2]}")
                    st.write(f"**Nationality**: {user[3]}")
                    st.write(f"**Sex**: {user[4]}")
                    st.write(f"**Marital Status**: {user[5]}")
                    st.write(f"**Education Level**: {user[6]}")
                    st.write(f"**Professional Qualification**: {user[7]}")
                else:
                    st.error("IIN not found or data is incomplete.")
            else:
                st.error("Please enter an IIN.")

elif menu == "View History":
    users = get_last_5_users()
    if users:
        for user in users:
            if len(user) == 8:
                st.write(f"**IIN**: {user[0]}")
                st.write(f"**Name**: {user[1]}")
                st.write(f"**Date of Birth**: {user[2]}")
                st.write(f"**Nationality**: {user[3]}")
                st.write(f"**Sex**: {user[4]}")
                st.write(f"**Marital Status**: {user[5]}")
                st.write(f"**Education Level**: {user[6]}")
                st.write(f"**Professional Qualification**: {user[7]}")
                delete = st.button(f"Delete {user[0]}", key=user[0])
                if delete:
                    if delete_user(user[0]):
                        st.success(f"User with IIN {user[0]} deleted successfully.")
                        st.session_state['refresh'] = True
                    else:
                        st.error("Failed to delete user.")
                st.write("---")
