import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

# ==========================================
# 1. DATABASE CONNECTIVITY
# ==========================================
# On local machine, it reads from environment variable.
# On Streamlit Cloud, it reads from the "Secrets" manager.
DB_URL = st.secrets.get(
    "DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "PASTE_YOUR_SUPABASE_CONNECTION_STRING_HERE_FOR_LOCAL_TESTING",
    ),
)

import streamlit as st

# Automatically securely initializes connections using the dashboard secrets
conn = st.connection("postgresql", type="sql")

# Perform your queries safely
df = conn.query("SELECT * FROM your_table_name;", ttl="10m")


def get_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(DB_URL)


def init_db():
    """Creates the customer table if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            notes TEXT
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


def add_customer(name, email, phone, notes):
    """Inserts a new customer record into the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, email, phone, notes) VALUES (%s, %s, %s, %s)",
            (name, email, phone, notes),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Customer successfully added!"
    except psycopg2.errors.UniqueViolation:
        return False, "Error: A customer with this email already exists."
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_customers():
    """Retrieves all records from the customer table."""
    conn = get_connection()
    # RealDictCursor returns rows as dictionaries, perfect for DataFrames
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, name, email, phone, notes FROM customers")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# Initialize database table on app start
init_db()

# ==========================================
# 2. STREAMLIT WEB APP INTERFACE
# ==========================================
st.set_page_config(page_title="Customer Database Entry", layout="wide")

st.title("👥 Cloud Customer Database Entry Portal")
st.markdown("Enter customer details below to save them securely to Supabase.")

col1, col2 = st.columns()

with col1:
    st.subheader("📝 New Customer Form")

    with st.form(key="customer_form", clear_on_submit=True):
        name = st.text_input("Full Name *", placeholder="John Doe")
        email = st.text_input("Email Address *", placeholder="john@example.com")
        phone = st.text_input("Phone Number", placeholder="+1 (555) 019-2834")
        notes = st.text_area(
            "Internal Notes", placeholder="Additional context..."
        )

        submit_button = st.form_submit_button(label="Save Customer")

    if submit_button:
        if not name or not email:
            st.error("Fields marked with an asterisk (*) are required.")
        else:
            success, message = add_customer(name, email, phone, notes)
            if success:
                st.success(message)
            else:
                st.error(message)

with col2:
    st.subheader("🗄️ Database Records")

    try:
        records = get_all_customers()
        if not records:
            st.info("No records found in the database yet.")
        else:
            # Custom column mapping for clean presentation
            formatted_data = [
                {
                    "ID": row["id"],
                    "Name": row["name"],
                    "Email": row["email"],
                    "Phone": row["phone"],
                    "Notes": row["notes"],
                }
                for row in records
            ]
            st.dataframe(
                formatted_data, use_container_width=True, hide_index=True
            )
            st.metric(label="Total Customers Registered", value=len(records))
    except Exception as e:
        st.error(f"Failed to fetch records: {e}")
