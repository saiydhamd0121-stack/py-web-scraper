from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            customer TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            tx TEXT,
            status TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

products = {
    "1": {"name": "AI Telegram Bot Setup", "price": 30, "desc": "Smart Telegram bot integrated with AI for automated customer replies and group management."},
    "2": {"name": "Smart AI Data Analyst Tool", "price": 45, "desc": "Advanced Python script to analyze datasets and generate professional business reports."},
    "3": {"name": "Custom Website Development Service", "price": 120, "desc": "Professional custom website or landing page built from scratch according to your requirements."},
    "4": {"name": "Web Scraping & Lead Generation Script", "price": 18, "desc": "High-performance data extractor and lead generator for your marketing campaigns."}
}

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'GET':
        return redirect(url_for('index'))
        
    product_id = request.form.get('product_id')
    customer_name = request.form.get('customer_name', '').strip()
    customer_email = request.form.get('customer_email', '').strip()
    contact_info = request.form.get('contact_info', '').strip()
    binance_tx = request.form.get('binance_tx', '').strip()
    
    if not customer_name or not customer_email or not contact_info or not binance_tx:
        return "خطأ: يرجى ملء جميع الحقول ومعرف المعاملة!", 400

    if product_id in products:
        product = products[product_id]
        order_num = str(random.randint(100000, 999999))
        order_date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (order_number, product, price, customer, contact, email, tx, status, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_num, product['name'], product['price'], customer_name, contact_info, customer_email, binance_tx, "قيد المراجعة والتحقق", order_date))
        conn.commit()
        
        cursor.execute("SELECT last_insert_rowid()")
        db_id = cursor.fetchone()[0]
        conn.close()

        return redirect(url_for('invoice_page', order_id=db_id))
    
    return "المنتج غير موجود!", 400

@app.route('/verify-binance/<int:order_id>', methods=['POST'])
def verify_binance(order_id):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    # محاكاة الاتصال بشبكة باينانس والتحقق من صحة التحويل
    cursor.execute("UPDATE orders SET status = 'مكتمل ومدفوع (تم التحقق عبر Binance Pay)' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('invoice_page', order_id=order_id))

@app.route('/invoice/<int:order_id>')
def invoice_page(order_id):
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        return "الطلب غير موجود!", 404
        
    return render_template('invoice.html', order=order)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

