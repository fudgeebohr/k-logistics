import psycopg2
import bcrypt
import getpass

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "logistics_tracking",
    "user": "fudge",
    "password": "FugenPG-2025",
}

print("=== K Logistics™ Admin Setup ===")
print("Create your admin account (run once):")
username = input("Enter admin username: ").strip()
password = getpass.getpass("Enter admin password: ").strip()

if not username or not password:
    print("❌ Username and password required!")
    exit(1)

try:
    # Generate secure hash
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')
    
    # Connect and create user
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT INTO users (username, password_hash) 
        VALUES (%s, %s) 
        ON CONFLICT (username) DO UPDATE SET 
            password_hash = %s, 
            created_at = CURRENT_TIMESTAMP
    """, (username, hashed_str, hashed_str))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Admin user '{username}' created successfully!")
    print("💡 You can now run the main app and login with these credentials.")
    
except Exception as e:
    print(f"❌ Error: {e}")
