from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import  InputRequired, Length, Email, EqualTo, ValidationError, NumberRange
from Home4u.models import User, House, HouseSelector, SearchInfo , Review, stayed, Communication, Request
from wtforms.fields.html5 import DateField


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[InputRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[InputRequired()])
    confirm_password = PasswordField('Επαλήθευση Κωδικού',
                                     validators=[InputRequired(), EqualTo('password')])
    phone = IntegerField('Τηλέφωνο',
                          validators=[NumberRange(min=1000000000, max=9999999999, message='Το τηλέφωνο πρέπει να είναι ακριβώς 10 ψηφία')])
    birth_date = DateField('Ημερομηνία Γέννησης')
    firstname = StringField('Όνομα', validators=[Length(min=2, max=20)])
    surname = StringField('Επίθετο', validators=[Length(min=2, max=20)])
    sex =  SelectField(u'Φύλο', choices=[("Male", 'Άνδρας'), ("female", 'Γυναίκα'), ("other", 'Άλλο')])
    submit = SubmitField('Εγγραφή')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Το username υπάρχει ήδη')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Το email αυτό δεν είναι διαθέσιμο')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('Το τηλέφωνο υπάρχει ήδη')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[InputRequired(), Email()])
    password = PasswordField('Κωδικός', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Σύνδεση')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[InputRequired(), Email()])
    picture = FileField('Ενημέρωση Εικόνας Προφίλ', validators=[FileAllowed(['jpg', 'png'])])
    phone = IntegerField('Τηλέφωνο',
                          validators=[NumberRange(min=1000000000, max=9999999999, message='Το τηλέφωνο πρέπει να είναι ακριβώς 10 ψηφία')])
    birth_date = DateField('Ημερομηνία Γέννησης')
    firstname = StringField('Όνομα', validators=[Length(min=2, max=20)])
    surname = StringField('Επίθετο', validators=[Length(min=2, max=20)])
    balance = FloatField('Ταμείο')
    sex = SelectField(u'Φύλο', choices=[("Male", 'Άνδρας'), ("female", 'Γυναίκα'), ("other", 'Άλλο')])
    submit = SubmitField('Ενημέρωση')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Το username υπάρχει ήδη.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Το email αυτό δεν είναι διαθέσιμο.')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('Το τηλέφωνο υπάρχει ήδη.')

class ReviewForm(FlaskForm):
    reviewer = IntegerField('Reviewer')
    recipient = IntegerField('Id')
    stars = IntegerField('Stars', validators=[InputRequired()])
    comments = StringField('Comments', validators=[Length(min=1, max=200)])
    submit = SubmitField('Προσθήκη Αξιολόγησης')
    submit2 = SubmitField('Επιλογή Καταλύματος')
    submit3 = SubmitField('Επιλογή Χρήστη')



class AddHouseForm(FlaskForm):
    house_name = StringField('Όνομα Σπιτιού', validators=[InputRequired(), Length(min=2, max=50)])
    city = StringField('Πόλη', validators=[InputRequired(), Length(min=2, max=20)])
    postal_code = IntegerField('Ταχυδρομικός Κώδικας',
                                validators=[InputRequired(), NumberRange(min=5, max=5, message='Ο ΤΚ πρέπει να είναι 5 ψήφιο νούμερο')])
    address = StringField('Διεύθυνση', validators=[InputRequired(), Length(min=1, max=50)])
    square_meters = IntegerField('Τετραγωνικά Μέτρα', validators=[InputRequired()])
    price = IntegerField('Τιμή', validators=[InputRequired()])
    house_type = StringField('Είδος Καταλύματος', validators=[InputRequired()])
    visitors = IntegerField('Επισκέπτες', validators=[InputRequired()])
    available_from = DateField('Διαθέσιμο Από', validators=[InputRequired()])
    availability = BooleanField('Διαθέσιμο')
    submit = SubmitField('Αποθήκευση')

class UpdateHouseForm(FlaskForm):
    house_name = StringField('Όνομα Σπιτιού', validators=[InputRequired(), Length(min=2, max=50)])
    city = StringField('Πόλη', validators=[InputRequired(), Length(min=2, max=20)])
    postal_code = IntegerField('Ταχυδρομικός Κώδικας',
                                validators=[InputRequired(), NumberRange(min=10000, max=99999, message='Ο ΤΚ πρέπει να είναι 5 ψήφιο νούμερο')])
    address = StringField('Διεύθυνση', validators=[InputRequired(), Length(min=1, max=50)])
    square_meters = IntegerField('Τετραγωνικά Μέτρα', validators=[InputRequired()])
    price = IntegerField('Τιμή', validators=[InputRequired()])
    house_type = StringField('Είδος Καταλύματος', validators=[InputRequired()])
    visitors = IntegerField('Επισκέπτες', validators=[InputRequired()])
    available_from = DateField('Διαθέσιμο Από',
                           format='%Y-%m-%d')
    availability = BooleanField('Διαθέσιμο')
    picture = FileField('Ενημέρωση Εικόνας Προφίλ', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Αποθήκευση')

class SearchForm(FlaskForm):
    location = StringField('Περιοχή', validators=[InputRequired()])
    arrival_date = DateField('Ημερομηνία Άφιξης', format='%Y-%m-%d')
    guests = IntegerField('Αριθμός Επισκεπτών', validators=[InputRequired()])
    submit = SubmitField('Αναζήτηση')
    house_id = IntegerField('Id Σπιτιού')
    submit2 = SubmitField('Κάντε Κράτηση')

class ResultsForm(FlaskForm):
    submit = SubmitField('Κάντε Κράτηση')

class CommunicationForm(FlaskForm):
    select_type = SelectField(u'Επιλογη μήνυματος', choices=[("den exw reuma", 'Δεν εχω ρεύμα'), ("den exw nero", 'Δεν εχω νερό'), ("den exw internet", 'Δεν εχω internet'),("den exw zesto nero", 'Δεν εχω ζεστό νερό'), ("den exw thermansi", 'Δεν έχω θέρμανση')])
    receiver = StringField('Παραλήπτης')
    message =  StringField('Γραπτο μηνύμα')
    submit = SubmitField('Αποστολή')

class Communication2Form(FlaskForm):

    receiver = StringField('Παραλήπτης')
    message =  StringField('Γραπτο μηνύμα')
    submit = SubmitField('Αποστολή')

class PaymentMethodForm(FlaskForm):
    payment_type = SelectField(u'Πληρώστε με:', choices=[('cash', 'Μετρητά'), ('credit_card', 'Πιστωτική'), ('balance', 'Ταμείο')])
    submit = SubmitField('Επιλογή')
    submit2 = SubmitField('Επιβεβαίωση Πληρωμής')

class PaymentCreditForm(FlaskForm):
    card_name = StringField('Όνομα στη κάρτα')
    card_number = IntegerField('Αριθμός της κάρτας')
    cvv = IntegerField('CVV')
    # expire_date_month = IntegerField('Ημερομηνία Λήξεως Μήνα')
    # expire_date_year = IntegerField('Ημερομηνία Λήξεως')
    submit = SubmitField('Επιβεβαίωση Πληρωμής')

class SubmitForm(FlaskForm):
    submit = SubmitField('Επιβεβαίωση Πληρωμής')


class RequestForm(FlaskForm):
    req_id = IntegerField('Id Αιτήματος')
    submit = SubmitField('Επιβεβαίωση Αιτήματος')
    submit2 = SubmitField('Απόρριψη Αιτήματος')
    submit3 = SubmitField('Επιλογή')
