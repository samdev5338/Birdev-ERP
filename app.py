import streamlit as st
import sqlite3
import pandas as pd
from fpdf import FPDF
import datetime
import plotly.express as px  # नए और फ्यूचरिस्टिक ग्राफ के लिए

# 1. पेज की सेटिंग (पूरी स्क्रीन का इस्तेमाल)
st.set_page_config(page_title="Birdev ERP", page_icon="🌐", layout="wide")

# ================= FUTURISTIC CSS DESIGN & DEVELOPER BOX =================
st.markdown("""
    <style>
    /* बैकग्राउंड और फॉन्ट की सेटिंग */
    .reportview-container {
        background: #f0f2f6;
    }
    /* बटन्स को 3D और फ्यूचरिस्टिक बनाना */
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #312E81 100%);
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease 0s;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        background: linear-gradient(90deg, #312E81 0%, #1E3A8A 100%);
    }
    /* मेट्रिक्स (नंबर्स) के कार्ड्स का डिज़ाइन */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #1E3A8A;
    }
    
    /* ======== DEVELOPER SAMARTH BOX ======== */
    .developer-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(90deg, #1E3A8A 0%, #312E81 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        z-index: 10000;
        font-size: 15px;
        border: 1px solid #ffffff55;
        backdrop-filter: blur(5px);
    }
    </style>
    
    <div class="developer-box">
        👨‍💻 Developed by Samarth
    </div>
""", unsafe_allow_html=True)
# =========================================================================

if 'cart' not in st.session_state:
    st.session_state['cart'] = []

