from flask import Flask, request, jsonify, render_template # Import render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
# Flask will automatically look for templates in a 'templates' folder
# and static files (CSS, JS) in a 'static' folder next to app.py
app = Flask(__name__)

# CORS configuration - you can remove or simplify this if all requests are from the same origin,
# but it's good to keep if you might access the API from other sources later.
CORS(app, resources={r"/api/*": {"origins": ["*"]}}) # Use "*" for simplicity during development if needed, but be specific in production

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}

# Room limits (can be fetched from DB later for dynamic management)
ROOM_LIMITS = {
    "Single": 5,
    "Double": 3,
    "Suite": 2
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# --- Frontend Serving Route ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

# --- API Endpoints ---
@app.route('/api/bookings', methods=['POST'])
def book_room():
    """API endpoint to book a room."""
    data = request.get_json()
    guest_name = data.get('guestName')
    room_type = data.get('roomType')

    if not guest_name or not guest_name.strip():
        return jsonify({"message": "Guest name is required."}), 400
    if room_type not in ROOM_LIMITS:
        return jsonify({"message": "Invalid room type."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection error."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) AS booked_count FROM bookings WHERE room_type = %s", (room_type,))
        result = cursor.fetchone()
        booked_count = result['booked_count']

        if booked_count >= ROOM_LIMITS[room_type]:
            return jsonify({"message": f"{room_type} rooms are fully booked."}), 400

        cursor.execute(
            "INSERT INTO bookings (guest_name, room_type) VALUES (%s, %s)",
            (guest_name, room_type)
        )
        conn.commit()
        return jsonify({"message": "Room booked successfully!"}), 201

    except Error as e:
        print(f"Error during booking: {e}")
        conn.rollback()
        return jsonify({"message": "Server error during booking."}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/bookings', methods=['GET'])
def get_all_bookings():
    """API endpoint to retrieve all bookings."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection error."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, guest_name, room_type, booking_date FROM bookings ORDER BY booking_date DESC")
        bookings = cursor.fetchall()
        
        for booking in bookings:
            if isinstance(booking['booking_date'], datetime):
                booking['booking_date'] = booking['booking_date'].isoformat()

        return jsonify(bookings), 200

    except Error as e:
        print(f"Error fetching bookings: {e}")
        return jsonify({"message": "Server error fetching bookings."}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/availability/<string:room_type>', methods=['GET'])
def check_availability(room_type):
    """API endpoint to check room availability."""
    if room_type not in ROOM_LIMITS:
        return jsonify({"message": "Invalid room type specified."}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Database connection error."}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS booked_count FROM bookings WHERE room_type = %s", (room_type,))
        result = cursor.fetchone()
        booked_count = result['booked_count']
        
        limit = ROOM_LIMITS[room_type]
        available = limit - booked_count

        response_data = {
            "roomType": room_type,
            "available": available,
            "total": limit
        }
        return jsonify(response_data), 200

    except Error as e:
        print(f"Error checking availability: {e}")
        return jsonify({"message": "Server error checking availability."}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)