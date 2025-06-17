# app.py - Add context processor for global template variables
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from database import db, migrate, init_db
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_hub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Import models AFTER initializing db
from models import *

# Field configuration
FIELDS_CONFIG = {
    'mathematics': {
        'name': 'Mathematics',
        'icon': 'fas fa-calculator',
        'color': '#4CAF50',
        'theme': 'math-theme',
        'description': 'Explore the world of numbers, equations, and mathematical concepts',
        'features': ['Problem Solving', 'Formulas', 'Visual Learning', 'Practice Tests']
    },
    'programming': {
        'name': 'Programming',
        'icon': 'fas fa-code',
        'color': '#2196F3',
        'theme': 'code-theme',
        'description': 'Master coding with examples in Python, Java, C# and more',
        'features': ['Code Examples', 'Tutorials', 'Best Practices', 'Project Ideas']
    },
    'english': {
        'name': 'English Learning',
        'icon': 'fas fa-language',
        'color': '#FF9800',
        'theme': 'language-theme',
        'description': 'Improve your English with interactive lessons and practice',
        'features': ['Flash Cards', 'Grammar', 'Practice Tests', 'Pronunciation']
    },
    'danish': {
        'name': 'Danish Learning',
        'icon': 'fas fa-flag',
        'color': '#F44336',
        'theme': 'danish-theme',
        'description': 'Learn Danish language and culture effectively',
        'features': ['Flash Cards', 'Grammar', 'Cultural Notes', 'Speaking Practice']
    },
    'recipes': {
        'name': 'Vegan Recipes',
        'icon': 'fas fa-leaf',
        'color': '#8BC34A',
        'theme': 'recipe-theme',
        'description': 'Delicious plant-based recipes for healthy living',
        'features': ['Recipe Cards', 'Nutrition Info', 'Meal Planning', 'Cooking Tips']
    }
}

# Make FIELDS_CONFIG available to all templates
@app.context_processor
def inject_fields_config():
    return {'fields': FIELDS_CONFIG}

# Now update mathematics blueprint to use global config
def get_field_info(field_key):
    """Get field info from global config"""
    return FIELDS_CONFIG.get(field_key, {})

# Register blueprints function
def register_blueprints():
    """Register all blueprints"""
    from fields.mathematics import math_bp
    from fields.programming import programming_bp
    from fields.english import english_bp
    from fields.danish import danish_bp
    from fields.recipes import recipes_bp

    app.register_blueprint(math_bp, url_prefix='/mathematics')
    app.register_blueprint(programming_bp, url_prefix='/programming')
    app.register_blueprint(english_bp, url_prefix='/english')
    app.register_blueprint(danish_bp, url_prefix='/danish')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')

@app.route('/')
def home():
    """Dashboard/Home page with field overview"""
    return render_template('dashboard.html', fields=FIELDS_CONFIG)

@app.route('/api/fields')
def api_fields():
    """API endpoint for field configuration"""
    return jsonify(FIELDS_CONFIG)

if __name__ == '__main__':
    register_blueprints()
    
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5006)