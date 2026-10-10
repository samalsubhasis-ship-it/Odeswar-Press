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
            order_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            category TEXT,
            item TEXT,
            delivery_status TEXT,
            notes TEXT
        )
    """
    )
    
    # Ensure all columns exist in the database schema dynamically
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    
    upgrades = {
        "order_id": "ALTER TABLE customers ADD COLUMN order_id TEXT",
        "category": "ALTER TABLE customers ADD COLUMN category TEXT",
        "item": "ALTER TABLE customers ADD COLUMN item TEXT",
        "delivery_status": "ALTER TABLE customers ADD COLUMN delivery_status TEXT"
    }
    
    for col_name, alter_query in upgrades.items():
        if col_name not in columns:
            cursor.execute(alter_query)

    conn.commit()
    conn.close()


def add_customer(order_id, name, email, phone, category, item, delivery_status, notes):
    """Inserts a new customer order record into the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO customers 
               (order_id, name, email, phone, category, item, delivery_status, notes) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_id, name, email, phone, category, item, delivery_status, notes),
        )
        conn.commit()
        conn.close()
        return True, "Order successfully created!"
    except sqlite3.IntegrityError:
        return False, "Error: This Order ID already exists."
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_customers(search_query=""):
    """Retrieves records from the customer table, optionally filtered by search."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if search_query:
        query = """
            SELECT id, order_id, name, email, phone, category, item, delivery_status, notes FROM customers 
            WHERE order_id LIKE ? OR name LIKE ? OR email LIKE ? OR phone LIKE ? 
               OR category LIKE ? OR item LIKE ? OR delivery_status LIKE ? OR notes LIKE ?
        """
        search_pattern = f"%{search_query}%"
        cursor.execute(
            query,
            (search_pattern, search_pattern, search_pattern, search_pattern,
             search_pattern, search_pattern, search_pattern, search_pattern),
        )
    else:
        cursor.execute(
            "SELECT id, order_id, name, email, phone, category, item, delivery_status, notes FROM customers"
        )

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_customer(customer_id):
    """Deletes an order record based on the ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return True, "Record successfully deleted!"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ==========================================
# 2. STREAMLIT INTERFACE
# ==========================================
# Initialize database structural checks
init_db()

st.set_page_config(page_title="Customer Order Management", layout="wide")
st.title("👥 Odeswar Press Customer & Order DB")

# Creating layout tabs
tab1, tab2 = st.tabs(["➕ Create New Order", "🔍 View & Search Directory"])

# --- TAB 1: ADD NEW ORDER ---
with tab1:
    st.header("Register a New Order")

    # Generate an automated unique Order ID based on the current timestamp
    auto_order_id = datetime.now().strftime("ORD-%Y%m%d-%H%M%S")

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            # Displayed as disabled so users know it is auto-managed
            order_id = st.text_input("Order ID (Auto-Generated)", value=auto_order_id, disabled=True)
            name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email Address*", placeholder="john@example.com")
            phone = st.text_input("Phone Number", placeholder="+1 (555) 019-2834")

        with col2:
            category_selection = st.selectbox(
                "Customer Category",
                ["VIP", "Regular", "Lead", "Inactive", "Other"],
                index=1,
            )

            item_selection = st.selectbox(
                "Sales Item",
                ["Banner", "Cup/Cap/Tshirt", "Photo", "ID-Card", "Other"],
                index=1,
            )
            
            status_selection = st.selectbox(
                "Delivery Status",
                ["ordered", "in-progress", "pending", "delivered", "received", "payment issue", "completed"],
                index=0,
            )

            if category_selection == "Other":
                final_category = st.text_input("Please specify customer category:")
            else:
                final_category = category_selection

            notes = st.text_area(
                "Internal Account & Order Notes",
                placeholder="Enter item sizes, text details, or billing statuses...",
            )

        submit_btn = st.button("Submit Order", type="primary")

        if submit_btn:
            if not name or not email:
                st.error("Please fill out all mandatory fields (*).")
            elif category_selection == "Other" and (not final_category or not final_category.strip()):
                st.error("Please enter a manual category name.")
            else:
                success, message = add_customer(
                    order_id, name, email, phone, final_category, item_selection, status_selection, notes
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# --- TAB 2: VIEW & SEARCH DIRECTORY ---
with tab2:
    st.header("Search and Explore Records")

    search_input = st.text_input(
        "Search records by Order ID, Name, Email, Phone, Category, Item, or Status",
        placeholder="Type to filter...",
    )

    customers = get_all_customers(search_input)

    if not customers:
        st.info("No matching customer or order records found.")
    else:
        for row in customers:
            c_id, c_oid, c_name, c_email, c_phone, c_category, c_item, c_status, c_notes = row

            with st.container(border=True):
                info_col, action_col = st.columns([4, 1])

                with info_col:
                    category_badge = {
                        "VIP": "🔴 VIP",
                        "Regular": "🟢 Regular",
                        "Lead": "🔵 Lead",
                        "Inactive": "⚪ Inactive",
                    }.get(c_category, f"🟠 {c_category}")

                    # Status color coding system
                    status_badge = {
                        "ordered": "📦 ordered",
                        "in-progress": "⚡ in-progress",
                        "pending": "⏳ pending",
                        "delivered": "🚚 delivered",
                        "received": "🤝 received",
                        "payment issue": "⚠️ payment issue",
                        "completed": "✅ completed"
                    }.get(c_status, c_status)

                    st.markdown(f"### {c_name} | {category_badge} | `{c_oid}`")

                    det_col1, det_col2, det_col3, det_col4 = st.columns(4)
                    det_col1.markdown(f"**📧 Email:** {c_email}")
                    det_col2.markdown(f"**📞 Phone:** {c_phone if c_phone else 'N/A'}")
                    det_col3.markdown(f"**🛍️ Product:** `{c_item}`")
                    det_col4.markdown(f"**📊 Status:** {status_badge}")

                    if c_notes:
                        st.markdown(f"**📝 Notes:** {c_notes}")

                with action_col:
                    st.write("")
                    st.write("")
                    if st.button("Delete Order", key=f"del_{c_id}", type="primary"):
                        success, message = delete_customer(c_id)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
