import secrets
import os
from PIL import Image

from flask import render_template, url_for, flash, redirect, request, abort
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, RecipeForm
from application.models import User, Recipe, Ingredient, Equipment
from flask_login import login_user, current_user, logout_user, login_required
from application import app, db, bcrypt


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    page2 = request.args.get('page2', 1, type=int)
    recipes = Recipe.query.order_by(Recipe.date_posted.desc()).paginate(page=page, per_page=5)
    popular_recipes = Recipe.query.order_by(Recipe.view_counter.desc()).paginate(page=page2, per_page=4)
    return render_template('home.html', recipes=recipes, popular_recipes=popular_recipes)


@app.route("/search")
def search():
    page = request.args.get('page', 1, type=int)
    page2 = request.args.get('page2', 1, type=int)
    popular_recipes = Recipe.query.order_by(Recipe.view_counter.desc()).paginate(page=page2, per_page=4)
    try:
        recipe = Recipe.query.whoosh_search(request.args.get('query'))
        recipes = recipe.paginate(page=page, per_page=5)
    except :
        recipes = []
    return render_template('home.html', recipes=recipes, popular_recipes=popular_recipes)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Vaš nalog je uspešno kreiran! Sada se možete prijaviti.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registracija', form=form)


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
            flash('Prijava neuspešna! Molim vas proverite email i lozinku.', 'danger')
    return render_template('login.html', title='Prijava', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.update(username=form.username.data, email=form.email.data)
        db.session.commit()
        flash('Vaš nalog je uspešno ažuriran!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Profil', image_file=image_file, form=form)


@app.route("/recipe/new", methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    for ingredient in Ingredient.query.all():
        form.main_ingredients.choices.append((ingredient.id, ingredient.name))
        form.side_ingredients.choices.append((ingredient.id, ingredient.name))
    for equipment in Equipment.query.all():
        form.equipment.choices.append((equipment.id, equipment.name))

    if form.is_submitted():
        recipe = Recipe(title=form.title.data, content=form.content.data, author=current_user,
                        preparation_time=form.preparation_time.data, difficulty=form.difficulty.data)

        for el in request.form.getlist('main_ingredients'):
            recipe.main_ingredients.append(Ingredient.query.get(el[0]))
        for el in request.form.getlist('side_ingredients'):
            recipe.side_ingredients.append(Ingredient.query.get(el[0]))
        for el in request.form.getlist('equipment'):
            recipe.equipment.append(Equipment.query.get(el[0]))
        recipe.view_counter = 0

        if form.image_file.data:
            recipe.image_file = save_recipe_picture(form.image_file.data)
        db.session.add(recipe)
        db.session.commit()
        flash('Vaš recept je uspešno kreiran!', 'success')
        return redirect(url_for('home'))
    return render_template('create_update_recipe.html', title='Kreiranje recepta', form=form, legend='Kreiranje recepta')


@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.view_counter += 1
    db.session.commit()

    print("Povecao se view count")
    print(recipe.view_counter)
    return render_template('recipe.html', title=recipe.title, recipe=recipe)


@app.route("/recipe/<int:recipe_id>/update", methods=['GET', 'POST'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        abort(403)

    form = RecipeForm()
    for ingredient in Ingredient.query.all():
        form.main_ingredients.choices.append((ingredient.id, ingredient.name))
        form.side_ingredients.choices.append((ingredient.id, ingredient.name))
    for equipment in Equipment.query.all():
        form.equipment.choices.append((equipment.id, equipment.name))

    if form.is_submitted():
        if form.image_file.data:
            recipe.image_file = save_recipe_picture(form.image_file.data)
        recipe.update(form.title.data, form.difficulty.data, form.content.data, form.preparation_time.data)

        for el in request.form.getlist('main_ingredients'):
            recipe.main_ingredients.append(Ingredient.query.get(el[0]))
        for el in request.form.getlist('side_ingredients'):
            recipe.side_ingredients.append(Ingredient.query.get(el[0]))
        for el in request.form.getlist('equipment'):
            recipe.equipment.append(Equipment.query.get(el[0]))

        db.session.commit()
        flash('Vaš recept je uspešno ažuriran!', 'success')
        return redirect(url_for('recipe', recipe_id=recipe.id))
    elif request.method == 'GET':
        form.image_file.data = recipe.image_file
        form.title.data = recipe.title
        form.content.data = recipe.content
        form.main_ingredients.data = recipe.main_ingredients
        form.side_ingredients.data = recipe.side_ingredients
        form.preparation_time.data = recipe.preparation_time
        form.equipment.data = recipe.equipment
        form.difficulty.data = recipe.difficulty
    return render_template('create_update_recipe.html', title='Ažuriranje recepta', form=form, legend='Ažuriranje recepta')


@app.route("/recipe/<int:recipe_id>/delete", methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash('Vaš recept je uspešno obrisan!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_recipes(username):
    page = request.args.get('page', 1, type=int)

    # get first user with this username (if none return 404)
    user = User.query.filter_by(username=username).first_or_404()

    recipes = Recipe.query.filter_by(author=user)\
        .order_by(Recipe.date_posted.desc())\
        .paginate(page=page, per_page=5)

    return render_template('user_recipes.html', recipes=recipes, user=user)


def save_recipe_picture(form_image):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_image.filename)
    image_filename = random_hex + file_extension
    image_path = os.path.join(app.root_path, 'static/img', image_filename)
    output_size = (200, 200)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)
    return image_filename


def save_profile_picture(form_image):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_image.filename)
    image_filename = random_hex + file_extension
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_filename)
    output_size = (250, 200)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)
    return image_filename