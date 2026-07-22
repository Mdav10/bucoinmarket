from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Setting, Product, Order, Transaction
from werkzeug.security import generate_password_hash
from decimal import Decimal

superadmin_bp = Blueprint('superadmin', __name__)

@superadmin_bp.before_request
def superadmin_required():
    if not current_user.is_authenticated or current_user.role != 'superadmin':
        flash('Super Admin access required.', 'danger')
        return redirect(url_for('main.index'))

@superadmin_bp.route('/')
def dashboard():
    total_users = User.query.count()
    total_admins = User.query.filter(User.role.in_(['admin', 'superadmin'])).count()
    total_customers = User.query.filter_by(role='customer').count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_transactions = Transaction.query.count()
    
    return render_template('superadmin/dashboard.html',
                         total_users=total_users,
                         total_admins=total_admins,
                         total_customers=total_customers,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_transactions=total_transactions)

@superadmin_bp.route('/users')
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('superadmin/users.html', users=users)

@superadmin_bp.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'customer')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('superadmin.users'))
    
    return render_template('superadmin/add_user.html')

@superadmin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        site_description = request.form.get('site_description')
        buc_exchange_rate = request.form.get('buc_exchange_rate')
        
        settings = {
            'site_name': site_name,
            'site_description': site_description,
            'buc_exchange_rate': buc_exchange_rate
        }
        
        for key, value in settings.items():
            setting = Setting.query.filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = value
            else:
                setting = Setting(setting_key=key, setting_value=value)
                db.session.add(setting)
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('superadmin.settings'))
    
    site_name = Setting.query.filter_by(setting_key='site_name').first()
    site_description = Setting.query.filter_by(setting_key='site_description').first()
    buc_exchange_rate = Setting.query.filter_by(setting_key='buc_exchange_rate').first()
    
    return render_template('superadmin/settings.html',
                         site_name=site_name.setting_value if site_name else '',
                         site_description=site_description.setting_value if site_description else '',
                         buc_exchange_rate=buc_exchange_rate.setting_value if buc_exchange_rate else '1.00')
