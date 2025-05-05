from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from sqlalchemy import func, case
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import jsonify
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "my secret key"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "loginFunction"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "error"

@login_manager.unauthorized_handler
def unauthorized():
    flash("Please login to access this page.", "error")
    return redirect(url_for('loginFunction'))

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    role = db.Column(db.String(100), default="user")
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def generate_password(self, simple_password):
        self.password_hash = generate_password_hash(simple_password)
    
    def check_password(self, simple_password):
        return check_password_hash(self.password_hash, simple_password)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50))
    unit = db.Column(db.String(20), nullable=False)
    returnable = db.Column(db.Boolean, default=True)
    selling_price = db.Column(db.Float)
    cost_price = db.Column(db.Float)
    tax_rate = db.Column(db.Float)
    quantity_in_hand = db.Column(db.Integer, default=0)
    quantity_to_receive = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=10)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    returnable = db.Column(db.Boolean, default=False)
    unit = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    attributes = db.relationship('GroupAttribute', backref='group', cascade='all, delete-orphan')

class GroupAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    attribute_name = db.Column(db.String(100), nullable=False)
    options = db.Column(db.Text, nullable=False)  

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to access this page.", "error")
            return redirect(url_for("loginFunction"))
        if current_user.role != "admin":
            flash("Access denied: Admin privileges required for this operation.", "error")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/register", methods=["POST","GET"])
def registerFunction():
    if request.method=="POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        country = request.form.get("country")
        state = request.form.get("state")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please use a different email.", "error")
            return redirect(url_for("registerFunction"))

        user_object = User(
            username=username,
            email=email,
            phone=phone,
            country=country,
            state=state
        )
        user_object.generate_password(password)
        db.session.add(user_object)
        db.session.commit()

        flash("Registration successful! Please login to continue.", "success")
        return redirect(url_for("loginFunction"))

    return render_template("signup.html")

