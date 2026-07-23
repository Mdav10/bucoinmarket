from app import db
from flask_login import UserMixin
from datetime import datetime
import hashlib
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='customer')
    wallet_balance = db.Column(db.Numeric(15, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    profile_pic = db.Column(db.String(255))
    
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    products = db.relationship('Product', backref='creator', lazy=True)
    
    def set_password(self, password):
        """Hash password using SHA256"""
        # Use SHA256 instead of bcrypt to avoid compatibility issues
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256()
        hash_obj.update((salt + password).encode('utf-8'))
        self.password_hash = f"sha256${salt}${hash_obj.hexdigest()}"
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        
        try:
            # Parse the stored hash
            parts = self.password_hash.split('$')
            if len(parts) == 3 and parts[0] == 'sha256':
                _, salt, stored_hash = parts
                # Compute hash of provided password with same salt
                hash_obj = hashlib.sha256()
                hash_obj.update((salt + password).encode('utf-8'))
                computed_hash = hash_obj.hexdigest()
                return computed_hash == stored_hash
            else:
                # Fallback for bcrypt or other formats
                from werkzeug.security import check_password_hash
                return check_password_hash(self.password_hash, password)
        except Exception as e:
            return False
    
    def has_role(self, role):
        return self.role == role or self.role == 'superadmin'
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance_before = db.Column(db.Numeric(15, 2))
    balance_after = db.Column(db.Numeric(15, 2))
    description = db.Column(db.String(255))
    reference_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Transaction {self.id}>'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    shipping_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def generate_order_number(self):
        return f'BUC-{datetime.utcnow().strftime("%Y%m%d")}-{secrets.token_hex(4).upper()}'
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    total = db.Column(db.Numeric(15, 2), nullable=False)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class Setting(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Setting {self.setting_key}>'
