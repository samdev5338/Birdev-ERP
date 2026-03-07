import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Birdev ERP", page_icon="🌐", layout="wide")

# 2. Futuristic CSS (Buttons aur Design ke liye)
st.markdown("""
    <style>
    /* Input box focus blue outline hatane ke liye */
    .stTextInput>div>div>input:focus {
        border-color: #1E3A8A !important;
        box-shadow: none !important;
    }
    /* Buttons ko 3D aur Futuristic banana */
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #312E81 100%);
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease 0s;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        background: linear-gradient(90deg, #312E81 0%, #1E3A8A 100%);
    }
    /* Metric Cards Style */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
    }
    /* Developer Box */
    .developer-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(30, 58, 138, 0.9);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        z-index: 1000;
        backdrop-filter: blur(5px);
    }
    </style>
    <div class="developer-box">👨‍💻 Developed by Samarth</div>
""", unsafe_allow_html=True)

# 3. Database Connection
def setup_db():
    conn = sqlite3.connect('birdev_erp_billing.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ProductMaster
                      (product TEXT, cost_price REAL, selling_price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS SalesHistory
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, bill_date TEXT,
                       product TEXT, quantity REAL, total_bill REAL, profit REAL)''')
    conn.commit()
    return conn

conn = setup_db()

# 4. Login System
st.sidebar.title("🔐 Admin Access")
password = st.sidebar.text_input("Enter Password", type="password")

if password == "332005":
    st.sidebar.success("Login Successful!")
    st.sidebar.markdown("---")
    
    # Navigation Menu
    menu_choice = st.sidebar.radio("Go to:", 
        ["🧾 Create Invoice", "📈 Business Analytics", "📜 Customer History", "⚙️ Manage Products"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("System Status: Online 🟢")

    # Main Header
    st.title("🏭 Birdev Udyog Samuha")
    st.markdown("##### Advanced Enterprise Resource Planning System")
    st.divider()

    # --- Menu 1: Billing ---
    if menu_choice == "🧾 Create Invoice":
        if 'cart' not in st.session_state:
            st.session_state['cart'] = []
            
        st.header("🛒 Billing / POS")
        df_p = pd.read_sql_query("SELECT product FROM ProductMaster", conn)
        product_list = df_p['product'].tolist()

        col_c1, col_c2 = st.columns(2)
        customer_name = col_c1.text_input("Customer Name", "Rakesh")
        bill_date = col_c2.date_input("Bill Date", datetime.date.today())

        col1, col2, col3 = st.columns([2, 1, 1])
        selected_p = col1.selectbox("Select Product", product_list)
        qty = col2.number_input("Qty (Kg)", min_value=1.0, value=1.0)
        
        if col3.button("➕ Add Item"):
            cursor = conn.cursor()
            cursor.execute("SELECT cost_price, selling_price FROM ProductMaster WHERE product=?", (selected_p,))
            res = cursor.fetchone()
            if res:
                cp, sp = res[0], res[1]
                st.session_state['cart'].append({
                    "Product": selected_p, "Quantity": qty, "Rate": sp, 
                    "Total Sales": sp * qty, "Profit": (sp - cp) * qty, "Cost": cp * qty
                })
        
        if st.session_state['cart']:
            df_cart = pd.DataFrame(st.session_state['cart'])
            st.table(df_cart[['Product', 'Quantity', 'Rate', 'Total Sales']])
            
            g_total = df_cart['Total Sales'].sum()
            g_profit = df_cart['Profit'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("Grand Total", f"₹{g_total}")
            c2.metric("Expected Profit", f"₹{g_profit}")

            if st.button("💾 Save Bill & Finish"):
                cursor = conn.cursor()
                for item in st.session_state['cart']:
                    cursor.execute("INSERT INTO SalesHistory (customer_name, bill_date, product, quantity, total_bill, profit) VALUES (?,?,?,?,?,?)",
                                 (customer_name, bill_date.strftime('%Y-%m-%d'), item['Product'], item['Quantity'], item['Total Sales'], item['Profit']))
                conn.commit()
                st.session_state['cart'] = []
                st.success("Bill Saved!")
                st.rerun()

    # --- Menu 2: Analytics ---
    elif menu_choice == "📈 Business Analytics":
        st.header("📈 Sales Analytics")
        df_s = pd.read_sql_query("SELECT * FROM SalesHistory", conn)
        if not df_s.empty:
            fig = px.pie(df_s, values='quantity', names='product', title='Sales Distribution', hole=0.3)
            st.plotly_chart(fig)
        else:
            st.warning("No data found!")

    # --- Menu 3: History ---
    elif menu_choice == "📜 Customer History":
        st.header("📜 Sales Records")
        df_h = pd.read_sql_query("SELECT * FROM SalesHistory ORDER BY id DESC", conn)
        st.dataframe(df_h, use_container_width=True)

    # --- Menu 4: Manage Products ---
    elif menu_choice == "⚙️ Manage Products":
        st.header("⚙️ Inventory Management")
        with st.form("Add Product"):
            p_name = st.text_input("Product Name")
            p_cp = st.number_input("Cost Price")
            p_sp = st.number_input("Selling Price")
            if st.form_submit_button("Save"):
                conn.cursor().execute("INSERT INTO ProductMaster VALUES (?,?,?)", (p_name, p_cp, p_sp))
                conn.commit()
                st.success("Product Added!")

else:
    # Jab tak password galat hai ya nahi dala
    st.title("🔒 Access Restricted")
    st.info("Please enter the correct admin password in the sidebar to unlock the system.")
    st.stop()

conn.close()
