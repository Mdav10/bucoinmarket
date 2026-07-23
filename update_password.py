import os
import psycopg2
from dotenv import load_dotenv
import hashlib
import secrets

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def update_superadmin_password():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Generate new password hash
        password = "++08800++"
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((salt + password).encode('utf-8'))
        new_hash = f"sha256${salt}${hash_obj.hexdigest()}"
        
        # Update SuperAdmin password
        cur.execute("""
            UPDATE users 
            SET password_hash = %s 
            WHERE username = 'MCM'
        """, (new_hash,))
        
        if cur.rowcount > 0:
            print("✅ SuperAdmin password updated successfully!")
            print(f"   Username: MCM")
            print(f"   Password: ++08800++")
            print(f"   New Hash: {new_hash[:50]}...")
        else:
            print("⚠️ SuperAdmin user not found. Creating new one...")
            cur.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, wallet_balance, is_active) 
                VALUES ('MCM', 'superadmin@bucoinmarket.com', %s, 'Master Admin', 'superadmin', 0.00, TRUE)
            """, (new_hash,))
            print("✅ SuperAdmin created!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_superadmin_password()
