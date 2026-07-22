from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, User
from decimal import Decimal

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def admin_required():
    if not current_user.is_authenticated or not current_user.has_role('admin'):
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/')
def dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         pending_orders=pending_orders)
