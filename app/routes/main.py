from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models import Product, Order, Transaction, Setting
from app import db
from datetime import datetime
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Debug - check template folder
    print(f"Template folder: {current_app.template_folder}")
    print(f"Files in template folder: {os.listdir(current_app.template_folder)}")
    
    products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(12).all()
    
    site_name = Setting.query.filter_by(setting_key='site_name').first()
    site_description = Setting.query.filter_by(setting_key='site_description').first()
    exchange_rate = Setting.query.filter_by(setting_key='buc_exchange_rate').first()
    
    return render_template('index.html', 
                         products=products,
                         site_name=site_name.setting_value if site_name else 'BuCoinMarket',
                         site_description=site_description.setting_value if site_description else 'The Future of Cashless Shopping',
                         exchange_rate=exchange_rate.setting_value if exchange_rate else '1.00')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    total_orders = Order.query.filter_by(user_id=current_user.id).count()
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(10).all()
    
    balance = current_user.wallet_balance
    
    exchange_rate = Setting.query.filter_by(setting_key='buc_exchange_rate').first()
    buc_rate = float(exchange_rate.setting_value) if exchange_rate else 1.00
    
    return render_template('dashboard.html',
                         total_orders=total_orders,
                         recent_orders=recent_orders,
                         transactions=transactions,
                         balance=balance,
                         buc_rate=buc_rate)
