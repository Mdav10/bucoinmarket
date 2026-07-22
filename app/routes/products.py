from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem
from decimal import Decimal
import os
from werkzeug.utils import secure_filename

products_bp = Blueprint('products', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@products_bp.route('/')
def list_products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
    
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('products/list.html', products=products)

@products_bp.route('/<int:product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/view.html', product=product)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.has_role('admin'):
        flash('You do not have permission to add products.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock', 0)
        category = request.form.get('category')
        image = request.files.get('image')
        
        if not all([name, price]):
            flash('Name and price are required.', 'danger')
            return redirect(url_for('products.add_product'))
        
        product = Product(
            name=name,
            description=description,
            price=Decimal(price),
            stock=int(stock),
            category=category,
            created_by=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        if image and allowed_file(image.filename):
            filename = secure_filename(f"{product.id}_{image.filename}")
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            product.image_url = filename
            db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('products.view_product', product_id=product.id))
    
    return render_template('products/add.html')
