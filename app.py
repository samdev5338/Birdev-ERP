import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime
import plotly.express as px
import plotly.graph_objects as go

# ================= 1. PAGE SETTING =================
st.set_page_config(page_title="Birdev Udyog Samuha ERP", page_icon="🚀", layout="wide")

# ================= 2. ULTRA PREMIUM COLORFUL 3D CSS =================
st.markdown("""
    <style>
    /* Global Background - Colorful Deep Radial Gradient */
    .stApp { 
        background: radial-gradient(circle at top right, #2e1065, #0f172a 40%, #020617); 
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div { color: #f8fafc !important; }
    
    /* Login Box 3D Colorful Effect */
    .login-container {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8), 
                    inset 0 2px 0 rgba(255,255,255,0.2),
                    0 0 30px rgba(139, 92, 246, 0.3); /* Purple Glow */
        text-align: center;
        max-width: 400px;
        margin: auto;
        margin-top: 100px;
        border: 1px solid #8b5cf6;
    }

    /* 3D Inputs & Select Boxes (Debossed Vibrant Effect) */
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    .stNumberInput input, .stTextInput input, .stSelectbox > div {
        background: #0f172a !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: inset 4px 4px 10px rgba(0,0,0,0.9), inset -2px -2px 8px rgba(255,255,255,0.05) !important;
        color: #00ffcc !important;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    div[data-baseweb="input"] > div:focus-within, 
    div[data-baseweb="select"] > div:focus-within,
    .stNumberInput input:focus, .stTextInput input:focus {
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.5), inset 4px 4px 10px rgba(0,0,0,0.9) !important;
        border: 1px solid #00ffcc !important;
    }

    /* Main Area Colorful 3D Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6);
        background-size: 200% auto;
        color: #ffffff !important;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5), 
                    inset 0 2px 0 rgba(255,255,255,0.4), 
                    inset 0 -4px 0 rgba(0,0,0,0.4);
        transition: 0.4s;
        font-weight: 900;
        letter-spacing: 1.5px;
        padding: 12px 24px;
    }
    .stButton>button:hover {
        background-position: right center;
        transform: translateY(-4px);
        box-shadow: 0 15px 30px rgba(139, 92, 246, 0.7), 
                    inset 0 2px 0 rgba(255,255,255,0.5), 
                    inset 0 -4px 0 rgba(0,0,0,0.4);
        color: #ffffff !important;
    }
    .stButton>button:active {
        transform: translateY(4px);
        box-shadow: inset 0 5px 15px rgba(0,0,0,0.7) !important;
    }

    /* SIDEBAR COLORFUL 3D NAVIGATION */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050810, #0f172a); 
        border-right: 2px solid #3b82f6;
        box-shadow: 10px 0 25px rgba(0,0,0,0.8);
    }
    [data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #475569;
        box-shadow: 5px 5px 12px rgba(0,0,0,0.7), -1px -1px 4px rgba(255,255,255,0.05);
        text-align: left !important;
        padding: 12px 15px;
        font-size: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        width: 100%;
        display: flex;
        justify-content: flex-start;
        text-transform: none;
        font-weight: bold;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        border-color: #f43f5e;
        background: linear-gradient(145deg, #0f172a, #1e293b);
        box-shadow: 0 0 25px rgba(244, 63, 94, 0.4);
        color: #f43f5e !important;
        transform: translateX(8px);
    }

    /* 3D Metric Cards (Rainbow Top Border) */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #162032, #0a0f1d);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 8px 8px 25px rgba(0,0,0,0.9), -3px -3px 15px rgba(255,255,255,0.04);
        border: 1px solid #1e293b;
        border-top: 4px solid transparent;
        border-image: linear-gradient(to right, #00ffcc, #3b82f6, #ec4899) 1;
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 15px 15px 35px rgba(0,0,0,0.9), 0 0 20px rgba(59, 130, 246, 0.3);
    }
    div[data-testid="metric-container"] label { color: #cbd5e1 !important; font-size: 17px !important; font-weight: 800;}
    div[data-testid="metric-container"] div { 
        background: linear-gradient(to right, #00ffcc, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
        font-weight: 900;
    }

    /* 3D Tabs */
    button[data-baseweb="tab"] {
        background: linear-gradient(145deg, #1e293b, #0f172a) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px 12px 0 0 !important;
        box-shadow: inset 0 2px 0 rgba(255,255,255,0.05) !important;
        margin-right: 5px;
        padding: 10px 20px !important;
        font-weight: bold;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #ec4899, #8b5cf6) !important;
        border-color: #f43f5e !important;
        color: #ffffff !important;
        box-shadow: 0 -5px 20px rgba(236, 72, 153, 0.4), inset 0 2px 0 rgba(255,255,255,0.3) !important;
    }

    /* 3D Expanders */
    div[data-testid="stExpander"] {
        background: linear-gradient(145deg, #1e293b, #0f172a) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 15px !important;
        box-shadow: 8px 8px 20px rgba(0,0,0,0.7) !important;
        overflow: hidden;
    }
    
    /* Title Gradient Effect */
    .colorful-title {
        background: linear-gradient(to right, #00ffcc, #3b82f6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3em;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    .developer-box {
        position: fixed; bottom: 20px; right: 20px;
        background: rgba(15, 23, 42, 0.85); 
        color: #ec4899 !important;
        padding: 12px 25px; 
        border-radius: 30px; 
        font-weight: 900; 
        font-size: 15px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9), 0 0 15px rgba(236, 72, 153, 0.3); 
        border: 2px solid rgba(236, 72, 153, 0.5);
        transition: all 0.3s ease; 
        z-index: 10000;
        backdrop-filter: blur(10px);
    }
    .developer-box:hover { 
        background: linear-gradient(135deg, #ec4899, #8b5cf6);
        color: white !important; 
        transform: scale(1.1); 
        border-color: #fff;
        box-shadow: 0 10px 40px rgba(236, 72, 153, 0.6);
    }
    </style>
    <div class="developer-box">🚀 Developed by Samarth</div>
""", unsafe_allow_html=True)

