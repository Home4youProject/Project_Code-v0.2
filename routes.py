import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from Home4u import app, db, bcrypt
from Home4u.forms import RegistrationForm, SubmitForm, PaymentCreditForm, LoginForm, PaymentMethodForm, UpdateAccountForm, ReviewForm, AddHouseForm, UpdateHouseForm, SearchForm, ResultsForm, CommunicationForm, Communication2Form, RequestForm
from Home4u.models import User, House, HouseSelector, SearchInfo, Review, stayed, Communication, Request
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime



@app.route("/")
@app.route("/home",methods=['GET', 'POST'])
def home():
    logo_image = url_for('static', filename='logo.png')
    return render_template('home.html', image_file=logo_image)

@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search = SearchInfo(location=form.location.data, arrival_date=form.arrival_date.data, guests=form.guests.data)
        db.session.add(search)
        db.session.commit()
        searched = SearchInfo.query.order_by(SearchInfo.id.desc()).first()
        searched_houses = House.query.filter_by(city=searched.location).filter_by(availability=True).filter(House.visitors>=searched.guests).filter(House.available_from<=searched.arrival_date).all()
        if searched_houses == []:
            flash('Δεν βρέθηκαν κατάλληλα καταλύματα', 'danger')
            return redirect(url_for('search'))
        return redirect(url_for('search_results'))
    return render_template('search.html', title='Search', form=form)

@app.route("/search_results", methods=['GET', 'POST'])
def search_results():
    form = SearchForm()
    searched = SearchInfo.query.order_by(SearchInfo.id.desc()).first()
    searched_houses = House.query.filter_by(city=searched.location).filter_by(availability=True).filter(House.visitors>=searched.guests).filter(House.available_from<=searched.arrival_date).all()
    if form.validate_on_submit():
        select = HouseSelector(house_id=form.house_id.data)
        db.session.add(select)
        db.session.commit()
        return redirect(url_for('payment_method'))
    return render_template('search_results.html', searched_houses=searched_houses, title='Search Results', form=form)

@app.route("/user_review_list", methods=['GET', 'POST'])
@login_required
def user_review_list():
    form = ReviewForm()
    req = Request.query.filter_by(req_sender=current_user.id).filter_by(req_type='accepted').all()
    print(req)
    for r in req:
        homes = House.query.filter_by(id=r.req_house).all()
        print(homes)
    if form.validate_on_submit():
        return redirect(url_for('user_review'))
    return render_template('user_review_list.html', homes=homes, title='Houses List', form=form)

@app.route("/user_review")
@login_required
def user_review():
    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(reviewer=current_user.id, recipient=homes.id, stars=form.stars.data, comments=form.comments.data)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been succesfully saved!', 'success')
        return redirect(url_for('home'))
    return render_template('user_review.html', title='Add a Review', form=form)

