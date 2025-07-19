# app/routes.py
from flask import render_template, flash, redirect, url_for, Blueprint, session, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import Product, User, Order, OrderItem
from app.forms import RegistrationForm, LoginForm
from flask import request

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    # Get the search query from the URL, if it exists
    query = request.args.get('query', '')
    
    if query:
        # If there is a search query, filter products by name
        # The '%' signs are wildcards, so it finds partial matches
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        # If there is no search query, show all products
        products = Product.query.all()
        
    # Pass the products and the query string to the template
    return render_template('index.html', title='Home', products=products, query=query)

# --- AUTH ROUTES ---
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- SHOPPING CART & ORDER ROUTES ---
@bp.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        product = Product.query.get_or_404(product_id)
        cart[product_id_str] = {'name': product.name, 'price': float(product.price), 'quantity': 1, 'image': product.image_file}
    session['cart'] = cart
    flash(f"{cart[product_id_str]['name']} has been added to your cart.", 'success')
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', title='Shopping Cart', cart=cart, total_price=total_price)

@bp.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        session['cart'] = cart
        flash('Item removed from cart.', 'success')
    return redirect(url_for('main.view_cart'))

# --- SIMPLIFIED CHECKOUT ---
@bp.route('/checkout')
@login_required # We keep this to ensure a user is logged in
def checkout():
    # Clear the cart from the session
    session.pop('cart', None)
    # Redirect to a simple success page
    return render_template('order_success.html', title='Thank You!')
