from datetime import datetime
import sqlite3
import streamlit as st

# ==========================================
# 1. DATABASE SETUP & FUNCTIONS
# ==========================================
DB_NAME = "customers.db"


def init_db():
    """Creates the customer table if it does not exist and ensures structural upgrades."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            category TEXT,
            notes TEXT
        )
    """
    )
    # Ensure category column exists in the database schema
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    if "category" not in columns:
        cursor.execute("ALTER TABLE customers ADD COLUMN category TEXT")

    conn.commit()
    conn.close()


def add_customer(name, email, phone, category, notes):
    """Inserts a new customer record into the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, email, phone, category, notes) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, category, notes),
        )
        conn.commit()
        conn.close()
        return True, "Customer successfully added!"
    except sqlite3.IntegrityError:
        return False, "Error: A customer with this email already exists."
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_customers(search_query=""):
    """Retrieves records from the customer table, optionally filtered by search."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if search_query:
        query = """
            SELECT id, name, email, phone, category, notes FROM customers 
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR category LIKE ? OR notes LIKE ?
        """
        search_pattern = f"%{search_query}%"
        cursor.execute(
            query,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
            ),
        )
    else:
        cursor.execute(
            "SELECT id, name, email, phone, category, notes FROM customers"
        )

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_customer(customer_id):
    """Deletes a customer record based on the ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return True, "Customer successfully deleted!"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ==========================================
# 2. STREAMLIT INTERFACE
# ==========================================
# Initialize the database on application start
init_db()

st.set_page_config(page_title="Customer Directory Management", layout="wide")
st.title("👥 Odeswar Press Customer-DB")

# Creating layout tabs
tab1, tab2 = st.tabs(["➕ Add New Customer", "🔍 View & Search Directory"])

# --- TAB 1: ADD NEW CUSTOMER ---
with tab1:
    st.header("Register a New Customer")

    # To create dynamic visibility, we use a standard container instead of st.form
    # because st.form blocks immediate UI reactivity based on intermediate inputs.
    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email Address*", placeholder="john@example.com")
            phone = st.text_input("Phone Number", placeholder="+1 (555) 019-2834")

        with col2:
              # Added "Other" to the Customer Category dropdown selection
           category_selection = st.selectbox(
               "Customer Category",
               ["VIP", "Regular", "Lead", "Inactive", "Other"],
               index=1,
    ) # <--- Added missing closing parenthesis

    # Added "Other" to the Sales Item dropdown selection
           item_selection = st.selectbox(
             "Sales Item",
             ["Banner", "Cup/Cap/Tshirt", "Photo", "ID-Card", "Other"],
             index=1,
    ) # Changed variable name to avoid overwriting

            
            # Dynamically display manual text input box if "Other" is chosen
          if category_selection == "Other":
                final_category = st.text_input("Specify Other Category*", placeholder="Enter manual category type...")
            else:
                final_category = category_selection

            notes = st.text_area(
                "Internal Account Notes",
                placeholder="Enter background details, preferences, or transaction history...",
            )

        submit_btn = st.button("Add Customer", type="primary")

        if submit_btn:
            if not name or not email:
                st.error("Please fill out all mandatory fields (*).")
            elif category_selection == "Other" and not final_category.strip():
                st.error("Please enter a manual category name.")
            else:
                success, message = add_customer(name, email, phone, final_category, notes)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# --- TAB 2: VIEW & SEARCH DIRECTORY ---
with tab2:
    st.header("Search and Explore Records")

    # Search Bar Interface
    search_input = st.text_input(
        "Search records by Name, Email, Phone, Category, or Notes",
        placeholder="Type to filter...",
    )

    # Fetch records based on search query
    customers = get_all_customers(search_input)

    if not customers:
        st.info("No matching customer records found.")
    else:
        # Dynamically generate list layout with metrics and delete options
        for row in customers:
            c_id, c_name, c_email, c_phone, c_category, c_notes = row

            # Design a clean card layout for each entry
            with st.container(border=True):
                info_col, action_col = st.columns([4, 1])

                with info_col:
                    # Category Badge styling support mapping
                    badge_color = {
                        "VIP": "🔴 VIP",
                        "Regular": "🟢 Regular",
                        "Lead": "🔵 Lead",
                        "Inactive": "⚪ Inactive",
                    }.get(c_category, f"🟠 {c_category}") # Fallback to handle custom manual categories nicely

                    st.markdown(f"### {c_name} | {badge_color}")

                    # Detailed contact alignment
                    det_col1, det_col2 = st.columns(2)
                    det_col1.markdown(f"**📧 Email:** {c_email}")
                    det_col2.markdown(f"**📞 Phone:** {c_phone if c_phone else 'N/A'}")

                    if c_notes:
                        st.markdown(f"**📝 Notes:** {c_notes}")

                with action_col:
                    # Vertical separation for action elements
                    st.write("")
                    st.write("")
                    # Unique key binding for dynamic delete loops
                    if st.button(
                        "Delete Record", key=f"del_{c_id}", type="primary"
                    ):
                        success, message = delete_customer(c_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
