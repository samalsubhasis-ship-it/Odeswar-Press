import sqlite3
import streamlit as st

# ==========================================
# 1. DATABASE SETUP & FUNCTIONS
# ==========================================
DB_NAME = "customers.db"


def init_db():
    """Creates the customer table if it does not exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            notes TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def add_customer(name, email, phone, notes):
    """Inserts a new customer record into the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, email, phone, notes) VALUES (?, ?, ?, ?)",
            (name, email, phone, notes),
        )
        conn.commit()
        conn.close()
        return True, "Customer successfully added!"
    except sqlite3.IntegrityError:
        return False, "Error: A customer with this email already exists."
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_customers():
    """Retrieves all records from the customer table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, notes FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Initialize database table on app start
init_db()

# ==========================================
# 2. STREAMLIT WEB APP INTERFACE
# ==========================================
st.set_page_config(page_title="Customer Database Entry", layout="wide")

st.title("👥 ODESWAR PRESS")
st.markdown("Enter customer details below to save them directly to the database.")

# Create two columns layout: left for data entry, right for viewing records
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 New Customer Form")

    # Wrap inputs inside a form component
    with st.form(key="customer_form", clear_on_submit=True):
        name = st.text_input("Full Name *", placeholder="John Doe")
        email = st.text_input("Email Address *", placeholder="john@example.com")
        phone = st.text_input("Phone Number", placeholder="+1 (555) 019-2834")
        notes = st.text_area(
            "Internal Notes", placeholder="Additional context..."
        )

        submit_button = st.form_submit_button(label="Save Customer")

    # Handle form submission logic
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

    # Fetch records and display them
    records = get_all_customers()

    if not records:
        st.info("No records found in the database yet.")
    else:
        # Convert raw tuples to a displayable list of dictionaries
        formatted_data = [
            {
                "ID": row[0],
                "Name": row[1],
                "Email": row[2],
                "Phone": row[3],
                "Notes": row[4],
            }
            for row in records
        ]

        # Display raw table with built-in search and filtering features
        st.dataframe(formatted_data, use_container_width=True, hide_index=True)

        # Quick metric block
        st.metric(label="Total Customers Registered", value=len(records))
