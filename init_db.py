import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_ijc8mWwoCz2D@ep-noisy-frost-ato3kdpv-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

def init_database():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🗄️  Dropping existing tables...")
        
        # Drop tables in correct order (due to foreign keys)
        cur.execute("DROP TABLE IF EXISTS order_items CASCADE")
        cur.execute("DROP TABLE IF EXISTS orders CASCADE")
        cur.execute("DROP TABLE IF EXISTS transactions CASCADE")
        cur.execute("DROP TABLE IF EXISTS products CASCADE")
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        cur.execute("DROP TABLE IF EXISTS settings CASCADE")
        
        print("📦 Creating tables...")
        
        # Create users table (correct column order)
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                phone VARCHAR(20),
                role VARCHAR(20) DEFAULT 'customer',
                wallet_balance DECIMAL(15,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                profile_pic VARCHAR(255)
            )
        """)
        print("✅ users table created")
        
        # Create products table
        cur.execute("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(15,2) NOT NULL,
                stock INT DEFAULT 0,
                category VARCHAR(100),
                image_url VARCHAR(255),
                created_by INT REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        print("✅ products table created")
        
        # Create transactions table
        cur.execute("""
            CREATE TABLE transactions (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES users(id),
                transaction_type VARCHAR(20) NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                balance_before DECIMAL(15,2),
                balance_after DECIMAL(15,2),
                description VARCHAR(255),
                reference_id VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        print("✅ transactions table created")
        
        # Create orders table
        cur.execute("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES users(id),
                order_number VARCHAR(50) UNIQUE NOT NULL,
                total_amount DECIMAL(15,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                payment_status VARCHAR(20) DEFAULT 'pending',
                shipping_address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ orders table created")
        
        # Create order_items table
        cur.execute("""
            CREATE TABLE order_items (
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id),
                quantity INT NOT NULL,
                price DECIMAL(15,2) NOT NULL,
                total DECIMAL(15,2) NOT NULL
            )
        """)
        print("✅ order_items table created")
        
        # Create settings table
        cur.execute("""
            CREATE TABLE settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                description VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ settings table created")
        
        print("\n📝 Inserting default data...")
        
        # Insert SuperAdmin (Password: ++08800++)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, wallet_balance, is_active) 
            VALUES (
                'MCM', 
                'superadmin@bucoinmarket.com', 
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpbGBmZFVH6ZJ6', 
                'Master Admin', 
                'superadmin', 
                0.00, 
                TRUE
            ) ON CONFLICT (username) DO NOTHING
        """)
        print("✅ SuperAdmin inserted (username: MCM, password: ++08800++)")
        
        # Insert settings
        cur.execute("""
            INSERT INTO settings (setting_key, setting_value, description) VALUES
            ('buc_exchange_rate', '1.00', '1 BUC = 1 BIF'),
            ('site_name', 'BuCoinMarket', 'Website name'),
            ('site_description', 'The Future of Cashless Shopping', 'Website description'),
            ('maintenance_mode', 'false', 'Maintenance mode status')
            ON CONFLICT (setting_key) DO NOTHING
        """)
        print("✅ Default settings inserted")
        
        print("\n" + "="*50)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\n📊 Tables created:")
        
        # Show tables
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        tables = cur.fetchall()
        for table in tables:
            print(f"   📋 {table[0]}")
        
        print("\n👤 SuperAdmin Credentials:")
        print("   Username: MCM")
        print("   Password: ++08800++")
        print("\n⚙️  Settings:")
        
        cur.execute("SELECT setting_key, setting_value FROM settings")
        settings = cur.fetchall()
        for key, value in settings:
            print(f"   {key}: {value}")
        
        cur.close()
        conn.close()
        
        print("\n🚀 You can now deploy your application on Render!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database()
