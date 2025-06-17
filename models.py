# models.py - Database models (UPDATED)
from database import db  # Import from database.py instead of app.py
from datetime import datetime

class BaseContent(db.Model):
    """Base model for all content types"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    field = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(500))  # Comma-separated tags

class BlogPost(BaseContent):
    """General blog posts for all fields"""
    author = db.Column(db.String(100), default='Admin')
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(200))
    reading_time = db.Column(db.Integer)  # in minutes

class FlashCard(db.Model):
    """Flash cards for language learning"""
    id = db.Column(db.Integer, primary_key=True)
    field = db.Column(db.String(50), nullable=False)  # 'english' or 'danish'
    front_text = db.Column(db.Text, nullable=False)
    back_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # vocabulary, grammar, etc.
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    times_reviewed = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)

class CodeExample(db.Model):
    """Code examples for programming field"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    language = db.Column(db.String(50), nullable=False)  # python, java, csharp, etc.
    code = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default='beginner')
    category = db.Column(db.String(100))  # algorithms, web-dev, data-structures, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(500))

class Recipe(db.Model):
    """Vegan recipes"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text, nullable=False)  # JSON string
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer)  # in minutes
    cook_time = db.Column(db.Integer)  # in minutes
    servings = db.Column(db.Integer)
    difficulty = db.Column(db.String(20), default='easy')
    image_url = db.Column(db.String(200))
    nutrition_info = db.Column(db.Text)  # JSON string
    category = db.Column(db.String(100))  # breakfast, lunch, dinner, snack, dessert
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

class MathProblem(db.Model):
    """Mathematical problems and solutions"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_text = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    category = db.Column(db.String(100))  # algebra, calculus, geometry, etc.
    difficulty = db.Column(db.String(20), default='beginner')
    formula_used = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.Column(db.Integer, default=0)
    correct_attempts = db.Column(db.Integer, default=0)

class GrammarRule(db.Model):
    """Grammar rules for language learning"""
    id = db.Column(db.Integer, primary_key=True)
    field = db.Column(db.String(50), nullable=False)  # 'english' or 'danish'
    title = db.Column(db.String(200), nullable=False)
    rule_text = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text)  # JSON string of examples
    exceptions = db.Column(db.Text)
    category = db.Column(db.String(100))  # tenses, articles, prepositions, etc.
    difficulty = db.Column(db.String(20), default='beginner')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
