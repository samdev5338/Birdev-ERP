import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Birdev ERP", page_icon="🌐", layout="wide")

# 2. Futuristic CSS
st.markdown("""
    <style>
    .stTextInput>div>div>input:focus { border-color: #1E3A8A !important; box-shadow: none !important; }
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #312E81 100%);
        color: white; border-radius: 8px; border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 15px; border-radius: 10px; border-left: 5px solid #1E3A8A;
    }
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
    menu_choice = st.sidebar.radio("Go to:", 
        ["🧾 Create Invoice", "📈 Business Analytics", "📜 Customer History", "⚙️ Manage Products"])
    
    st.title("🏭 Birdev Udyog Samuha")
    st.divider()

    # --- Menu 1: Billing ---
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
                cp, sp = res[0], res[1]
                st.session_state['cart'].append({
                    "Product": selected_p, "Quantity": qty, "Rate": sp, 
                    "Total Sales": sp * qty, "Profit": (sp - cp) * qty})
        
        if st.session_state['cart']:
            df_cart = pd.DataFrame(st.session_state['cart'])
            st.table(df_cart[['Product', 'Quantity', 'Rate', 'Total Sales']])
            
            g_total = df_cart['Total Sales'].sum()
            
            if st.button("💾 Save Bill & Get PDF"):
                cursor = conn.cursor()
                for item in st.session_state['cart']:
                    cursor.execute("INSERT INTO SalesHistory (customer_name, bill_date, product, quantity, total_bill, profit) VALUES (?,?,?,?,?,?)",
                                 (customer_name, bill_date.strftime('%Y-%m-%d'), item['Product'], item['Quantity'], item['Total Sales'], item['Profit']))
                conn.commit()

                # Bill PDF Generation
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA - INVOICE", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(200, 10, f"Customer: {customer_name} | Date: {bill_date}", ln=True, align='C')
                pdf.ln(10)
                pdf.cell(80, 10, "Product", 1); pdf.cell(30, 10, "Qty", 1); pdf.cell(40, 10, "Rate", 1); pdf.cell(40, 10, "Total", 1, 1)
                for item in st.session_state['cart']:
                    pdf.cell(80, 10, item['Product'], 1); pdf.cell(30, 10, str(item['Quantity']), 1); pdf.cell(40, 10, str(item['Rate']), 1); pdf.cell(40, 10, str(item['Total Sales']), 1, 1)
                pdf.cell(150, 10, "Grand Total", 1); pdf.cell(40, 10, f"Rs {g_total}", 1, 1)
                
                pdf_name = f"Bill_{customer_name}.pdf"
                pdf.output(pdf_name)
                with open(pdf_name, "rb") as f:
                    st.download_button("📥 Download This Bill", f, file_name=pdf_name)
                st.session_state['cart'] = []
                st.success("Bill Saved!")

    # --- Menu 2: Analytics ---
    elif menu_choice == "📈 Business Analytics":
        st.header("📈 Sales Overview")
        df_s = pd.read_sql_query("SELECT * FROM SalesHistory", conn)
        if not df_s.empty:
            st.plotly_chart(px.bar(df_s, x='product', y='total_bill', color='product', title="Sales by Product"))
        else: st.warning("No data yet.")

    # --- Menu 3: Customer History (Full PDF Download Here) ---
    elif menu_choice == "📜 Customer History":
        st.header("📜 All Sales Records")
        df_h = pd.read_sql_query("SELECT * FROM SalesHistory ORDER BY id DESC", conn)
        
        if not df_h.empty:
            # Full Report PDF Generator
            if st.button("📥 Download Full Sales Report (PDF)"):
                pdf_report = FPDF()
                pdf_report.add_page()
                pdf_report.set_font("Arial", 'B', 14)
                pdf_report.cell(200, 10, "BIRDEV UDYOG - COMPLETE SALES REPORT", ln=True, align='C')
                pdf_report.ln(5)
                pdf_report.set_font("Arial", 'B', 10)
                # Table Headers
                pdf_report.cell(25, 10, "Date", 1); pdf_report.cell(45, 10, "Customer", 1); pdf_report.cell(45, 10, "Product", 1); pdf_report.cell(20, 10, "Qty", 1); pdf_report.cell(30, 10, "Total Bill", 1); pdf_report.cell(25, 10, "Profit", 1, 1)
                pdf_report.set_font("Arial", '', 9)
                for i, row in df_h.iterrows():
                    pdf_report.cell(25, 10, str(row['bill_date']), 1); pdf_report.cell(45, 10, str(row['customer_name'])[:20], 1); pdf_report.cell(45, 10, str(row['product']), 1); pdf_report.cell(20, 10, str(row['quantity']), 1); pdf_report.cell(30, 10, str(row['total_bill']), 1); pdf_report.cell(25, 10, str(row['profit']), 1, 1)
                
                report_name = "Full_Sales_Report.pdf"
                pdf_report.output(report_name)
                with open(report_name, "rb") as f:
                    st.download_button("💾 Click to Download Full Report", f, file_name=report_name)

            st.dataframe(df_h, use_container_width=True)
        else: st.info("No records found.")

    # --- Menu 4: Manage Products ---
    elif menu_choice == "⚙️ Manage Products":
        st.header("⚙️ Product Inventory")
        with st.form("Add"):
            p_n = st.text_input("Product Name"); p_c = st.number_input("Cost Price"); p_s = st.number_input("Selling Price")
            if st.form_submit_button("Add"):
                conn.cursor().execute("INSERT INTO ProductMaster VALUES (?,?,?)", (p_n, p_c, p_s))
                conn.commit(); st.success("Added!"); st.rerun()
        st.dataframe(pd.read_sql_query("SELECT * FROM ProductMaster", conn), use_container_width=True)

else:
    st.title("🔒 Birdev ERP - Locked")
    st.info("Enter admin password in the sidebar to access.")
    st.stop()
