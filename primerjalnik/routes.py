from primerjalnik import app, db
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, jsonify, make_response
from primerjalnik.models import Item, User
from primerjalnik.forms import RegisterForm, LoginForm, SearchForm
from flask_login import login_user, logout_user, login_required
from primerjalnik.scraper import get_products

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
    
    if request.method == 'GET' and request.is_json:
        searched_product = request.json['searched_product']
        products = get_products(searched_product)
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
            return redirect(url_for('market_page'))
        else:
            flash("Username and password don't match! Please try again.", category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You've logged out.", category='info')
    return redirect(url_for('home_page'))