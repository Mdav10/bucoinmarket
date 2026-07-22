from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Order, OrderItem, Product, Transaction
from decimal import Decimal
import secrets
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    
    if not product.is_active:
        flash('This product is not available.', 'danger')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    if product.stock < quantity:
        flash('Not enough stock available.', 'danger')
        return redirect(url_for('products.view_product', product_id=product_id))
    
    total = product.price * quantity
    
    if current_user.wallet_balance < total:
        flash('Insufficient wallet balance. Please top up your wallet.', 'danger')
        return redirect(url_for('wallet.topup'))
    
    order = Order(
        user_id=current_user.id,
        order_number=Order.generate_order_number(order),
        total_amount=total,
        status='pending',
        payment_status='paid'
    )
    
    order_item = OrderItem(
        product_id=product.id,
        quantity=quantity,
        price=product.price,
        total=total
    )
    order.items.append(order_item)
    
    current_user.wallet_balance -= total
    
    transaction = Transaction(
        user_id=current_user.id,
        transaction_type='payment',
        amount=total,
        balance_before=current_user.wallet_balance + total,
        balance_after=current_user.wallet_balance,
        description=f'Purchase: {product.name} x{quantity}',
        reference_id=order.order_number,
        status='completed',
        completed_at=datetime.utcnow()
    )
    
    product.stock -= quantity
    
    db.session.add(order)
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Order #{order.order_number} placed successfully!', 'success')
    return redirect(url_for('orders.view', order_id=order.id))

@orders_bp.route('/<int:order_id>')
@login_required
def view(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.has_role('admin'):
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('orders/view.html', order=order)

@orders_bp.route('/history')
@login_required
def history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/history.html', orders=orders)
