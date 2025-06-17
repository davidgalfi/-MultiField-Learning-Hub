# fields/recipes.py
from flask import Blueprint
recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/')
def index():
    return "Recipes field - Coming soon!"
