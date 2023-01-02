import requests
from primerjalnik import app, db, logger, consul_connection
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, jsonify, make_response
from primerjalnik.models import Item, User
from primerjalnik.forms import RegisterForm, LoginForm, SearchForm
from flask_login import login_user, logout_user, login_required
from primerjalnik.scraper import get_products
from primerjalnik.utils import ProductsOut, LiveOut, ReadyOut, get_info

metrics_data = {'searched_product_count': {}, 'returned_products': 0}

@app.route('/')
@app.route('/home')
def home_page():

    try:
        index, data = consul_connection.kv.get('maintenance')
        if data['Value'].decode('utf-8') == 'true':
            return render_template('maintenance.html')
    except:
        pass

    cat_fact = str(requests.get('https://catfact.ninja/fact').json()['fact'])
    btc = dict()
    btc['eur'] = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json').json()['bpi']['EUR']['rate']
    btc['usd'] = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json').json()['bpi']['USD']['rate']
    btc['gbp'] = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json').json()['bpi']['GBP']['rate']

    return render_template('home.html', cat_fact=cat_fact, btc=btc)

@app.route('/products/<searched_product>', methods=['GET'])
@app.output(ProductsOut(many=True))
def return_products(searched_product, store):
    
    products = get_products(searched_product)
    
    # Metrics collection

    if searched_product not in metrics_data['searched_product_count']:
        metrics_data['searched_product_count'][searched_product] = 0
    metrics_data['searched_product_count'][searched_product] += 1

    # Logging
    logger.info(f"Searched product: {searched_product}")
    
    return make_response(jsonify(products), 200)


@app.route('/izdelki', methods=['GET', 'POST'])
def izdelki_page():
    form = SearchForm()
    products = []
    product_info = ""

    if request.method == 'POST':
        searched_product = form.searched_product.data
        products = get_products(searched_product)

        # Metrics collection

        if searched_product not in metrics_data['searched_product_count']:
            metrics_data['searched_product_count'][searched_product] = 0
        metrics_data['searched_product_count'][searched_product] += 1

        # Logging
        logger.info(f"Searched product: {form.searched_product.data}")

        metrics_data['returned_products'] += len(products)

        product_info = get_info(searched_product)

    return render_template('izdelki.html', form=form, products=products, product_info=product_info)

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
@app.output(LiveOut)
def health_live():
    return make_response(jsonify(live=True), 200)

# Ready
@app.route('/health/ready')
@app.output(ReadyOut)
def health_ready():
    try:
        with app.app_context():
            db.session.execute("SELECT 1")

        return make_response(jsonify(ready=True), 200)

    except Exception as e:
        # 503 - Service unavailable
        return make_response(jsonify(erros=e), 503)

# Metrics
@app.route('/metrics')
def metrics():
    return make_response(jsonify(metrics_data), 200)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404