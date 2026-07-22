from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Transaction, Setting
from datetime import datetime
from decimal import Decimal

wallet_bp = Blueprint('wallet', __name__)

@wallet_bp.route('/')
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    
    exchange_rate = Setting.query.filter_by(setting_key='buc_exchange_rate').first()
    buc_rate = float(exchange_rate.setting_value) if exchange_rate else 1.00
    
    return render_template('wallet/index.html', 
                         transactions=transactions,
                         balance=current_user.wallet_balance,
                         buc_rate=buc_rate)

@wallet_bp.route('/topup', methods=['GET', 'POST'])
@login_required
def topup():
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method')
        
        if amount <= 0:
            flash('Please enter a valid amount.', 'danger')
            return redirect(url_for('wallet.topup'))
        
        exchange_rate = Setting.query.filter_by(setting_key='buc_exchange_rate').first()
        buc_rate = float(exchange_rate.setting_value) if exchange_rate else 1.00
        
        buc_amount = amount * buc_rate
        
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type='topup',
            amount=buc_amount,
            balance_before=current_user.wallet_balance,
            balance_after=current_user.wallet_balance + buc_amount,
            description=f'Topup via {payment_method} - {amount} BIF = {buc_amount} BUC',
            status='completed',
            completed_at=datetime.utcnow()
        )
        
        current_user.wallet_balance += buc_amount
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully added {buc_amount} BUC to your wallet!', 'success')
        return redirect(url_for('wallet.index'))
    
    return render_template('wallet/topup.html', balance=current_user.wallet_balance)
