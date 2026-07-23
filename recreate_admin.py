import os
import psycopg2
import hashlib
import secrets
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def recreate_admin():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Delete existing
        cur.execute("DELETE FROM users WHERE username = 'MCM'")
        
        # Create new
        password = "++08800++"
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((salt + password).encode('utf-8'))
        new_hash = f"sha256${salt}${hash_obj.hexdigest()}"
        
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, wallet_balance, is_active) 
            VALUES ('MCM', 'superadmin@bucoinmarket.com', %s, 'Master Admin', 'superadmin', 0.00, TRUE)
        """, (new_hash,))
        
        print("✅ SuperAdmin recreated successfully!")
        print("   Username: MCM")
        print("   Password: ++08800++")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    recreate_admin()
