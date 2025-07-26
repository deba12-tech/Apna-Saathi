from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
from datetime import datetime
from ocr import extract_text_from_image
from chatbot import get_chatbot_response
from recommendation_engine import get_supplier_recommendations

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///apna_saathi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'vendor' or 'supplier'
    phone = db.Column(db.String(15))
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text)  # JSON string of items
    rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    address = db.Column(db.String(200))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    needs = db.Column(db.Text)  # JSON string of needs
    location = db.Column(db.String(100))

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            phone=phone,
            location=location
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'supplier':
        supplier = Supplier.query.filter_by(user_id=current_user.id).first()
        return render_template('supplier_dashboard.html', supplier=supplier)
    else:
        vendor = Vendor.query.filter_by(user_id=current_user.id).first()
        return render_template('vendor_dashboard.html', vendor=vendor)

@app.route('/vendors')
def vendors():
    vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=vendors)

@app.route('/suppliers')
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/debug')
def debug():
    return render_template('debug.html')

@app.route('/test-static')
def test_static():
    return render_template('test_static.html')

# API Routes
@app.route('/api/suppliers')
def api_suppliers():
    suppliers = Supplier.query.all()
    suppliers_data = []
    for supplier in suppliers:
        user = User.query.get(supplier.user_id)
        suppliers_data.append({
            'id': supplier.id,
            'business_name': supplier.business_name,
            'items': json.loads(supplier.items) if supplier.items else [],
            'rating': supplier.rating,
            'total_ratings': supplier.total_ratings,
            'location': user.location,
            'description': supplier.description
        })
    return jsonify(suppliers_data)

@app.route('/api/vendors', methods=['GET', 'POST'])
def api_vendors():
    if request.method == 'POST':
        data = request.json
        vendor = Vendor.query.filter_by(user_id=current_user.id).first()
        if vendor:
            vendor.needs = json.dumps(data.get('needs', []))
        else:
            vendor = Vendor(
                user_id=current_user.id,
                business_name=data.get('business_name', ''),
                needs=json.dumps(data.get('needs', [])),
                location=data.get('location', '')
            )
            db.session.add(vendor)
        db.session.commit()
        return jsonify({'message': 'Vendor needs updated successfully'})
    
    vendors = Vendor.query.all()
    vendors_data = []
    for vendor in vendors:
        user = User.query.get(vendor.user_id)
        vendors_data.append({
            'id': vendor.id,
            'business_name': vendor.business_name,
            'needs': json.loads(vendor.needs) if vendor.needs else [],
            'location': vendor.location
        })
    return jsonify(vendors_data)



@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload():
    """Handle bill upload and OCR processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file temporarily
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Validate file
        is_valid, error_msg = ocr.validate_image_file(filepath)
        if not is_valid:
            os.remove(filepath)
            return jsonify({'error': error_msg}), 400
        
        # Extract text using OCR
        extracted_text = ocr.extract_text_from_image(filepath)
        
        # Parse raw materials from text
        raw_materials = ocr.parse_raw_materials(extracted_text)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'raw_materials': raw_materials
        })
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.json
    message = data.get('message', '')
    
    # Get chatbot response
    response = get_chatbot_response(message)
    
    # Save chat to database
    chat = Chat(
        user_id=current_user.id,
        message=message,
        response=response
    )
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({'response': response})

@app.route('/api/recommendations')
@login_required
def api_recommendations():
    if current_user.role != 'vendor':
        return jsonify({'error': 'Only vendors can get recommendations'}), 403
    
    vendor = Vendor.query.filter_by(user_id=current_user.id).first()
    if not vendor:
        return jsonify({'error': 'Vendor profile not found'}), 404
    
    needs = json.loads(vendor.needs) if vendor.needs else []
    recommendations = get_supplier_recommendations(needs, vendor.location)
    
    return jsonify(recommendations)



# Initialize database
with app.app_context():
    db.create_all()
    
    # Add sample data if database is empty
    if not User.query.first():
        # Create sample suppliers
        supplier1 = User(
            username='fresh_veggies',
            email='fresh@example.com',
            password_hash=generate_password_hash('password123'),
            role='supplier',
            phone='9876543210',
            location='Mumbai'
        )
        db.session.add(supplier1)
        db.session.commit()
        
        supplier_profile1 = Supplier(
            user_id=supplier1.id,
            business_name='Fresh Vegetables Co.',
            items=json.dumps(['onion', 'tomato', 'potato', 'carrot']),
            rating=4.5,
            total_ratings=25,
            description='Fresh vegetables delivered daily',
            address='Mumbai Central, Mumbai'
        )
        db.session.add(supplier_profile1)
        
        # Create sample vendor
        vendor1 = User(
            username='street_food_king',
            email='vendor@example.com',
            password_hash=generate_password_hash('password123'),
            role='vendor',
            phone='9876543211',
            location='Mumbai'
        )
        db.session.add(vendor1)
        db.session.commit()
        
        vendor_profile1 = Vendor(
            user_id=vendor1.id,
            business_name='Street Food King',
            needs=json.dumps(['onion', 'tomato', 'potato']),
            location='Mumbai'
        )
        db.session.add(vendor_profile1)
        
        # Create West Bengal vendors
        vendor2 = User(
            username='siliguri_food_corner',
            email='siliguri@example.com',
            password_hash=generate_password_hash('password123'),
            role='vendor',
            phone='9876543212',
            location='Siliguri'
        )
        db.session.add(vendor2)
        db.session.commit()
        
        vendor_profile2 = Vendor(
            user_id=vendor2.id,
            business_name='Siliguri Food Corner',
            needs=json.dumps(['rice', 'flour', 'oil', 'spices', 'onion', 'tomato']),
            location='Siliguri'
        )
        db.session.add(vendor_profile2)
        
        vendor3 = User(
            username='darjeeling_street_food',
            email='darjeeling@example.com',
            password_hash=generate_password_hash('password123'),
            role='vendor',
            phone='9876543213',
            location='Darjeeling'
        )
        db.session.add(vendor3)
        db.session.commit()
        
        vendor_profile3 = Vendor(
            user_id=vendor3.id,
            business_name='Darjeeling Street Food',
            needs=json.dumps(['potato', 'carrot', 'onion', 'tomato', 'spices']),
            location='Darjeeling'
        )
        db.session.add(vendor_profile3)
        
        vendor4 = User(
            username='jalpaiguri_food_hub',
            email='jalpaiguri@example.com',
            password_hash=generate_password_hash('password123'),
            role='vendor',
            phone='9876543214',
            location='Jalpaiguri'
        )
        db.session.add(vendor4)
        db.session.commit()
        
        vendor_profile4 = Vendor(
            user_id=vendor4.id,
            business_name='Jalpaiguri Food Hub',
            needs=json.dumps(['rice', 'flour', 'oil', 'onion', 'tomato', 'potato']),
            location='Jalpaiguri'
        )
        db.session.add(vendor_profile4)
        
        vendor5 = User(
            username='cooch_behar_street_vendor',
            email='coochbehar@example.com',
            password_hash=generate_password_hash('password123'),
            role='vendor',
            phone='9876543215',
            location='Cooch Behar'
        )
        db.session.add(vendor5)
        db.session.commit()
        
        vendor_profile5 = Vendor(
            user_id=vendor5.id,
            business_name='Cooch Behar Street Vendor',
            needs=json.dumps(['rice', 'flour', 'oil', 'spices', 'onion', 'tomato', 'potato']),
            location='Cooch Behar'
        )
        db.session.add(vendor_profile5)
        
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True) 