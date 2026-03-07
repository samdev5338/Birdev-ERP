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
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #312E81 100%);
        color: white; border-radius: 8px; border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
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
                st.session_state['cart'].append({"Product": selected_p, "Quantity": qty, "Rate": res[1], "Total": res[1]*qty, "Profit": (res[1]-res[0])*qty})
        
        if st.session_state['cart']:
            df_cart = pd.DataFrame(st.session_state['cart'])
            st.table(df_cart[['Product', 'Quantity', 'Rate', 'Total']])
            g_total = df_cart['Total'].sum()

            # --- SAVE AND PDF LOGIC ---
            if st.button("💾 SAVE BILL & GENERATE PDF"):
                # 1. Database mein save karein
                cursor = conn.cursor()
                for item in st.session_state['cart']:
                    cursor.execute("INSERT INTO SalesHistory (customer_name, bill_date, product, quantity, total_bill, profit) VALUES (?,?,?,?,?,?)",
                                 (customer_name, bill_date.strftime('%Y-%m-%d'), item['Product'], item['Quantity'], item['Total'], item['Profit']))
                conn.commit()

                # 2. PDF Banayein
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(200, 10, f"Bill To: {customer_name} | Date: {bill_date}", ln=True, align='C')
                pdf.ln(10)
                pdf.cell(80, 10, "Product", 1); pdf.cell(30, 10, "Qty", 1); pdf.cell(40, 10, "Rate", 1); pdf.cell(40, 10, "Total", 1, 1)
                for item in st.session_state['cart']:
                    pdf.cell(80, 10, item['Product'], 1); pdf.cell(30, 10, str(item['Quantity']), 1); pdf.cell(40, 10, str(item['Rate']), 1); pdf.cell(40, 10, str(item['Total']), 1, 1)
                pdf.cell(150, 10, "Grand Total", 1); pdf.cell(40, 10, f"Rs {g_total}", 1, 1)
                
                pdf_output = f"Bill_{customer_name}.pdf"
                pdf.output(pdf_output)

                # 3. PDF link turant dikhayein
                with open(pdf_output, "rb") as f:
                    st.download_button("📥 CLICK HERE TO DOWNLOAD PDF BILL", f, file_name=pdf_output)
                
                st.session_state['cart'] = [] # Cart khali karein
                st.success("Record Saved Successfully!")

    # --- Menu 3: Customer History (All Records PDF) ---
    elif menu_choice == "📜 Customer History":
        st.header("📜 Sales History")
        df_h = pd.read_sql_query("SELECT * FROM SalesHistory ORDER BY id DESC", conn)
        
        if not df_h.empty:
            if st.button("📥 GENERATE FULL REPORT PDF"):
                pdf_rep = FPDF()
                pdf_rep.add_page()
                pdf_rep.set_font("Arial", 'B', 12)
                pdf_rep.cell(200, 10, "FULL SALES REPORT - BIRDEV UDYOG", ln=True, align='C')
                pdf_rep.ln(5)
                # Headers
                pdf_rep.cell(30, 10, "Date", 1); pdf_rep.cell(50, 10, "Customer", 1); pdf_rep.cell(50, 10, "Product", 1); pdf_rep.cell(30, 10, "Total", 1); pdf_rep.cell(30, 10, "Profit", 1, 1)
                pdf_rep.set_font("Arial", '', 10)
                for i, r in df_h.iterrows():
                    pdf_rep.cell(30, 10, str(r['bill_date']), 1); pdf_rep.cell(50, 10, str(r['customer_name']), 1); pdf_rep.cell(50, 10, str(r['product']), 1); pdf_rep.cell(30, 10, str(r['total_bill']), 1); pdf_rep.cell(30, 10, str(r['profit']), 1, 1)
                
                pdf_rep.output("Full_Report.pdf")
                with open("Full_Report.pdf", "rb") as f:
                    st.download_button("💾 DOWNLOAD FULL REPORT", f, file_name="Full_Report.pdf")
            
            st.dataframe(df_h, use_container_width=True)

    # --- Baaki Menus (Manage/Analytics) ---
    elif menu_choice == "⚙️ Manage Products":
        st.header("⚙️ Product Settings")
        with st.form("Add"):
            p_n = st.text_input("Product Name"); p_c = st.number_input("Cost"); p_s = st.number_input("Selling")
            if st.form_submit_button("Add Product"):
                conn.cursor().execute("INSERT INTO ProductMaster VALUES (?,?,?)", (p_n, p_c, p_s))
                conn.commit(); st.rerun()
        st.dataframe(pd.read_sql_query("SELECT * FROM ProductMaster", conn), use_container_width=True)

else:
    st.title("🔒 Locked")
    st.stop()
