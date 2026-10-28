# ==============================================================================
# SECTION 1: IMPORTS & CORE MODULES
# ==============================================================================

# OS module to read environment variables set by Kubernetes manifests
import os

# JSON serializer to parse incoming Kafka byte events
import json

# Time module to manage retry delays and timeouts
import time

# Signal handling for clean pod termination during rollout restarts
import signal

# Kafka Consumer client to subscribe to payment event streams
from kafka import KafkaConsumer

# PooledDB to manage reusable connection pools to MySQL
from dbutils.pooled_db import PooledDB

# PyMySQL client to interact with MySQL database
import pymysql


# ==============================================================================
# SECTION 2: CONFIGURATION & ENVIRONMENT VARIABLES
# ==============================================================================

# Database host address (default: headless service in Kubernetes)
DB_HOST = os.getenv("DB_HOST", "mysql-headless")

# Database user credential
DB_USER = os.getenv("DB_USER", "restaurant_user")

# Database password
DB_PASSWORD = os.getenv("DB_PASSWORD", "Admin@123")

# Target database name
DB_NAME = os.getenv("DB_NAME", "restaurant_db")

# Kafka cluster service broker address
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-service:9092")

# Kafka topic dedicated to receiving payment events from backend
KAFKA_TOPIC = "order-payments"

# Unique consumer group ID to track commit offsets
CONSUMER_GROUP = "haris-payment-processors"


# ==============================================================================
# SECTION 3: GRACEFUL SHUTDOWN SIGNAL HANDLING
# ==============================================================================

# Global boolean flag to control consumer processing loop
running = True

def handle_shutdown(signum, frame):
    """Handle SIGINT and SIGTERM to stop listening and close sockets cleanly."""
    global running
    print("\n[Hari's Restaurant Worker] Graceful shutdown initiated...", flush=True)
    running = False

# Register signal listeners for container stops
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# ==============================================================================
# SECTION 4: DATABASE CONNECTION POOL WITH RETRY LOGIC
# ==============================================================================

def get_db_pool():
    """Create and return a MySQL connection pool with persistent retry logic."""
    while running:
        try:
            pool = PooledDB(
                creator=pymysql,
                maxconnections=5,
                mincached=1,
                maxcached=3,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            print("[Hari's Restaurant Worker] Connected to MySQL database successfully.", flush=True)
            return pool
        except Exception as e:
            print(f"[Hari's Restaurant Worker] MySQL waiting: {e}. Retrying in 5s...", flush=True)
            time.sleep(5)
    return None

# Initialize persistent database pool
db_pool = get_db_pool()


# ==============================================================================
# SECTION 5: KAFKA CONSUMER INITIALIZATION WITH RETRY LOGIC
# ==============================================================================

def get_consumer():
    """Create and return a KafkaConsumer instance with persistent connection retry."""
    while running:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP.split(","),
                group_id=CONSUMER_GROUP,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                consumer_timeout_ms=1000
            )
            print(f"[Hari's Restaurant Worker] Subscribed to topic: {KAFKA_TOPIC}", flush=True)
            return consumer
        except Exception as e:
            print(f"[Hari's Restaurant Worker] Kafka waiting: {e}. Retrying in 5s...", flush=True)
            time.sleep(5)
    return None

# Initialize consumer instance
consumer = get_consumer()


# ==============================================================================
# SECTION 6: PAYMENT EVENT PROCESSING & POWERSHELL DISPLAY
# ==============================================================================

def process_and_mark_paid(event):
    """Update order status in MySQL, record tax audit in payments table, and print details."""
    order_id = event.get("order_id")
    table_number = event.get("table_number", 1)
    subtotal = float(event.get("subtotal", 0.0))
    cgst = float(event.get("cgst_2_5", round(subtotal * 0.025, 2)))
    sgst = float(event.get("sgst_2_5", round(subtotal * 0.025, 2)))
    grand_total = float(event.get("grand_total", round(subtotal + cgst + sgst, 2)))
    payment_method = event.get("payment_method", "UPI")
    paid_at = event.get("paid_at", time.strftime("%Y-%m-%d %H:%M:%S"))
    items_count = event.get("items_count", 0)

    if not order_id:
        return False

    # Obtain connection from pool
    conn = db_pool.connection()
    try:
        with conn.cursor() as cursor:
            # 1. Update the parent order status to PAID
            cursor.execute(
                "UPDATE orders SET status = 'PAID', total_amount = %s WHERE order_id = %s;",
                (grand_total, order_id)
            )

            # 2. Insert or update transaction audit record into payments table
            cursor.execute("""
                INSERT INTO payments 
                (order_id, table_number, subtotal, cgst, sgst, grand_total, payment_method, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'PAID')
                ON DUPLICATE KEY UPDATE 
                    payment_status = 'PAID',
                    grand_total = VALUES(grand_total);
            """, (order_id, table_number, subtotal, cgst, sgst, grand_total, payment_method))

        # 3. Print a clean, formatted receipt to PowerShell console in real-time
        print("\n" + "=" * 60, flush=True)
        print("💰 [KAFKA EVENT CONSUMED]: BILL_PAID SUCCESSFUL", flush=True)
        print("=" * 60, flush=True)
        print(f"Order Reference : #{order_id}", flush=True)
        print(f"Dining Table    : Table {table_number}", flush=True)
        print(f"Timestamp       : {paid_at}", flush=True)
        print(f"Dishes Count    : {items_count} items", flush=True)
        print("-" * 60, flush=True)
        print(f"Food Subtotal   : INR {subtotal:.2f}", flush=True)
        print(f"CGST (2.5%)     : INR {cgst:.2f}", flush=True)
        print(f"SGST (2.5%)     : INR {sgst:.2f}", flush=True)
        print(f"Total Tax (5%)  : INR {(cgst + sgst):.2f}", flush=True)
        print("-" * 60, flush=True)
        print(f"Grand Total     : INR {grand_total:.2f}", flush=True)
        print(f"Payment Method  : {payment_method}", flush=True)
        print(f"Database Status : ORDERS & PAYMENTS TABLES UPDATED", flush=True)
        print("=" * 60 + "\n", flush=True)

        return True

    except Exception as e:
        print(f"[Hari's Restaurant Worker] Error executing DB queries: {e}", flush=True)
        return False
    finally:
        # Return connection back to pool
        conn.close()


# ==============================================================================
# SECTION 7: MAIN EVENT LISTENER LOOP
# ==============================================================================

print("[Hari's Restaurant Worker] Payment listener running and ready...", flush=True)

try:
    while running:
        if not consumer:
            break
        for message in consumer:
            if not running:
                break
            # Process incoming message, and commit offset to Kafka only on successful DB write
            if process_and_mark_paid(message.value):
                consumer.commit()
finally:
    if consumer:
        consumer.close()
    print("[Hari's Restaurant Worker] Clean exit completed.", flush=True)