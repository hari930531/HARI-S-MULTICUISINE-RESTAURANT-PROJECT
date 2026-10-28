# ==============================================================================
# SECTION 1: IMPORTS & ESSENTIAL MODULES
# ==============================================================================

# Core Flask tools for handling HTTP requests, responses, and JSON data
from flask import Flask, jsonify, request

# Cross-Origin Resource Sharing handler to allow frontend requests
from flask_cors import CORS

# MySQL database driver to execute queries and transactions
import mysql.connector

# OS module to read environment variables configured by Kubernetes
import os

# Datetime tools to generate timestamps for orders and live analytics
from datetime import datetime

# JSON serializer to format event payloads
import json

# Kafka Producer client to publish real-time messages to Kafka topics
from kafka import KafkaProducer


# ==============================================================================
# SECTION 2: FLASK INITIALIZATION & KAFKA PRODUCER SETUP
# ==============================================================================

# Initialize the Flask web application
app = Flask(__name__)

# Allow cross-origin browser requests from Nginx frontend pod
CORS(app)

# Read Kafka bootstrap broker address from environment variables
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-service:9092')

# Define dedicated Kafka topic name matching consumer worker
KAFKA_TOPIC = "order-payments"

# Initialize Kafka Producer targeting the cluster service
kafka_producer = None
try:
    kafka_producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        # Serialize Python dictionary directly into UTF-8 JSON bytes
        value_serializer=lambda msg: json.dumps(msg).encode('utf-8')
    )
    print(f"Kafka Producer connected successfully to: {KAFKA_BOOTSTRAP}")
except Exception as err:
    # Print error warning if Kafka service is unreachable during startup
    print(f"Warning: Kafka Producer connection failed: {err}")


# ==============================================================================
# SECTION 3: DATABASE CONNECTION FACTORY
# ==============================================================================

def get_db_connection():
    """Establish and return a new connection to the MySQL database pod."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql-headless'),
        port=int(os.getenv('DB_PORT', 3306)),
        database=os.getenv('DB_NAME', 'restaurant_db'),
        user=os.getenv('DB_USER', 'restaurant_user'),
        password=os.getenv('DB_PASSWORD', 'Admin@123')
    )


# ==============================================================================
# SECTION 4: MENU API ENDPOINT (CATEGORIES SUPPORT)
# ==============================================================================

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """Fetch menu items optionally filtered by category (starters, main_course, snacks, beverages)."""
    # Extract category parameter from incoming request URL
    category = request.args.get('category')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Query specific category or return all active dishes
    if category and category != 'all':
        cursor.execute("SELECT * FROM menu_items WHERE category = %s AND is_available = 1", (category,))
    else:
        cursor.execute("SELECT * FROM menu_items WHERE is_available = 1")

    dishes = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(dishes), 200


# ==============================================================================
# SECTION 5: DAILY SALES & TOP DISH ANALYTICS ENDPOINT
# ==============================================================================

@app.route('/api/analytics/daily-summary', methods=['GET'])
def get_daily_analytics():
    """Calculate and return today's total revenue, order count, and top selling dish."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # SQL Query 1: Calculate total orders placed and total revenue collected today
        cursor.execute("""
            SELECT 
                COUNT(order_id) AS total_orders,
                COALESCE(SUM(total_amount), 0) AS total_sales
            FROM orders
            WHERE DATE(created_at) = CURDATE()
              AND status IN ('PAID', 'PLACED');
        """)
        summary = cursor.fetchone()

        # SQL Query 2: Identify the single most frequently ordered menu item
        cursor.execute("""
            SELECT 
                item_name,
                SUM(quantity) AS total_qty
            FROM order_items
            GROUP BY item_name
            ORDER BY total_qty DESC
            LIMIT 1;
        """)
        top_item = cursor.fetchone()

        # Send response payload to the top banner
        return jsonify({
            "status": "success",
            "date": datetime.now().strftime("%d-%b-%Y"),
            "total_orders": summary['total_orders'] if summary else 0,
            "total_sales": float(summary['total_sales']) if summary else 0.0,
            "top_selling_item": top_item['item_name'] if top_item else "No orders yet",
            "top_selling_quantity": int(top_item['total_qty']) if top_item else 0
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ==============================================================================
# SECTION 6: BILL PAYMENT & KAFKA EVENT PUBLISHER
# ==============================================================================

@app.route('/api/orders/pay', methods=['POST'])
def process_order_payment():
    """Process table checkout, calculate Indian GST (5%), save to DB, and send event to Kafka."""
    payload = request.get_json()

    table_number = payload.get('table_number', 1)
    items = payload.get('items', [])
    subtotal = float(payload.get('subtotal', 0.0))

    # Calculate Indian GST breakdown: 2.5% CGST + 2.5% SGST = 5.0% Grand Tax
    cgst = round(subtotal * 0.025, 2)
    sgst = round(subtotal * 0.025, 2)
    grand_total = round(subtotal + cgst + sgst, 2)
    payment_method = payload.get('payment_method', 'UPI')
    paid_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Insert order record with status PAID
        cursor.execute(
            "INSERT INTO orders (table_number, status, total_amount) VALUES (%s, 'PAID', %s)",
            (table_number, grand_total)
        )
        order_id = cursor.lastrowid

        # 2. Insert itemized ordered dishes into order_items table
        for item in items:
            cursor.execute(
                """INSERT INTO order_items (order_id, item_id, item_name, quantity, unit_price) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (order_id, item['id'], item['name'], item['qty'], item['price'])
            )

        # 3. Commit order and items to database first
        conn.commit()

        # 4. Construct Kafka payment payload matching consumer expectations
        event_message = {
            "order_id": order_id,
            "payment_id": f"PAY-{order_id}-{int(datetime.now().timestamp())}",
            "table_number": table_number,
            "subtotal": subtotal,
            "cgst_2_5": cgst,
            "sgst_2_5": sgst,
            "grand_total": grand_total,
            "payment_method": payment_method,
            "paid_at": paid_time,
            "items_count": len(items)
        }

        # 5. Publish real-time event to Kafka topic 'order-payments'
        if kafka_producer:
            kafka_producer.send(KAFKA_TOPIC, value=event_message)
            kafka_producer.flush()
            print(f"[Backend API] Emitted payment event to Kafka topic '{KAFKA_TOPIC}' for Order #{order_id}")

        return jsonify({
            "status": "success",
            "message": "Bill paid and Kafka payment event emitted successfully!",
            "bill_details": event_message
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ==============================================================================
# SECTION 7: SERVER RUNNER
# ==============================================================================

if __name__ == '__main__':
    # Start Flask API server listening across all pod interfaces on port 5000
    app.run(host='0.0.0.0', port=5000)