@app.route("/register_house", methods=['GET', 'POST'])
@login_required
def register_house():
    form = UpdateHouseForm()
    if form.validate_on_submit():
        house = House(house_name=form.house_name.data, city=form.city.data, postal_code=form.postal_code.data, address=form.address.data, square_meters=form.square_meters.data, price=form.price.data, house_type=form.house_type.data, visitors=form.visitors.data, user_id=current_user.id, available_from=form.available_from.data, availability=form.availability.data)
        db.session.add(house)

        db.session.commit()
        flash('Your house has been succesfully saved!', 'success')
        return redirect(url_for('login'))
    return render_template('register_house.html', title='Add House', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, phone=form.phone.data, firstname=form.firstname.data, surname=form.surname.data, sex=form.sex.data, birth_date=form.birth_date.data)
        db.session.add(user)
        db.session.commit()
        flash('Το προφίλ σας δημιουργήθηκε. Για να ενημερώσετε το ταμείο σας κάνετε είσοδο και πηγαίνετε στο προφίλ σας', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture2(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/house_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.birth_date = form.birth_date.data
        current_user.firstname = form.firstname.data
        current_user.surname = form.surname.data
        current_user.balance = form.balance.data
        current_user.sex = form.sex.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.birth_date.data = current_user.birth_date
        form.firstname.data = current_user.firstname
        form.surname.data = current_user.surname
        form.balance.data = current_user.balance
        form.sex.data = current_user.sex
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/edit_house<int:house_id>", methods=['GET', 'POST'])
@login_required
def edit_house(house_id):
    form = UpdateHouseForm()

    house = House.query.get_or_404(house_id)
    if form.validate_on_submit():

        if form.picture.data:
            picture_file = save_picture2(form.picture.data)
            house.image_file = picture_file
        house.house_name = form.house_name.data
        house.city = form.city.data
        house.postal_code = form.postal_code.data
        house.address = form.address.data
        house.square_meters = form.square_meters.data
        house.price = form.price.data
        house.house_type = form.house_type.data
        house.visitors = form.visitors.data
        house.available_from = form.available_from.data
        house.availability = form.availability.data
        db.session.commit()
        flash('Το κατάλυμα σας ενημερώθηκε επιτυχώς', 'success')
        return redirect(url_for('edit_house', house_id=house.id))
    elif request.method == 'GET':

        form.house_name.data = house.house_name
        form.city.data = house.city
        form.postal_code.data = house.postal_code
        form.address.data = house.address
        form.square_meters.data = house.square_meters
        form.price.data = house.price
        form.available_from.data = house.available_from
        form.availability.data = house.availability
        form.house_type.data = house.house_type
        form.visitors.data = house.visitors
    image_file = url_for('static', filename='house_pics/' + house.image_file)
    return render_template('edit_house.html', title='Edit House',
                           image_file=image_file, form=form, house=house)


@app.route("/house_list", methods=['GET', 'POST'])
def house_list():
    houses = House.query.filter_by(user_id=current_user.id).all()
    return render_template('house_list.html', houses=houses , title='Houses')

@app.route("/payment_method", methods=['GET', 'POST'])
@login_required
def payment_method():
    form = PaymentMethodForm()
    if form.validate_on_submit():
        if form.payment_type.data == 'cash':
            return redirect(url_for('payment_cash'))
        elif form.payment_type.data == 'credit_card':
            return redirect(url_for('payment_creditcard'))
        else:
            return redirect(url_for('payment_balance'))

    return render_template("payment_method.html", title='Πληρωμή', form=form)

@app.route("/payment_cash", methods=['GET', 'POST'])
def payment_cash():
    form = SubmitForm()
    house_to_rent = HouseSelector.query.order_by(HouseSelector.id.desc()).first()
    house1 = House.query.filter_by(id=house_to_rent.house_id).first()

    if form.validate_on_submit():
        house1.availability = False
        request = Request(req_sender=current_user.id, req_reciever=house1.user_id, req_house=house1.id)
        db.session.add(request)
        db.session.commit()
        print(request.id)
        flash('Η κράτηση ολοκληρώθηκε', 'success')
        return redirect(url_for('home'))

    return render_template('payment_cash.html', title='Μετρητά', house1=house1,  form=form)

@app.route("/payment_creditcard", methods=['GET', 'POST'])
def payment_creditcard():
    form = PaymentCreditForm()
    house_to_rent = HouseSelector.query.order_by(HouseSelector.id.desc()).first()
    house1 = House.query.filter_by(id=house_to_rent.house_id).first()

    if form.validate_on_submit():
        house1.availability = False
        request = Request(req_sender=current_user.id, req_reciever=house1.user_id, req_house=house1.id)
        db.session.add(request)
        db.session.commit()
        print(request.id)
        flash('Η κράτηση ολοκληρώθηκε', 'success')
        return redirect(url_for('home'))

    return render_template('payment_creditcard.html', title='Πιστωτική Κάρτα', house1=house1,  form=form)

@app.route("/payment_balance", methods=['GET', 'POST'])
def payment_balance():
    form = SubmitForm()
    house_to_rent = HouseSelector.query.order_by(HouseSelector.id.desc()).first()
    house1 = House.query.filter_by(id=house_to_rent.house_id).first()
    if form.validate_on_submit():
        if current_user.balance>=house1.price:
            current_user.balance = current_user.balance-house1.price
            house1.availability = False
            request = Request(req_sender=current_user.id, req_reciever=house1.user_id, req_house=house1.id)
            db.session.add(request)
            db.session.commit()
            print(request.id)
            flash('Η κράτηση ολοκληρώθηκε', 'success')
            return redirect(url_for('home'))
        else:
            flash('Το ταμείο σας δεν έχει αρκετό υπόλοιπο. Πηγένετε στο προφίλ σας για να το ενημερώσετε', 'danger')

    return render_template('payment_balance.html', title='Ταμείο', house1=house1,  form=form)


@app.route("/report")
@login_required
def report():
    return render_template('report.html', title='Report')

@app.route("/owner_review_list")
def owner_review_list():
    form = ReviewForm()
    #acc_req = Request.query.filter_by(req_sender=)
    users = User.query.filter_by(id=current_user.id).all()
    if form.validate_on_submit():
        return redirect(url_for('owner_review'))
    return render_template('owner_review_list.html', title='Users List', form=form)


@app.route("/owner_review")
def owner_review():
    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(reviewer=current_user.id, recipient=users.id, stars=form.stars.data, comments=form.comments.data)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been succesfully saved!', 'success')
        return redirect(url_for('home'))
    return render_template('owner_review.html', title='Add a Review', form=form)

@app.route("/communication")
@login_required
def communication():
    return render_template('communication.html', title='Communication')

@app.route("/write_message", methods=['GET', 'POST'])
def write_message():
    form = Communication2Form()
    users = User.query.filter_by(username=form.receiver.data).first()
    if form.validate_on_submit() :
        if users:
            if form.receiver.data==users.username:
                com2 = Communication(sender=current_user.id, message=form.message.data, receiver= form.receiver.data)
                db.session.add(com2)
                db.session.commit()
                flash('Το μήνυμα εστάλει στο χρήστη !', 'success')
                return redirect(url_for('home'))
        else:
            flash('Ο παραλήπτης δεν βρέθηκε', 'danger')
            return redirect(url_for('write_message'))
    return render_template('write_message.html', users=users ,title='write message', form=form)

@app.route("/auto_message", methods=['GET', 'POST'])
def auto_message():
    form = CommunicationForm()
    users = User.query.filter_by(username=form.receiver.data).first()
    if form.validate_on_submit():

        if users:
            if form.receiver.data==users.username:
                com = Communication(sender=current_user.id , auto_type=form.select_type.data, receiver= form.receiver.data)
                db.session.add(com)
                db.session.commit()
                print(com.auto_type)
                flash('Το μήνυμα εστάλει στο χρήστη !', 'success')
                return redirect(url_for('home'))
        else:
            flash('Ο παραλήπτης δεν βρέθηκε', 'danger')
            print("heyyyy")
            return redirect(url_for('auto_message'))
    return render_template('auto_message.html', users=users , title='auto_message', form=form)


@app.route("/request_list", methods=['GET', 'POST'])
def request_list():
    form = RequestForm()
    requests = Request.query.filter_by(req_reciever=current_user.id).filter_by(req_type='pending').order_by(Request.id.desc()).all()

    if form.validate_on_submit():
        current_user.selected_request=form.req_id.data
        db.session.commit()
        return redirect(url_for('accept_request'))
    return render_template('request_list.html', requests=requests , title='Request List', form=form)


@app.route("/accept_request", methods=['GET', 'POST'])
def accept_request():
    form = RequestForm()
    sel_request = Request.query.filter_by(id=current_user.selected_request).first()
    if form.submit.data:
        if form.validate_on_submit():
            sel_request.req_type='accepted'
            db.session.commit()
            flash('Το αίτημα έγινε αποδεχτό', 'success')
            return redirect(url_for('request_list'))
    else:
        if form.validate_on_submit():
            sel_request.req_type='rejected'
            db.session.commit()
            flash('Το αίτημα απορρίφθηκε', 'danger')
            return redirect(url_for('request_list'))
    return render_template('accept_request.html', sel_request=sel_request , title='Request List', form=form)
