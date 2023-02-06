import flask_whooshalchemyplus
from datetime import datetime
from flask_login import UserMixin

from application import app, db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


association_recipe_main_ingredient = db.Table('association_recipe_main_ingredient', db.Model.metadata,
                                              db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                                              db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'))
                                              )

association_recipe_side_ingredient = db.Table('association_recipe_side_ingredient', db.Model.metadata,
                                              db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                                              db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'))
                                              )

association_recipe_equipment = db.Table('association_recipe_equipment', db.Model.metadata,
                                        db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                                        db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'))
                                        )

association_recipe_category = db.Table('association_recipe_category', db.Model.metadata,
                                       db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                                       db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
                                       )


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    def update(self, username, email):
        self.username = username
        self.email = email


class Recipe(db.Model):
    __tablename__ = 'recipe'
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    main_ingredients = db.relationship("Ingredient", secondary=association_recipe_main_ingredient)
    side_ingredients = db.relationship("Ingredient", secondary=association_recipe_side_ingredient)
    preparation_time = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    equipment = db.relationship("Equipment", secondary=association_recipe_equipment)
    difficulty = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    view_counter = db.Column(db.Integer)

    def __repr__(self):
        return f"Recipe('{self.title}', '{self.date_posted}')"

    def update(self, title, difficulty, content, preparation_time):
        self.title = title
        self.difficulty = difficulty
        self.content = content
        self.preparation_time = preparation_time


class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')


class Rating(db.Model):
    __tablename__ = 'rating'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)


class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


# For searching
flask_whooshalchemyplus.whoosh_index(app, Recipe)