# ================= 3. SECURITY & LOGIN =================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<h1 class='colorful-title' style='text-align: center;'>Birdev Udyog Samuha</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #cbd5e1;'>Admin Secure Portal (सुरक्षित पोर्टल)</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        pwd = st.text_input("Enter Admin Password (पासवर्ड टाका)", type="password", placeholder="Password yahan dalein...")
        
        if st.button("Unlock System 🔓 (सिस्टम चालू करा)", use_container_width=True):
            if pwd == "33":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password! (चुकीचा पासवर्ड)")
    st.stop()

# ================= 4. DATABASE SETUP =================
if 'cart' not in st.session_state:
    st.session_state['cart'] = []

def setup_db():
    conn = sqlite3.connect('birdev_erp_pro_v3.db') 
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ProductMaster (product TEXT PRIMARY KEY, cost_price REAL, selling_price REAL, stock REAL DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS SalesHistory (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, bill_date TEXT, product TEXT, quantity REAL, total_bill REAL, profit REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (name TEXT PRIMARY KEY, hourly_rate REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS PayrollHistory (id INTEGER PRIMARY KEY AUTOINCREMENT, emp_name TEXT, date TEXT, hours_worked REAL, total_paid REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount REAL, description TEXT, entered_by TEXT)''')
    conn.commit()
    return conn

conn = setup_db()

def resequence_ids(table_name):
    cursor = conn.cursor()
    df = pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY id", conn)
    
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
        
    cursor.execute(f"DELETE FROM {table_name}")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
    conn.commit()
    
    if not df.empty:
        df.to_sql(table_name, conn, if_exists='append', index=False)
    conn.commit()

# ================= 5. SIDEBAR NAVIGATION =================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", width=80)
st.sidebar.markdown("<h2 style='background: linear-gradient(to right, #00ffcc, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🌐 Birdev Udyog Samuha</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = "🧾 Create Invoice (बिल बनवा)"

def change_tab(tab_name):
    st.session_state['active_tab'] = tab_name

# Sidebar buttons in Marathi
if st.sidebar.button("🧾 Create Invoice (बिल बनवा)"): change_tab("🧾 Create Invoice (बिल बनवा)")
if st.sidebar.button("📦 Inventory (मालाची नोंद)"): change_tab("📦 Inventory (मालाची नोंद)")
if st.sidebar.button("👥 HR & Payroll (कामगार आणि पगार)"): change_tab("👥 HR & Payroll (कामगार आणि पगार)")
if st.sidebar.button("💸 Expenses (खर्च आणि नुकसान)"): change_tab("💸 Expenses (खर्च आणि नुकसान)")
if st.sidebar.button("📈 Analytics (व्यवसायाचा नफा)"): change_tab("📈 Analytics (व्यवसायाचा नफा)")
if st.sidebar.button("📜 Customer History (जुन्या बिलांची नोंद)"): change_tab("📜 Customer History (जुन्या बिलांची नोंद)")

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout (बाहेर पडा)", type="primary"):
    st.session_state['logged_in'] = False
    st.rerun()

menu_choice = st.session_state['active_tab']
st.markdown("<h1 class='colorful-title'>🏭 Birdev Udyog Samuha</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color: #00ffcc; text-shadow: 0 0 10px rgba(0,255,204,0.3);'>✦ {menu_choice}</h3>", unsafe_allow_html=True)
st.divider()

# ================= MODULE 1: INVOICE (POS) =================
if menu_choice == "🧾 Create Invoice (बिल बनवा)":
    df_products = pd.read_sql_query("SELECT product, stock FROM ProductMaster WHERE stock > 0", conn)
    product_list = df_products['product'].tolist() if not df_products.empty else []
    
    col_c1, col_c2 = st.columns(2)
    with col_c1: customer_name = st.text_input("👤 Customer Name (ग्राहकाचे नाव)", "Rakesh")
    with col_c2: bill_date = st.date_input("📅 Bill Date (तारीख)", datetime.date.today())
        
    st.markdown("#### 🛍️ Add Items (वस्तू जोडा)")
    if not product_list: st.error("⚠️ Stock is empty! Add products from Inventory. (माल शिल्लक नाही! आधी मालाची नोंद करा.)")
    else:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            selected_product = st.selectbox("Select Product (वस्तू निवडा)", product_list)
            available_stock = df_products[df_products['product'] == selected_product]['stock'].values[0]
            st.caption(f"Stock (शिल्लक माल): **{available_stock} Kg**")
        with col2: qty = st.number_input("Quantity in Kg (वजन किलो मध्ये)", min_value=1.0, max_value=float(available_stock), value=1.0)
        with col3:
            st.write(" "); st.write(" ")
            if st.button("➕ Add to Cart (बिलात जोडा)"):
                cursor = conn.cursor()
                cursor.execute("SELECT cost_price, selling_price FROM ProductMaster WHERE product=?", (selected_product,))
                cost, sp = cursor.fetchone()
                found = False
                for item in st.session_state['cart']:
                    if item['Product'] == selected_product:
                        if item['Quantity'] + qty > available_stock:
                            st.error("❌ Exceeds stock! (माल शिल्लक नाही!)")
                            found = True; break
                        item['Quantity'] += qty
                        item['Total Cost'] = cost * item['Quantity']
                        item['Total Sales'] = sp * item['Quantity']
                        item['Profit'] = (sp - cost) * item['Quantity']
                        found = True; st.success("Updated! (बदल केला)"); break
                if not found:
                    st.session_state['cart'].append({"Product": selected_product, "Quantity": qty, "Cost Rate": cost, "Selling Rate": sp, "Total Cost": cost * qty, "Total Sales": sp * qty, "Profit": (sp - cost) * qty})
                    st.success("Added! (वस्तू जोडली)")

    if len(st.session_state['cart']) > 0:
        st.divider()
        st.dataframe(pd.DataFrame(st.session_state['cart'])[['Product', 'Quantity', 'Selling Rate', 'Total Sales']], use_container_width=True)
        col_rm1, col_rm2 = st.columns([3, 1])
        with col_rm1: item_to_remove = st.selectbox("Remove item (वस्तू काढा)", ["None"] + [i['Product'] for i in st.session_state['cart']])
        with col_rm2:
            st.write(" "); st.write(" ")
            if st.button("🗑️ Remove (काढून टाका)") and item_to_remove != "None":
                st.session_state['cart'] = [i for i in st.session_state['cart'] if i['Product'] != item_to_remove]
                st.rerun()

        if len(st.session_state['cart']) > 0:
            grand_cost = sum(i['Total Cost'] for i in st.session_state['cart'])
            grand_sales = sum(i['Total Sales'] for i in st.session_state['cart'])
            grand_profit = sum(i['Profit'] for i in st.session_state['cart'])
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Cost (एकूण खर्च/लागत)", f"₹ {grand_cost:,.2f}")
            m_col2.metric("Total Bill (एकूण बिल)", f"₹ {grand_sales:,.2f}")
            m_col3.metric("Net Profit (नफा/फायदा)", f"₹ {grand_profit:,.2f}")
            
            st.write("") 
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("💾 Save Bill & Generate PDF (बिल सेव्ह करा आणि PDF बनवा)", type="primary"):
                    cursor = conn.cursor()
                    for item in st.session_state['cart']:
                        cursor.execute('''INSERT INTO SalesHistory (customer_name, bill_date, product, quantity, total_bill, profit) VALUES (?, ?, ?, ?, ?, ?)''', (customer_name, bill_date.strftime('%Y-%m-%d'), item['Product'], item['Quantity'], item['Total Sales'], item['Profit']))
                        cursor.execute("UPDATE ProductMaster SET stock = stock - ? WHERE product = ?", (item['Quantity'], item['Product']))
                    conn.commit()
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 20)
                    pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA", ln=True, align='C')
                    pdf.set_font("Arial", '', 12)
                    pdf.cell(200, 10, "Official Invoice", ln=True, align='C')
                    pdf.line(10, 30, 200, 30); pdf.ln(10)
                    
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(100, 10, f"Date: {bill_date.strftime('%d-%m-%Y')}", ln=False)
                    pdf.cell(100, 10, f"Customer: {customer_name}", ln=True); pdf.ln(5)
                    
                    pdf.set_fill_color(200, 200, 200)
                    pdf.cell(80, 10, "Product Name", border=1, fill=True)
                    pdf.cell(30, 10, "Qty (Kg)", border=1, fill=True)
                    pdf.cell(40, 10, "Rate/Kg", border=1, fill=True)
                    pdf.cell(40, 10, "Total", border=1, ln=True, fill=True)
                    
                    pdf.set_font("Arial", '', 12)
                    for item in st.session_state['cart']:
                        pdf.cell(80, 10, item['Product'], border=1)
                        pdf.cell(30, 10, str(item['Quantity']), border=1)
                        pdf.cell(40, 10, f"Rs {item['Selling Rate']}", border=1)
                        pdf.cell(40, 10, f"Rs {item['Total Sales']}", border=1, ln=True)
                        
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(150, 10, "Grand Total", border=1, align='R')
                    pdf.cell(40, 10, f"Rs {grand_sales}", border=1, ln=True)
                    
                    pdf_filename = f"Final_Bill_{customer_name}.pdf"
                    pdf.output(pdf_filename)
                    
                    st.session_state['pdf_ready'] = pdf_filename
                    st.session_state['cart'] = []
                    st.success("✅ Bill Saved Successfully! (बिल सेव्ह झाले आहे!)")
            
            with col_btn2:
                if 'pdf_ready' in st.session_state:
                    with open(st.session_state['pdf_ready'], "rb") as pdf_file:
                        st.download_button("📥 Download PDF Invoice (PDF डाउनलोड करा)", data=pdf_file, file_name=st.session_state['pdf_ready'], mime="application/pdf")
                    
                    if st.button("🔄 Create New Bill (नवीन बिल बनवा)"):
                        del st.session_state['pdf_ready']
                        st.rerun()

# ================= MODULE 2: INVENTORY =================
elif menu_choice == "📦 Inventory (मालाची नोंद)":
    df_all = pd.read_sql_query("SELECT product as 'Product', stock as 'Stock (Kg)', cost_price as 'Cost (₹)', selling_price as 'SP (₹)' FROM ProductMaster", conn)
    all_products = df_all['Product'].tolist() if not df_all.empty else []
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ➕ Add New Product (नवीन वस्तू जोडा)")
        with st.form("add_form"):
            new_prod = st.text_input("Product Name (वस्तूचे नाव)"); new_stock = st.number_input("Stock (शिल्लक माल)", min_value=0.0); cost = st.number_input("Cost Price (खरेदी किंमत)", min_value=0.0); sp = st.number_input("Selling Price (विक्री किंमत)", min_value=0.0)
            if st.form_submit_button("Save Data (सेव्ह करा)"):
                conn.cursor().execute("INSERT OR IGNORE INTO ProductMaster VALUES (?, ?, ?, ?)", (new_prod, cost, sp, new_stock)); conn.commit(); st.rerun()
    with c2:
        st.markdown("#### 🔄 Add Stock (जुना माल भरा)")
        if all_products:
            with st.form("edit_form"):
                e_prod = st.selectbox("Select Product (वस्तू निवडा)", all_products); add_stk = st.number_input("Add Stock Kg (माल किलो मध्ये जोडा)", min_value=0.0)
                if st.form_submit_button("Update Stock (माल अपडेट करा)"):
                    conn.cursor().execute("UPDATE ProductMaster SET stock = stock + ? WHERE product=?", (add_stk, e_prod)); conn.commit(); st.rerun()
                    
    st.divider()
    
    st.markdown("#### 📋 Product Inventory List (मालाची यादी)")
    if not df_all.empty:
        df_all.insert(0, 'Sr. No.', range(1, len(df_all) + 1))
        st.dataframe(df_all, use_container_width=True, hide_index=True)
    else:
        st.info("No products found in the inventory. (मालाची नोंद नाही.)")

# ================= MODULE 3: HR & PAYROLL =================
elif menu_choice == "👥 HR & Payroll (कामगार आणि पगार)":
    tab1, tab2, tab3 = st.tabs(["📝 Add/Edit Kamgar (कामगार नोंद)", "💰 Pay Salary (पगार द्या)", "🖨️ Report PDF (पगाराची रिपोर्ट)"])
    
    with tab1:
        st.markdown("#### Register Worker's Hourly Rate (कामगाराची तासाची मजुरी नोंद करा)")
        with st.form("add_emp"):
            e_name = st.text_input("Kamgar Name (कामगाराचे नाव)")
            e_rate = st.number_input("Per Hour Pagar ₹ (तासाचा पगार)", min_value=1.0, value=50.0)
            if st.form_submit_button("Save Kamgar (सेव्ह करा)"):
                conn.cursor().execute("INSERT OR REPLACE INTO Employees VALUES (?, ?)", (e_name, e_rate)); conn.commit()
                st.success("Worker Saved! (नोंद झाली)")
        st.dataframe(pd.read_sql_query("SELECT name as 'Kamgar', hourly_rate as '₹ per Hour' FROM Employees", conn), use_container_width=True)

    with tab2:
        st.markdown("#### Calculate & Pay Salary (पगाराचा हिशोब)")
        emps = pd.read_sql_query("SELECT * FROM Employees", conn)
        if not emps.empty:
            sel_emp = st.selectbox("Select Kamgar (कामगार निवडा)", emps['name'].tolist())
            rate = emps[emps['name']==sel_emp]['hourly_rate'].values[0]
            st.caption(f"Hourly Rate (तासाचा पगार): ₹{rate}")
            pay_date = st.date_input("Date (तारीख)", datetime.date.today())
            hours = st.number_input("Hours Worked (किती तास काम केले)", min_value=0.5, step=0.5, value=8.0)
            total_salary = rate * hours
            st.info(f"Total Salary to Pay (एकूण पगार): **₹ {total_salary}**")
            
            if st.button("💸 Confirm Payment (पगार जमा करा)"):
                conn.cursor().execute("INSERT INTO PayrollHistory (emp_name, date, hours_worked, total_paid) VALUES (?,?,?,?)", (sel_emp, pay_date.strftime('%Y-%m-%d'), hours, total_salary))
                conn.commit(); st.success("Salary Paid & Logged! (पगार नोंदवला)")
        else: st.warning("Please add Kamgar first. (आधी कामगार जोडा)")

    with tab3:
        st.markdown("#### Generate Salary PDF (पगाराची PDF बनवा)")
        if not emps.empty:
            rep_emp = st.selectbox("Select Kamgar for Report (कामगार निवडा)", emps['name'].tolist(), key="rep")
            df_pay = pd.read_sql_query(f"SELECT date, hours_worked, total_paid FROM PayrollHistory WHERE emp_name='{rep_emp}'", conn)
            if not df_pay.empty:
                st.dataframe(df_pay)
                if st.button("📄 Generate PDF Report (PDF बनवा)"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16); pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA", ln=True, align='C')
                    pdf.set_font("Arial", 'B', 12); pdf.cell(200, 10, f"Salary Statement: {rep_emp}", ln=True, align='C'); pdf.ln(10)
                    pdf.cell(60, 10, "Date", border=1); pdf.cell(60, 10, "Hours Worked", border=1); pdf.cell(60, 10, "Amount Paid", border=1, ln=True)
                    pdf.set_font("Arial", '', 12)
                    for _, row in df_pay.iterrows():
                        pdf.cell(60, 10, row['date'], border=1); pdf.cell(60, 10, str(row['hours_worked']), border=1); pdf.cell(60, 10, f"Rs {row['total_paid']}", border=1, ln=True)
                    pdf.set_font("Arial", 'B', 12); pdf.cell(120, 10, "Total Paid", border=1, align='R'); pdf.cell(60, 10, f"Rs {df_pay['total_paid'].sum()}", border=1, ln=True)
                    
                    p_name = f"Salary_{rep_emp}.pdf"
                    pdf.output(p_name)
                    with open(p_name, "rb") as f: st.download_button("📥 Download PDF (PDF डाउनलोड करा)", data=f, file_name=p_name)
            else: st.warning("No payment history found. (कोणतीही नोंद नाही)")

# ================= MODULE 4: EXPENSES & WASTAGE =================
elif menu_choice == "💸 Expenses (खर्च आणि नुकसान)":
    st.markdown("### Log Company Expenses & Material Wastage (खर्च आणि नुकसानीची नोंद)")
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("exp_form"):
            e_date = st.date_input("Date (तारीख)")
            e_cat = st.selectbox("Category (प्रकार)", ["Wastage (Nuksan)", "Electricity/Light Bill", "Maintenance", "Travel", "Other"])
            e_amt = st.number_input("Amount ₹ (रक्कम)", min_value=1.0)
            e_desc = st.text_input("Description (कशासाठी खर्च झाला?)")
            e_by = st.text_input("Entered By (कोणी नोंद केली?)")
            if st.form_submit_button("Save Expense (नोंद सेव्ह करा)"):
                conn.cursor().execute("INSERT INTO Expenses (date, category, amount, description, entered_by) VALUES (?,?,?,?,?)", (e_date.strftime('%Y-%m-%d'), e_cat, e_amt, e_desc, e_by))
                conn.commit(); st.success("Saved! (सेव्ह झाले)")
                
    with c2:
        df_exp = pd.read_sql_query("SELECT id, date as Date, category as Type, amount as 'Amount(₹)', description as Details FROM Expenses ORDER BY id DESC", conn)
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
        if not df_exp.empty:
            del_id = st.number_input("Enter ID to Delete Expense (नोंद क्रमांक टाकून डिलीट करा)", min_value=1, step=1)
            if st.button("🗑️ Delete Expense (नोंद काढून टाका)"):
                conn.cursor().execute("DELETE FROM Expenses WHERE id=?", (del_id,)); conn.commit()
                resequence_ids('Expenses'); st.rerun()

# ================= MODULE 5: BUSINESS ANALYTICS =================
elif menu_choice == "📈 Analytics (व्यवसायाचा नफा)":
    st.header("📈 3D Financial & Profit Dashboard (नफ्याचा डॅशबोर्ड)")
    df_sales = pd.read_sql_query("SELECT * FROM SalesHistory", conn)
    df_exp = pd.read_sql_query("SELECT * FROM Expenses", conn)
    df_pay = pd.read_sql_query("SELECT * FROM PayrollHistory", conn)
    
    if not df_sales.empty:
        gross_sales = df_sales['total_bill'].sum()
        gross_profit = df_sales['profit'].sum() 
        
        total_exp = df_exp['amount'].sum() if not df_exp.empty else 0
        total_payroll = df_pay['total_paid'].sum() if not df_pay.empty else 0
        
        true_net_profit = gross_profit - total_exp - total_payroll
        
        st.markdown("### 💰 Ultimate Company Health")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Gross Sales (एकूण विक्री)", f"₹ {gross_sales:,.2f}")
        c2.metric("Gross Profit (एकूण नफा)", f"₹ {gross_profit:,.2f}")
        c3.metric("Deductions (खर्च आणि पगार)", f"₹ {(total_exp + total_payroll):,.2f}", delta="- Expense", delta_color="inverse")
        c4.metric("🏆 TRUE NET PROFIT (हातात आलेला निव्वळ नफा)", f"₹ {true_net_profit:,.2f}")
        
        st.divider()
        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("#### 💸 Money Flow (पैशाचा प्रवाह)")
            flow_df = pd.DataFrame({'Category': ['Gross Profit', 'Company Expenses', 'Kamgar Salary'], 'Amount': [gross_profit, total_exp, total_payroll]})
            fig_pie = px.pie(flow_df, values='Amount', names='Category', hole=0.5, color_discrete_sequence=['#00ffcc', '#f43f5e', '#a855f7'])
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_ch2:
            st.markdown("#### 🔥 Most Demanding Products (जास्त विकल्या गेलेल्या वस्तू)")
            demand_df = df_sales.groupby('product')['quantity'].sum().reset_index()
            fig_bar = px.bar(demand_df, x='product', y='quantity', color='quantity', color_continuous_scale='Turbo')
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        st.markdown("#### 📄 Analytics Reports")
        
        if st.button("⚙️ Generate Top Products Analytics PDF (रिपोर्ट PDF बनवा)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA - Analytics Report", ln=True, align='C')
            pdf.ln(10)
            
            top_selling = df_sales.groupby('product')['quantity'].sum().sort_values(ascending=False)
            top_profit = df_sales.groupby('product')['profit'].sum().sort_values(ascending=False)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, "Top Demanding Products (by Quantity Sold):", ln=True)
            pdf.set_font("Arial", '', 12)
            for prod, qty in top_selling.items():
                pdf.cell(200, 10, f"- {prod}: {qty} Kg", ln=True)
            
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, "Most Profitable Products (by Net Profit Generated):", ln=True)
            pdf.set_font("Arial", '', 12)
            for prod, prof in top_profit.items():
                pdf.cell(200, 10, f"- {prod}: Rs {prof:,.2f}", ln=True)
                
            pdf.output("Top_Products_Report.pdf")
            st.session_state['analytics_pdf'] = "Top_Products_Report.pdf"
            st.success("✅ Report Generated! (रिपोर्ट तयार झाली!)")
            
        if 'analytics_pdf' in st.session_state:
            with open(st.session_state['analytics_pdf'], "rb") as f:
                st.download_button("📥 Download Top Products Report (रिपोर्ट डाउनलोड करा)", data=f, file_name=st.session_state['analytics_pdf'], mime="application/pdf")

# ================= MODULE 6: SALES HISTORY =================
elif menu_choice == "📜 Customer History (जुन्या बिलांची नोंद)":
    df_for_delete = pd.read_sql_query("SELECT * FROM SalesHistory ORDER BY id", conn)
    if not df_for_delete.empty:
        with st.expander("❌ Delete a Customer Record (बिलाची नोंद डिलीट करा)"):
            del_id = st.number_input("Enter Bill No. (ID) to delete (बिल नंबर टाका)", min_value=1, step=1)
            if st.button("🗑️ Delete Record (रेकॉर्ड काढून टाका)"):
                conn.cursor().execute("DELETE FROM SalesHistory WHERE id=?", (del_id,)); conn.commit()
                resequence_ids('SalesHistory'); st.success("Deleted & Re-sequenced! (नोंद काढली)"); st.rerun()

    search_query = st.text_input("🔍 Search Customer Name or Product... (ग्राहकाचे नाव किंवा वस्तू शोधा)")
    if search_query:
        df_history = pd.read_sql_query(f"SELECT id as 'Bill No.', bill_date as 'Date', customer_name as 'Customer', product as 'Product', quantity as 'Qty', total_bill as 'Bill(₹)', profit as 'Profit(₹)' FROM SalesHistory WHERE customer_name LIKE '%{search_query}%' ORDER BY id ASC", conn)
    else:
        df_history = pd.read_sql_query("SELECT id as 'Bill No.', bill_date as 'Date', customer_name as 'Customer', product as 'Product', quantity as 'Qty', total_bill as 'Bill(₹)', profit as 'Profit(₹)' FROM SalesHistory ORDER BY id ASC", conn)
    
    st.dataframe(df_history, use_container_width=True, hide_index=True)

    if not df_history.empty:
        st.write("")
        if st.button("⚙️ Generate PDF for Current View (PDF बनवा)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA - Sales History", ln=True, align='C')
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(20, 10, "Bill No", border=1)
            pdf.cell(30, 10, "Date", border=1)
            pdf.cell(45, 10, "Customer", border=1)
            pdf.cell(45, 10, "Product", border=1)
            pdf.cell(20, 10, "Qty", border=1)
            pdf.cell(30, 10, "Bill(Rs)", border=1, ln=True)
            
            pdf.set_font("Arial", '', 10)
            for index, row in df_history.iterrows():
                pdf.cell(20, 10, str(row['Bill No.']), border=1)
                pdf.cell(30, 10, str(row['Date']), border=1)
                pdf.cell(45, 10, str(row['Customer'])[:15], border=1) 
                pdf.cell(45, 10, str(row['Product'])[:15], border=1)
                pdf.cell(20, 10, str(row['Qty']), border=1)
                pdf.cell(30, 10, str(row['Bill(₹)']), border=1, ln=True)
            
            pdf.output("Customer_Sales_History.pdf")
            st.session_state['history_pdf'] = "Customer_Sales_History.pdf"
            st.success("✅ PDF Generated! (PDF तयार झाली!)")
            
        if 'history_pdf' in st.session_state:
            with open(st.session_state['history_pdf'], "rb") as f:
                st.download_button("📥 Download Customer History PDF (PDF डाउनलोड करा)", data=f, file_name=st.session_state['history_pdf'], mime="application/pdf")

conn.close()
