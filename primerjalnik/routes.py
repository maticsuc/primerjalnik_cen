from primerjalnik import app, db, logger
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, jsonify, make_response
from primerjalnik.models import Item, User
from primerjalnik.forms import RegisterForm, LoginForm, SearchForm
from flask_login import login_user, logout_user, login_required
from primerjalnik.scraper import get_products

metrics_data = {'searched_product_count': {}, 'returned_products': 0}

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/izdelki', methods=['GET', 'POST'])
def izdelki_page():
    form = SearchForm()
    products = []

    if request.method == 'POST':
        products = get_products(form.searched_product.data)

        # Metrics collection

        if form.searched_product.data not in metrics_data['searched_product_count']:
            metrics_data['searched_product_count'][form.searched_product.data] = 0
        metrics_data['searched_product_count'][form.searched_product.data] += 1

        # Logging
        logger.info(f"Searched product: {form.searched_product.data}")

        metrics_data['returned_products'] += len(products)
        
    if request.method == 'GET' and request.is_json:
        searched_product = request.json['searched_product']
        products = get_products(searched_product)

        # Metrics collection

        if searched_product not in metrics_data['searched_product_count']:
            metrics_data['searched_product_count'][searched_product] = 0
        metrics_data['searched_product_count'][searched_product] += 1

        # Logging
        logger.info(f"Searched product: {form.searched_product.data}")

        return make_response(jsonify(products), 200)

    return render_template('izdelki.html', form=form, products=products)

@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        with app.app_context():
            db.session.add(user_to_create)
            db.session.commit()
            db.session.refresh(user_to_create)
        login_user(user_to_create)
        flash(f"Account created successfully! Welcome {user_to_create.username}!", category='info')
        return redirect(url_for('market_page'))
    
    if len(form.errors) > 0:
        for err_msg in form.errors.values():
            flash(err_msg[0], category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(message=f"Welcome back {attempted_user.username}!", category='success')

            # Logging
            logger.info(f"User {attempted_user.username} logged in.")

            return redirect(url_for('market_page'))
        else:
            flash("Username and password don't match! Please try again.", category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You've logged out.", category='info')

    # Logging
    logger.info(f"User logged out.")

    return redirect(url_for('home_page'))

# Health checks
# Live
@app.route('/health/live')
def health_live():
    return make_response(jsonify(live=True), 200)

# Ready
@app.route('/health/ready')
def health_ready():
    try:
        with app.app_context():
            db.session.execute("SELECT 1")

        return make_response(jsonify(ready=True), 200)

    except Exception as e:
        print('neki')
        # 503 - Service unavailable
        return make_response(jsonify(erros=e), 503)

# Metrics
@app.route('/metrics')
def metrics():
    return make_response(jsonify(metrics_data), 200)