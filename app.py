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
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col for col in cursor.fetchall()]
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
        like_str = f"%{search_query}%"
        cursor.execute(
            query, (like_str, like_str, like_str, like_str, like_str)
        )
    else:
        cursor.execute(
            "SELECT id, name, email, phone, category, notes FROM customers"
        )

    rows = cursor.fetchall()
    conn.close()
    return rows


# Initialize database table on app start

if "success_message" not in st.session_state:
    st.session_state.success_message = None

# ==========================================
# 2. STREAMLIT WEB APP INTERFACE
# ==========================================
st.set_page_config(page_title="Customer Database Entry", layout="wide")

# Inject Custom CSS for grey background, stylized inputs, and shining text animation
st.markdown(
    """
    <style>
    /* Change primary app background to grey */
    .stApp {
        background-color: #ECECEC;
    }
    
    /* Styling for the Shining header text */
    .shining-text {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #ff005b, #00d2ff, #ff005b);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        padding-bottom: 10px;
    }
    
    @keyframes shine {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    
    /* Card borders wrapper */
    .form-container {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- TOP BADGE: SHINING TEXT BANNER ---
st.markdown(
    '<div class="shining-text">⭐️ SERVICE SINCE 2016 ⭐️</div>',
    unsafe_allow_html=True,
)

# Header Section with Title & Dynamic Clock
col_title, col_clock = st.columns([2, 1])
with col_title:
    st.title("👥 Odeswar Press")
with col_clock:
    current_time = datetime.now().strftime("%Y-%m-%d | %I:%M:%S %p")
    st.markdown(
        f"<div style='text-align: right; padding-top: 20px; font-weight: bold; color: #555555;'>🕒 {current_time}</div>",
        unsafe_allow_html=True,
    )

# --- VISUAL BORDERS: DECORATIVE PRINT IMAGES (LEFT AND RIGHT) ---
# Wrapping layout columns to place thematic images around the data panels
left_img_col, main_content_col, right_img_col = st.columns([1, 4, 1])

with left_img_col:
    # Decorative print layout illustration (Left border side)
    st.image(
        "https://dreamstime.com",
        caption="Production Press",
        use_container_width=True,
    )
    st.image(
        "https://pinterest.com",
        use_container_width=True,
    )

with right_img_col:
    # Decorative graphic banner illustration (Right border side)
    st.image(
        "https://indiamart.com",
        caption="Graphic Hub",
        use_container_width=True,
    )
    st.image(
        "https://indiamart.com",
        use_container_width=True,
    )

# --- MIDDLE APPLICATION WORKSPACE ---
with main_content_col:
    st.markdown(
        "Enter customer details below or switch tabs to manage records."
    )

    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    # Tab navigation container
    tab1, tab2 = st.tabs(["📝 Add New Customer", "🗄️ View Database Records"])

    # --- TAB 1: ADD NEW CUSTOMER FORM ---
    with tab1:
        st.subheader("New Customer Details")

        with st.form(key="customer_form", clear_on_submit=True):
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input(
                "Email Address *", placeholder="john@example.com"
            )
            phone = st.text_input(
                "Phone Number", placeholder="+1 (555) 019-2834"
            )

            category_options = [
                "General Customer",
                "VIP/Premium",
                "Wholesale/Corporate",
                "Inbound Lead",
                "Inactive",
            ]
            category = st.selectbox(
                "Customer Segment", options=category_options
            )
            notes = st.text_area(
                "Internal Notes", placeholder="Additional context..."
            )

            submit_button = st.form_submit_button(label="Save Customer")

        if submit_button:
            if not name or not email:
                st.error("Fields marked with an asterisk (*) are required.")
            else:
                success, message = add_customer(
                    name, email, phone, category, notes
                )
                if success:
                    st.session_state.success_message = message
                    st.rerun()
                else:
                    st.error(message)

    # --- TAB 2: DATABASE VIEW AND SEARCH ---
    with tab2:
        st.subheader("Database Records")

        search_input = st.text_input(
            "🔍 Search Customers",
            placeholder="Type a name, email, category, or keyword and press enter...",
        )

        records = get_all_customers(search_input)

        if not records:
            if search_input:
                st.warning(f"No records found matching: '{search_input}'")
            else:
                st.info("No records found in the database yet.")
        else:
            formatted_data = [
                {
                    "ID": row,
                    "Name": row,
                    "Email": row,
                    "Phone": row,
                    "Category": row,
                    "Notes": row,
                }
                for row in records
            ]

            st.dataframe(
                formatted_data, use_container_width=True, hide_index=True
            )
            st.metric(label="Total Records Displayed", value=len(records))