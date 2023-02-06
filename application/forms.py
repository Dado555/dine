from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, Form, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Korisničko ime',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    confirm_password = PasswordField('Potvrda lozinke',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registruj se')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Korisničko ime je zauzeto. Molimo vas odaberite neko drugo.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email već postoji u sistemu. Molimo vas odaberite neki drugi.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    remember = BooleanField('Zapamti me')
    submit = SubmitField('Prijava')


class UpdateAccountForm(FlaskForm):
    username = StringField('Korisničko ime',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Ažuriraj profilnu sliku', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Ažuriraj')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Korisničko ime je zauzeto. Molimo vas odaberite neko drugo.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email već postoji u sistemu. Molimo vas odaberite neki drugi.')


class RecipeForm(FlaskForm):
    title = StringField('Naziv', validators=[DataRequired()])
    image_file = FileField('Ažuriraj sliku', validators=[FileAllowed(['jpg', 'png'])])
    content = TextAreaField('Opis', validators=[DataRequired()])
    main_ingredients = SelectMultipleField('Glavni sastojci', id='main_ingredients', choices=[], validators=[DataRequired()])
    side_ingredients = SelectMultipleField('Sporedni sastojci', id='side_ingredients', choices=[], validators=[DataRequired()])
    equipment = SelectMultipleField('Oprema', id='equipment', choices=[], validators=[DataRequired()])
    preparation_time = TextAreaField('Vreme spremanja', validators=[DataRequired()])
    difficulty = SelectField('Težina spremanja', [DataRequired()],
                             choices=[('Lako', 'Lako'),
                                      ('Srednje teško', 'Srednje teško'),
                                      ('Teško', 'Teško'),
                                      ("Veoma teško", "Veoma teško")])
    submit = SubmitField('Napravi recept')