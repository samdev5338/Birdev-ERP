import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Birdev ERP", page_icon="🌐", layout="wide")

# 2. Futuristic CSS
st.markdown("""
    <style>
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #312E81 100%);
        color: white; border-radius: 8px; border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;
        font-weight: bold; width: 100%; height: 3em;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .developer-box {
        position: fixed; bottom: 20px; right: 20px;
        background: rgba(30, 58, 138, 0.9); color: white;
        padding: 10px 20px; border-radius: 8px; font-weight: bold;
        z-index: 1000; backdrop-filter: blur(5px);
    }
    </style>
    <div class="developer-box">👨‍💻 Developed by Samarth</div>
""", unsafe_allow_html=True)

# 3. Database Setup
def setup_db():
    conn = sqlite3.connect('birdev_erp_billing.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ProductMaster (product TEXT, cost_price REAL, selling_price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS SalesHistory (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, bill_date TEXT, product TEXT, quantity REAL, total_bill REAL, profit REAL)''')
    conn.commit()
    return conn

conn = setup_db()

# 4. Login System
st.sidebar.title("🔐 Admin Access")
password = st.sidebar.text_input("Enter Password", type="password")

if password == "332005":
    st.sidebar.success("Login Successful!")
    menu_choice = st.sidebar.radio("Go to:", ["🧾 Create Invoice", "📈 Business Analytics", "📜 Customer History", "⚙️ Manage Products"])
    
    st.title("🏭 Birdev Udyog Samuha")
    st.divider()

    # --- Menu 1: Billing (Stylish PDF included) ---
    if menu_choice == "🧾 Create Invoice":
        if 'cart' not in st.session_state: st.session_state['cart'] = []
        st.header("🛒 Create New Bill")
        df_p = pd.read_sql_query("SELECT product FROM ProductMaster", conn)
        product_list = df_p['product'].tolist()

        col_c1, col_c2 = st.columns(2)
        customer_name = col_c1.text_input("Customer Name", "Walking Customer")
        bill_date = col_c2.date_input("Bill Date", datetime.date.today())

        col1, col2, col3 = st.columns([2, 1, 1])
        selected_p = col1.selectbox("Select Product", product_list)
        qty = col2.number_input("Qty (Kg)", min_value=0.1, value=1.0)
        
        if col3.button("➕ Add Item"):
            cursor = conn.cursor()
            cursor.execute("SELECT cost_price, selling_price FROM ProductMaster WHERE product=?", (selected_p,))
            res = cursor.fetchone()
            if res:
                st.session_state['cart'].append({"Product": selected_p, "Quantity": qty, "Rate": res[1], "Total": res[1]*qty, "Profit": (res[1]-res[0])*qty})
        
        if st.session_state['cart']:
            df_cart = pd.DataFrame(st.session_state['cart'])
            st.table(df_cart[['Product', 'Quantity', 'Rate', 'Total']])
            g_total = df_cart['Total'].sum()

            if st.button("💾 SAVE BILL & GENERATE PDF"):
                cursor = conn.cursor()
                for item in st.session_state['cart']:
                    cursor.execute("INSERT INTO SalesHistory (customer_name, bill_date, product, quantity, total_bill, profit) VALUES (?,?,?,?,?,?)",
                                 (customer_name, bill_date.strftime('%Y-%m-%d'), item['Product'], item['Quantity'], item['Total'], item['Profit']))
                conn.commit()

                # PDF Logic
                pdf = FPDF()
                pdf.add_page()
                pdf.set_fill_color(30, 58, 138); pdf.rect(0, 0, 210, 40, 'F')
                pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 24)
                pdf.cell(190, 20, "BIRDEV UDYOG SAMUHA", ln=True, align='C')
                pdf.ln(20); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
                pdf.cell(100, 10, f"Customer: {customer_name}"); pdf.cell(90, 10, f"Date: {bill_date}", ln=True, align='R')
                pdf.ln(5); pdf.set_fill_color(230, 230, 230); pdf.cell(80, 10, " Product", 1, 0, 'L', True); pdf.cell(30, 10, "Qty", 1, 0, 'C', True); pdf.cell(40, 10, "Rate", 1, 0, 'C', True); pdf.cell(40, 10, "Total", 1, 1, 'C', True)
                for item in st.session_state['cart']:
                    pdf.cell(80, 10, f" {item['Product']}", 1); pdf.cell(30, 10, str(item['Quantity']), 1, 0, 'C'); pdf.cell(40, 10, str(item['Rate']), 1, 0, 'C'); pdf.cell(40, 10, str(item['Total']), 1, 1, 'C')
                pdf.set_font("Arial", 'B', 12); pdf.set_fill_color(30, 58, 138); pdf.set_text_color(255, 255, 255)
                pdf.cell(150, 12, "GRAND TOTAL  ", 1, 0, 'R', True); pdf.cell(40, 12, f"Rs {g_total}/- ", 1, 1, 'C', True)
                
                pdf_output = f"Invoice_{customer_name}.pdf"
                pdf.output(pdf_output)
                with open(pdf_output, "rb") as f:
                    st.download_button("📥 DOWNLOAD INVOICE", f, file_name=pdf_output)
                st.session_state['cart'] = []; st.success("Saved!")

    # --- Menu 3: Customer History ---
    elif menu_choice == "📜 Customer History":
        st.header("📜 Sales Records")
        df_h = pd.read_sql_query("SELECT * FROM SalesHistory ORDER BY id DESC", conn)
        st.dataframe(df_h, use_container_width=True, hide_index=True)

    # --- Menu 4: Manage Products (DELETE OPTION ADDED HERE) ---
    elif menu_choice == "⚙️ Manage Products":
        st.header("⚙️ Product Inventory Management")
        
        col_m1, col_m2 = st.columns([1, 1])
        
        with col_m1:
            st.subheader("➕ Add New Product")
            with st.form("AddForm", clear_on_submit=True):
                new_p = st.text_input("Product Name")
                new_c = st.number_input("Cost Price (Lagaat)", min_value=0.0)
                new_s = st.number_input("Selling Price (Rate)", min_value=0.0)
                if st.form_submit_button("Save Product"):
                    if new_p:
                        conn.cursor().execute("INSERT INTO ProductMaster VALUES (?,?,?)", (new_p, new_c, new_s))
                        conn.commit()
                        st.success(f"{new_p} added!")
                        st.rerun()

        with col_m2:
            st.subheader("🗑️ Delete Product")
            df_view = pd.read_sql_query("SELECT product FROM ProductMaster", conn)
            if not df_view.empty:
                prod_to_del = st.selectbox("Select Product to Remove", df_view['product'].tolist())
                if st.button("❌ Delete Permanently"):
                    conn.cursor().execute("DELETE FROM ProductMaster WHERE product=?", (prod
