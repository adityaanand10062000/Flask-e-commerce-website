# app/models.py
from datetime import datetime
from app import db, login_manager, bcrypt
from flask_login import UserMixin

# This function is required by Flask-Login to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# app/models.py


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # <-- ADD THIS LINE
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='customer', lazy=True)

    # ... (the rest of the User model remains the same)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False) # For price accuracy
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    stock = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # This relationship links an Order back to its OrderItems
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Order('Order #{self.id}', 'Date: {self.order_date}')"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_per_unit = db.Column(db.Numeric(10, 2), nullable=False) # Store price at time of order
    
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # This gives us easy access to the Product object from an OrderItem
    product = db.relationship('Product')

    def __repr__(self):
        return f"OrderItem('Product ID: {self.product_id}', 'Quantity: {self.quantity}')"