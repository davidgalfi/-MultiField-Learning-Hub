# fields/danish.py
from flask import Blueprint
danish_bp = Blueprint('danish', __name__)

@danish_bp.route('/')
def index():
    return "Danish learning field - Coming soon!"