@app.route("/login",methods=["POST","GET"])
def loginFunction():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_object = User.query.filter_by(email=email).first()

        if user_object and user_object.check_password(password):
            login_user(user_object)
            user_object.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome back, {user_object.username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for("loginFunction"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        flash(f"Goodbye, {current_user.username}! You have been logged out.", "success")
        logout_user()
    return redirect(url_for("loginFunction"))

@app.route('/')
def home():
    company_name = "InventoryHub"
    return render_template("index.html", 
    user=current_user, 
                         company_name=company_name,
                         is_authenticated=current_user.is_authenticated)

@app.route('/about')
def about():
    return render_template("about_us.html")


@app.route('/dashboard')
@login_required
def dashboard():
    flash(f"Welcome to your dashboard, {current_user.username}!", "info")
    
    total_items = Item.query.count()
    total_inventory_value = db.session.query(
        func.sum(case((Item.cost_price.isnot(None), 
                      Item.quantity_in_hand * Item.cost_price), else_=0))
    ).scalar() or 0
    
    avg_item_value = total_inventory_value / total_items if total_items > 0 else 0
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
    items_to_receive = Item.query.filter(Item.quantity_to_receive > 0).count()
    high_value_items = Item.query.filter(Item.cost_price.isnot(None), 
                                       Item.cost_price > 1000).count()
    returnable_items = Item.query.filter_by(returnable=True).count()
    non_returnable_items = Item.query.filter_by(returnable=False).count()

    top_value_items = db.session.query(Item)\
        .filter(Item.cost_price.isnot(None), Item.quantity_in_hand > 0)\
        .order_by((Item.cost_price * Item.quantity_in_hand).desc())\
        .limit(5).all()

    top_margin_items = db.session.query(
        Item,
        ((Item.selling_price - Item.cost_price) / Item.cost_price * 100).label('margin')
    ).filter(
        Item.cost_price.isnot(None),
        Item.selling_price.isnot(None),
        Item.cost_price > 0
    ).order_by(((Item.selling_price - Item.cost_price) / Item.cost_price).desc())\
    .limit(5).all()

    tax_distribution = db.session.query(
        Item.tax_rate,
        func.count(Item.id).label('count')
    ).group_by(Item.tax_rate)\
    .order_by(Item.tax_rate)\
    .all()

    type_filter = request.args.get('typeFilter')
    returnable_filter = request.args.get('returnableFilter')
    sort_by = request.args.get('sortBy', 'created_at')
    sort_order = request.args.get('sortOrder', 'desc')

    groups_query = Group.query

    if type_filter:
        groups_query = groups_query.filter(Group.type == type_filter)
    
    if returnable_filter:
        returnable_value = returnable_filter.lower() == 'true'
        groups_query = groups_query.filter(Group.returnable == returnable_value)

    if sort_by == 'name':
        order_column = Group.name
    else:  
        order_column = Group.created_at
    
    if sort_order == 'desc':
        groups_query = groups_query.order_by(order_column.desc())
    else:
        groups_query = groups_query.order_by(order_column.asc())

    total_groups = groups_query.count()
    goods_groups = groups_query.filter_by(type='goods').count()
    service_groups = groups_query.filter_by(type='service').count()
    returnable_groups = groups_query.filter_by(returnable=True).count()
    recent_groups = groups_query.limit(5).all()

    unit_distribution = db.session.query(
        Group.unit,
        func.count(Group.id).label('count')
    ).group_by(Group.unit).all()

    groups_with_attributes = db.session.query(
        Group,
        func.count(GroupAttribute.id).label('attribute_count')
    ).join(GroupAttribute).group_by(Group.id)\
    .order_by(func.count(GroupAttribute.id).desc())\
    .limit(5).all()

    return render_template(
        "dashboard.html",
        total_items=total_items,
        total_inventory_value=total_inventory_value,
        avg_item_value=avg_item_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        items_to_receive=items_to_receive,
        high_value_items=high_value_items,
        returnable_items=returnable_items,
        non_returnable_items=non_returnable_items,
        top_value_items=top_value_items,
        top_margin_items=top_margin_items,
        tax_distribution=tax_distribution,
        total_groups=total_groups,
        goods_groups=goods_groups,
        service_groups=service_groups,
        returnable_groups=returnable_groups,
        recent_groups=recent_groups,
        unit_distribution=unit_distribution,
        groups_with_attributes=groups_with_attributes,
        show_sidebar=True
    )

@app.route('/inventory')
@login_required
def inventory():
    flash("Viewing inventory management section.", "info")
    return render_template("inventory.html", show_sidebar=True)

@app.route('/inventory/add-item', methods=['GET', 'POST'])
@login_required
def item_form():
    if request.method == 'POST':
        name = request.form['item-name']
        sku = request.form['item-sku']
        unit = request.form['item-unit']
        returnable = 'returnable' in request.form
        selling_price = float(request.form['selling-price'])
        cost_price = float(request.form['cost-price']) if request.form['cost-price'] else None
        tax_rate = float(request.form['tax-rate']) if request.form['tax-rate'] else None

        new_item = Item(
            name=name,
            sku=sku,
            unit=unit,
            returnable=returnable,
            selling_price=selling_price,
            cost_price=cost_price,
            tax_rate=tax_rate
        )

        db.session.add(new_item)
        db.session.commit()
        flash(f"Item '{name}' has been added successfully!", "success")
        return redirect(url_for('inventory'))

    return render_template("item_form.html", show_sidebar=True)

@app.route('/profile')
@login_required
def profile():
    flash("Viewing your profile information.", "info")
    return render_template("profile.html", user=current_user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect. Please try again.', 'error')
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match. Please try again.', 'error')
            return redirect(url_for('change_password'))

        if current_password == new_password:
            flash('New password must be different from current password.', 'error')
            return redirect(url_for('change_password'))

        current_user.generate_password(new_password)
        db.session.commit()
        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template("change_password.html", user=current_user)

@app.route('/items')
@admin_required
@login_required
def item_list():
    items = Item.query.all()
    total_items = len(items)
    total_value = sum(item.selling_price for item in items if item.selling_price)
    item_types = {
        "Goods": Item.query.count()
    }
    
    flash(f"Viewing list of {total_items} items.", "info")
    return render_template(
        "item_list.html",
        items=items,
        total_items=total_items,
        total_value=total_value,
        item_types=item_types,
        show_sidebar=True
    )





@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    admin_users = User.query.filter_by(role="admin").count()
    regular_users = User.query.filter_by(role="user").count()
    
    recent_users = [
        {
            'username': user.username,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S'),
            'email': user.email,
            'country': user.country
        }
        for user in User.query.order_by(User.last_login.desc()).limit(5).all()
    ]
    
    total_items = Item.query.count()
    total_inventory_value = db.session.query(
        func.sum(case((Item.cost_price.isnot(None), 
                      Item.quantity_in_hand * Item.cost_price), else_=0))
    ).scalar() or 0
    
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
    
    high_value_items = [
        {
            'name': item.name,
            'cost_price': float(item.cost_price) if item.cost_price else 0,
            'quantity': item.quantity_in_hand
        }
        for item in Item.query.filter(
            Item.cost_price.isnot(None)
        ).order_by(Item.cost_price.desc()).limit(5).all()
    ]
    

    user_by_country = [
        {
            'country': country or 'Not Specified',
            'count': count
        }
        for country, count in db.session.query(
            User.country,
            func.count(User.id).label('count')
        ).group_by(User.country).all()
    ]
    
    price_ranges = [
        (0, 100, '0-100'),
        (101, 500, '101-500'),
        (501, 1000, '501-1000'),
        (1001, float('inf'), '1000+')
    ]
    
    price_distribution = []
    for min_price, max_price, label in price_ranges:
        count = Item.query.filter(
            Item.selling_price >= min_price,
            Item.selling_price <= max_price if max_price != float('inf') else Item.selling_price > min_price
        ).count()
        price_distribution.append({'range': label, 'count': count})

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        admin_users=admin_users,
        regular_users=regular_users,
        recent_users=recent_users,
        total_items=total_items,
        total_inventory_value=total_inventory_value,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        high_value_items=high_value_items,
        user_by_country=user_by_country,
        price_distribution=price_distribution
    )


@app.route('/items/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    item_name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Item '{item_name}' has been deleted successfully.", "success")
    return redirect(url_for('item_list'))

@app.route('/items/update/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if request.form.get('name'):
        item.name = request.form.get('name')
    if request.form.get('sku'):
        item.sku = request.form.get('sku')
    if request.form.get('unit'):
        item.unit = request.form.get('unit')
    if request.form.get('quantity_in_hand'):
        item.quantity_in_hand = int(request.form.get('quantity_in_hand'))
    if request.form.get('reorder_point'):
        item.reorder_point = int(request.form.get('reorder_point'))
    if request.form.get('selling_price'):
        item.selling_price = float(request.form.get('selling_price'))
    if request.form.get('cost_price'):
        item.cost_price = float(request.form.get('cost_price'))
    if request.form.get('tax_rate'):
        item.tax_rate = float(request.form.get('tax_rate'))
    
    item.returnable = 'returnable' in request.form
    
    db.session.commit()
    flash(f"Item '{item.name}' has been updated successfully!", "success")
    return redirect(url_for('item_list'))




@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    if request.method == 'POST':
        try:
            new_group = Group(
                type=request.form.get('type'),
                name=request.form.get('itemGroupName'),
                description=request.form.get('description'),
                returnable='returnable' in request.form,
                unit=request.form.get('unit'),
                manufacturer=request.form.get('manufacturer'),
                brand=request.form.get('brand'),
                created_by=current_user.id
            )
            
            db.session.add(new_group)
            db.session.flush()  
            
            if 'createAttributes' in request.form:
                attributes = request.form.getlist('attribute[]')
                options = request.form.getlist('options[]')
                
                for attr, opt in zip(attributes, options):
                    if attr and opt:  
                        group_attr = GroupAttribute(
                            group_id=new_group.id,
                            attribute_name=attr,
                            options=opt
                        )
                        db.session.add(group_attr)
            
            if 'images[]' in request.files:
                files = request.files.getlist('images[]')
            
            db.session.commit()
            flash(f"Item group '{request.form.get('itemGroupName')}' has been added successfully!", "success")
            return redirect(url_for('inventory'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding item group: {str(e)}", "error")
            return render_template('group_form.html', show_sidebar=True)
    
    return render_template('group_form.html', show_sidebar=True)


class InventoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    item = db.relationship('Item', backref='inventory_logs')
    user = db.relationship('User', backref='inventory_logs')


@app.route('/admin/inventory-logs')
@login_required
@admin_required
def admin_inventory_logs():
    logs = InventoryLog.query.order_by(InventoryLog.timestamp.desc()).limit(10).all()
    return jsonify([{
        'item': log.item.name,
        'user': log.user.username,
        'action': log.action,
        'quantity': log.quantity,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'notes': log.notes
    } for log in logs])






# ================ REST API Endpoints ================

# Add CORS support to allow Django to access these APIs
CORS(app)

# API: Get all items
@app.route('/api/items', methods=['GET'])
def api_get_items():
    items = Item.query.all()
    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'name': item.name,
            'sku': item.sku,
            'unit': item.unit,
            'returnable': item.returnable,
            'selling_price': item.selling_price,
            'cost_price': item.cost_price,
            'tax_rate': item.tax_rate,
            'quantity_in_hand': item.quantity_in_hand,
            'quantity_to_receive': item.quantity_to_receive,
            'reorder_point': item.reorder_point
        })
    return jsonify(items_data)

# API: Get specific item
@app.route('/api/items/<int:item_id>', methods=['GET'])
def api_get_item(item_id):
    item = Item.query.get_or_404(item_id)
    item_data = {
        'id': item.id,
        'name': item.name,
        'sku': item.sku,
        'unit': item.unit,
        'returnable': item.returnable,
        'selling_price': item.selling_price,
        'cost_price': item.cost_price,
        'tax_rate': item.tax_rate,
        'quantity_in_hand': item.quantity_in_hand,
        'quantity_to_receive': item.quantity_to_receive,
        'reorder_point': item.reorder_point
    }
    return jsonify(item_data)

# API: Create new item
@app.route('/api/items', methods=['POST'])
def api_create_item():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        new_item = Item(
            name=data.get('name'),
            sku=data.get('sku'),
            unit=data.get('unit'),
            returnable=data.get('returnable', True),
            selling_price=data.get('selling_price'),
            cost_price=data.get('cost_price'),
            tax_rate=data.get('tax_rate'),
            quantity_in_hand=data.get('quantity_in_hand', 0),
            quantity_to_receive=data.get('quantity_to_receive', 0),
            reorder_point=data.get('reorder_point', 10)
        )
        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            'message': 'Item created successfully',
            'id': new_item.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Update an item
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def api_update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        if 'name' in data:
            item.name = data['name']
        if 'sku' in data:
            item.sku = data['sku']
        if 'unit' in data:
            item.unit = data['unit']
        if 'returnable' in data:
            item.returnable = data['returnable']
        if 'selling_price' in data:
            item.selling_price = data['selling_price']
        if 'cost_price' in data:
            item.cost_price = data['cost_price']
        if 'tax_rate' in data:
            item.tax_rate = data['tax_rate']
        if 'quantity_in_hand' in data:
            item.quantity_in_hand = data['quantity_in_hand']
        if 'quantity_to_receive' in data:
            item.quantity_to_receive = data['quantity_to_receive']
        if 'reorder_point' in data:
            item.reorder_point = data['reorder_point']

        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Delete an item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def api_delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Get all groups
@app.route('/api/groups', methods=['GET'])
def api_get_groups():
    groups = Group.query.all()
    groups_data = []
    for group in groups:
        attributes = []
        for attr in group.attributes:
            attributes.append({
                'id': attr.id,
                'attribute_name': attr.attribute_name,
                'options': attr.options
            })
        
        groups_data.append({
            'id': group.id,
            'type': group.type,
            'name': group.name,
            'description': group.description,
            'returnable': group.returnable,
            'unit': group.unit,
            'manufacturer': group.manufacturer,
            'brand': group.brand,
            'created_at': group.created_at.isoformat() if group.created_at else None,
            'created_by': group.created_by,
            'attributes': attributes
        })
    return jsonify(groups_data)

# API: Get specific group
@app.route('/api/groups/<int:group_id>', methods=['GET'])
def api_get_group(group_id):
    group = Group.query.get_or_404(group_id)
    attributes = []
    for attr in group.attributes:
        attributes.append({
            'id': attr.id,
            'attribute_name': attr.attribute_name,
            'options': attr.options
        })
    
    group_data = {
        'id': group.id,
        'type': group.type,
        'name': group.name,
        'description': group.description,
        'returnable': group.returnable,
        'unit': group.unit,
        'manufacturer': group.manufacturer,
        'brand': group.brand,
        'created_at': group.created_at.isoformat() if group.created_at else None,
        'created_by': group.created_by,
        'attributes': attributes
    }
    return jsonify(group_data)

# API: Create new group with attributes
@app.route('/api/groups', methods=['POST'])
def api_create_group():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        new_group = Group(
            type=data.get('type'),
            name=data.get('name'),
            description=data.get('description'),
            returnable=data.get('returnable', False),
            unit=data.get('unit'),
            manufacturer=data.get('manufacturer'),
            brand=data.get('brand'),
            created_by=data.get('created_by')
        )
        db.session.add(new_group)
        db.session.flush()  # Get ID before commit

        # Add attributes if provided
        if 'attributes' in data and isinstance(data['attributes'], list):
            for attr_data in data['attributes']:
                new_attribute = GroupAttribute(
                    group_id=new_group.id,
                    attribute_name=attr_data.get('attribute_name'),
                    options=attr_data.get('options')
                )
                db.session.add(new_attribute)

        db.session.commit()
        return jsonify({
            'message': 'Group created successfully',
            'id': new_group.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Update a group
@app.route('/api/groups/<int:group_id>', methods=['PUT'])
def api_update_group(group_id):
    group = Group.query.get_or_404(group_id)
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        if 'type' in data:
            group.type = data['type']
        if 'name' in data:
            group.name = data['name']
        if 'description' in data:
            group.description = data['description']
        if 'returnable' in data:
            group.returnable = data['returnable']
        if 'unit' in data:
            group.unit = data['unit']
        if 'manufacturer' in data:
            group.manufacturer = data['manufacturer']
        if 'brand' in data:
            group.brand = data['brand']

        # Update attributes if provided
        if 'attributes' in data and isinstance(data['attributes'], list):
            # Remove existing attributes
            GroupAttribute.query.filter_by(group_id=group.id).delete()
            
            # Add new attributes
            for attr_data in data['attributes']:
                new_attribute = GroupAttribute(
                    group_id=group.id,
                    attribute_name=attr_data.get('attribute_name'),
                    options=attr_data.get('options')
                )
                db.session.add(new_attribute)

        db.session.commit()
        return jsonify({'message': 'Group updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Delete a group
@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def api_delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    try:
        # Delete associated attributes
        GroupAttribute.query.filter_by(group_id=group.id).delete()
        
        # Delete group
        db.session.delete(group)
        db.session.commit()
        return jsonify({'message': 'Group deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API endpoint to get dashboard data
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    total_items = Item.query.count()
    total_inventory_value = db.session.query(
        func.sum(case((Item.cost_price.isnot(None), 
                      Item.quantity_in_hand * Item.cost_price), else_=0))
    ).scalar() or 0
    
    low_stock_items = Item.query.filter(Item.quantity_in_hand <= Item.reorder_point).count()
    out_of_stock_items = Item.query.filter(Item.quantity_in_hand == 0).count()
    
    total_groups = Group.query.count()
    goods_groups = Group.query.filter_by(type='goods').count()
    service_groups = Group.query.filter_by(type='service').count()
    
    return jsonify({
        'total_items': total_items,
        'total_inventory_value': total_inventory_value,
        'low_stock_items': low_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_groups': total_groups,
        'goods_groups': goods_groups,
        'service_groups': service_groups
    })

# Add some mock data for testing if database is empty
def add_mock_data():
    # Check if there are any items in the database
    if Item.query.count() == 0:
        # Add mock items
        items = [
            Item(name="Laptop", sku="LAP-001", unit="piece", returnable=True, selling_price=1200.00, cost_price=900.00, tax_rate=18.0, quantity_in_hand=15, reorder_point=5),
            Item(name="Smartphone", sku="PHN-001", unit="piece", returnable=True, selling_price=800.00, cost_price=600.00, tax_rate=12.0, quantity_in_hand=25, reorder_point=8),
            Item(name="Headphones", sku="HDP-001", unit="piece", returnable=True, selling_price=150.00, cost_price=80.00, tax_rate=5.0, quantity_in_hand=40, reorder_point=10),
            Item(name="Keyboard", sku="KBD-001", unit="piece", returnable=True, selling_price=120.00, cost_price=70.00, tax_rate=5.0, quantity_in_hand=30, reorder_point=10),
            Item(name="Mouse", sku="MOU-001", unit="piece", returnable=True, selling_price=50.00, cost_price=25.00, tax_rate=5.0, quantity_in_hand=45, reorder_point=15)
        ]
        for item in items:
            db.session.add(item)
    
    # Check if there are any groups in the database
    if Group.query.count() == 0:
        # Create a user for group creation
        if User.query.count() == 0:
            admin_user = User(username="admin", email="admin@example.com", role="admin")
            admin_user.generate_password("admin123")
            db.session.add(admin_user)
            db.session.flush()
            user_id = admin_user.id
        else:
            user_id = User.query.first().id
            
        # Add mock groups
        electronics_group = Group(
            type="goods",
            name="Electronics",
            description="Electronic devices and accessories",
            returnable=True,
            unit="piece",
            manufacturer="Various",
            brand="Multiple",
            created_by=user_id
        )
        db.session.add(electronics_group)
        db.session.flush()
        
        # Add attributes to Electronics group
        attributes = [
            GroupAttribute(group_id=electronics_group.id, attribute_name="Color", options="Black, White, Silver, Gold"),
            GroupAttribute(group_id=electronics_group.id, attribute_name="Warranty", options="1 Year, 2 Years, 3 Years")
        ]
        for attr in attributes:
            db.session.add(attr)
            
        # Add another group
        furniture_group = Group(
            type="goods",
            name="Furniture",
            description="Office and home furniture",
            returnable=False,
            unit="piece",
            manufacturer="FurniCorp",
            brand="ComfortPlus",
            created_by=user_id
        )
        db.session.add(furniture_group)
        db.session.flush()
        
        # Add attributes to Furniture group
        furniture_attrs = [
            GroupAttribute(group_id=furniture_group.id, attribute_name="Material", options="Wood, Metal, Plastic, Glass"),
            GroupAttribute(group_id=furniture_group.id, attribute_name="Size", options="Small, Medium, Large")
        ]
        for attr in furniture_attrs:
            db.session.add(attr)
    
    db.session.commit()

# Call add_mock_data at startup
with app.app_context():
    db.create_all()
    add_mock_data()

# Configure Flask logging to be minimal
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

if __name__ == '__main__':
    print("Flask API server is running at http://localhost:5001/api")
    app.run(debug=False, host='0.0.0.0', port=5001)