def setup_db():
    conn = sqlite3.connect('birdev_erp_billing.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ProductMaster
                      (product TEXT, cost_price REAL, selling_price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS SalesHistory
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, bill_date TEXT,
                       product TEXT, quantity REAL, total_bill REAL, profit REAL)''')
    cursor.execute("SELECT count(*) FROM ProductMaster")
    if cursor.fetchone()[0] == 0:
        default_data = [('Poha Papad', 150.0, 200.0), ('Nachani Papad', 120.0, 180.0)]
        cursor.executemany('INSERT INTO ProductMaster VALUES (?,?,?)', default_data)
        conn.commit()
    return conn

conn = setup_db()

# ================= SIDEBAR NAVIGATION (प्रोफेशनल मेनू) =================
st.sidebar.title("🌐 Birdev ERP")
st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation Menu")
# टैब्स की जगह अब साइडबार में रेडियो बटन्स हैं
menu_choice = st.sidebar.radio("Go to:", 
    ["🧾 Create Invoice", "📈 Business Analytics", "📜 Customer History", "⚙️ Manage Products"]
)
st.sidebar.markdown("---")
st.sidebar.info("Logged in as: Admin\n\nSystem Status: Online 🟢")
# =======================================================================

# मेन स्क्रीन का हेडर
st.title("🏭 Birdev Udyog Samuha")
st.markdown("##### Advanced Enterprise Resource Planning System")
st.divider()

# ----------------- मेनू 1: बिलिंग -----------------
if menu_choice == "🧾 Create Invoice":
    st.header("🛒 Point of Sale (POS) / Billing")
    
    df_products = pd.read_sql_query("SELECT DISTINCT product FROM ProductMaster", conn)
    product_list = df_products['product'].tolist() if not df_products.empty else []
    
    st.markdown("### 👤 Customer Details")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        customer_name = st.text_input("Customer Name", "Rakesh")
    with col_c2:
        bill_date = st.date_input("Bill Date", datetime.date.today())
        
    st.markdown("### 📦 Add Products")
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        selected_product = st.selectbox("Select Product", product_list)
    with col2:
        qty = st.number_input("Quantity (Kg)", min_value=1, value=10)
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ Add Item"):
            cursor = conn.cursor()
            cursor.execute("SELECT cost_price, selling_price FROM ProductMaster WHERE product=?", (selected_product,))
            result = cursor.fetchone()
            if result:
                cost, sp = result[0], result[1]
                st.session_state['cart'].append({
                    "Product": selected_product, "Quantity": qty, "Cost Rate": cost,
                    "Selling Rate": sp, "Total Cost": cost * qty, "Total Sales": sp * qty, "Profit": (sp - cost) * qty
                })
                st.success(f"Added {qty} Kg {selected_product}")

    st.divider()
    
    if len(st.session_state['cart']) > 0:
        st.markdown(f"### 🧾 Current Bill Items: **{customer_name}**")
        cart_df = pd.DataFrame(st.session_state['cart'])
        st.dataframe(cart_df[['Product', 'Quantity', 'Selling Rate', 'Total Sales']], use_container_width=True, hide_index=True)
        
        grand_cost = cart_df['Total Cost'].sum()
        grand_sales = cart_df['Total Sales'].sum()
        grand_profit = cart_df['Profit'].sum()
        
        st.markdown("### 📊 Live Financial Overview")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Cost (Laagat)", f"₹ {grand_cost:,.2f}")
        m_col2.metric("Total Bill (Revenue)", f"₹ {grand_sales:,.2f}")
        m_col3.metric("Net Profit (Munafa)", f"₹ {grand_profit:,.2f}")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Save & Generate PDF", type="primary"):
                cursor = conn.cursor()
                for item in st.session_state['cart']:
                    cursor.execute('''INSERT INTO SalesHistory (customer_name, bill_date, product, quantity, total_bill, profit) 
                                      VALUES (?, ?, ?, ?, ?, ?)''', 
                                   (customer_name, bill_date.strftime('%Y-%m-%d'), item['Product'], item['Quantity'], item['Total Sales'], item['Profit']))
                conn.commit()
                st.toast("✅ Customer History Saved Successfully!")

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 18)
                pdf.cell(200, 10, "BIRDEV UDYOG SAMUHA", ln=True, align='C')
                pdf.set_font("Arial", '', 12)
                pdf.cell(200, 10, "Official Invoice", ln=True, align='C')
                pdf.line(10, 30, 200, 30)
                
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(100, 10, f"Date: {bill_date.strftime('%d-%m-%Y')}", ln=False)
                pdf.cell(100, 10, f"Customer: {customer_name}", ln=True)
                pdf.ln(5)
                
                pdf.set_fill_color(200, 220, 255)
                pdf.cell(80, 10, "Product Name", border=1, fill=True)
                pdf.cell(30, 10, "Qty (Kg)", border=1, fill=True)
                pdf.cell(40, 10, "Rate/Kg", border=1, fill=True)
                pdf.cell(40, 10, "Total Amount", border=1, ln=True, fill=True)
                
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
                
                with open(pdf_filename, "rb") as pdf_file:
                    st.download_button("📥 Download PDF Bill", data=pdf_file, file_name=pdf_filename, mime="application/pdf")
                    
        with col_btn2:
            if st.button("🗑️ Clear Cart"):
                st.session_state['cart'] = []
                st.rerun()

# ----------------- मेनू 2: एनालिटिक्स (Interactive Plotly Graphs) -----------------
elif menu_choice == "📈 Business Analytics":
    st.header("📈 AI-Powered Business Dashboard")
    df_analytics = pd.read_sql_query("SELECT * FROM SalesHistory", conn)
    
    if not df_analytics.empty:
        total_revenue = df_analytics['total_bill'].sum()
        total_profit = df_analytics['profit'].sum()
        total_qty = df_analytics['quantity'].sum()
        
        st.markdown("### 💰 Key Performance Indicators (KPIs)")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
        col_m2.metric("Total Net Profit", f"₹ {total_profit:,.2f}")
        col_m3.metric("Total Volume Sold", f"{total_qty} Kg")
        
        st.divider()
        
        # Plotly के एडवांस्ड और इंटरैक्टिव ग्राफ्स
        col_ch1, col_ch2 = st.columns(2)
        
        with col_ch1:
            st.markdown("#### 🔥 Most Demanding Products (Volume)")
            demand_df = df_analytics.groupby('product')['quantity'].sum().reset_index()
            # Plotly Pie Chart (3D फील के साथ)
            fig_pie = px.pie(demand_df, values='quantity', names='product', hole=0.4, color_discrete_sequence=px.colors.sequential.Plasma)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_ch2:
            st.markdown("#### 💵 Profit Margins by Product")
            profit_df = df_analytics.groupby('product')['profit'].sum().reset_index()
            # Plotly Bar Chart (होवर इफ़ेक्ट और कलर्स के साथ)
            fig_bar = px.bar(profit_df, x='product', y='profit', text_auto='.2s', color='profit', color_continuous_scale='Viridis')
            fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_bar, use_container_width=True)
            
    else:
        st.info("📊 अभी तक कोई सेल नहीं हुई है। ग्राफ देखने के लिए बिल जनरेट करें।")

# ----------------- मेनू 3: कस्टमर हिस्ट्री -----------------
elif menu_choice == "📜 Customer History":
    st.header("📜 Customer Database")
    
    df_for_delete = pd.read_sql_query("SELECT id, bill_date, customer_name, product, total_bill FROM SalesHistory ORDER BY id DESC", conn)
    if not df_for_delete.empty:
        with st.expander("❌ Delete a Customer Record (Click to open)"):
            history_options = df_for_delete.apply(lambda row: f"ID: {row['id']} | Date: {row['bill_date']} | Name: {row['customer_name']} | Item: {row['product']} | Bill: ₹{row['total_bill']}", axis=1).tolist()
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                record_to_delete = st.selectbox("Select Record", history_options)
            with col_d2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete"):
                    record_id = record_to_delete.split(" | ")[0].replace("ID: ", "")
                    conn.cursor().execute("DELETE FROM SalesHistory WHERE id=?", (record_id,))
                    conn.commit()
                    st.success("✅ Deleted!")
                    st.rerun()

    st.markdown("### 🔍 Search Sales Records")
    search_query = st.text_input("Enter Customer Name to search...")
    if search_query:
        df_history = pd.read_sql_query(f"SELECT bill_date as 'Date', customer_name as 'Customer', product as 'Product', quantity as 'Qty(Kg)', total_bill as 'Bill(₹)', profit as 'Profit(₹)' FROM SalesHistory WHERE customer_name LIKE '%{search_query}%' ORDER BY id DESC", conn)
    else:
        df_history = pd.read_sql_query("SELECT bill_date as 'Date', customer_name as 'Customer', product as 'Product', quantity as 'Qty(Kg)', total_bill as 'Bill(₹)', profit as 'Profit(₹)' FROM SalesHistory ORDER BY id DESC", conn)
    
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True, hide_index=True)

# ----------------- मेनू 4: मैनेज प्रोडक्ट्स (एडमिन) -----------------
elif menu_choice == "⚙️ Manage Products":
    st.header("⚙️ Master Data Management (Admin)")
    df_all = pd.read_sql_query("SELECT * FROM ProductMaster", conn)
    all_products = df_all['product'].tolist() if not df_all.empty else []
    
    col_add, col_edit, col_del = st.columns(3)
    
    with col_add:
        st.markdown("#### ➕ Add Product")
        with st.form("add_form", clear_on_submit=True):
            new_product = st.text_input("Name")
            new_cost = st.number_input("Cost ₹", min_value=0.0)
            new_sp = st.number_input("Selling Price ₹", min_value=0.0)
            if st.form_submit_button("Save Product"):
                if new_product:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM ProductMaster WHERE product=?", (new_product,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO ProductMaster VALUES (?, ?, ?)", (new_product, new_cost, new_sp))
                        conn.commit()
                        st.success("Added!")
                        st.rerun()

    with col_edit:
        st.markdown("#### ✏️ Edit Product")
        if all_products:
            edit_product = st.selectbox("Select", all_products, key="edit_box")
            current_data = df_all[df_all['product'] == edit_product].iloc[0]
            with st.form("edit_form"):
                edit_cost = st.number_input("Cost ₹", value=float(current_data['cost_price']))
                edit_sp = st.number_input("Selling Price ₹", value=float(current_data['selling_price']))
                if st.form_submit_button("Update Prices"):
                    conn.cursor().execute("UPDATE ProductMaster SET cost_price=?, selling_price=? WHERE product=?", (edit_cost, edit_sp, edit_product))
                    conn.commit()
                    st.success("Updated!")
                    st.rerun()

    with col_del:
        st.markdown("#### ❌ Delete Product")
        if all_products:
            del_product = st.selectbox("Select", all_products, key="del_box")
            if st.button("🗑️ Delete Permanently"):
                conn.cursor().execute("DELETE FROM ProductMaster WHERE product=?", (del_product,))
                conn.commit()
                st.success("Deleted!")
                st.rerun()

conn.close()
