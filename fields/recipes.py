from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import Recipe, BlogPost
import json
from datetime import datetime

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/')
def index():
    """Recipes field overview"""
    # Get recent recipes and posts
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(field='recipes').order_by(BlogPost.created_at.desc()).limit(3).all()
    
    # Get statistics
    stats = {
        'total_recipes': Recipe.query.count(),
        'total_posts': BlogPost.query.filter_by(field='recipes').count(),
        'categories': get_recipe_categories(),
        'avg_prep_time': get_average_prep_time(),
        'difficulty_distribution': get_recipe_difficulty_distribution()
    }
    
    # Get field info from global config
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('recipes', {})
    
    return render_template('recipes/index.html',
                         recent_recipes=recent_recipes,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='recipes',
                         field_info=field_info)

@recipes_bp.route('/browse')
def browse_recipes():
    """Browse all recipes with filtering"""
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    max_time = request.args.get('max_time', '')
    search = request.args.get('search', '')
    
    query = Recipe.query
    
    if category != 'all':
        query = query.filter(Recipe.category == category)
    
    if difficulty != 'all':
        query = query.filter(Recipe.difficulty == difficulty)
    
    if max_time:
        try:
            max_time_int = int(max_time)
            query = query.filter((Recipe.prep_time + Recipe.cook_time) <= max_time_int)
        except ValueError:
            pass
    
    if search:
        query = query.filter(Recipe.title.contains(search))
    
    recipes = query.order_by(Recipe.created_at.desc()).all()
    categories = get_recipe_categories()
    
    return render_template('recipes/browse.html',
                         recipes=recipes,
                         categories=categories,
                         current_category=category,
                         current_difficulty=difficulty,
                         max_time=max_time,
                         search_term=search)

@recipes_bp.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    """View specific recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Parse JSON fields
    ingredients = json.loads(recipe.ingredients) if recipe.ingredients else {}
    nutrition_info = json.loads(recipe.nutrition_info) if recipe.nutrition_info else {}
    
    # Get related recipes
    related = Recipe.query.filter(
        Recipe.category == recipe.category,
        Recipe.id != recipe.id
    ).limit(3).all()
    
    return render_template('recipes/detail.html',
                         recipe=recipe,
                         ingredients=ingredients,
                         nutrition_info=nutrition_info,
                         related_recipes=related)

@recipes_bp.route('/meal-plan')
def meal_plan():
    """Meal planning interface"""
    # Get recipes for meal planning
    breakfast_recipes = Recipe.query.filter_by(category='breakfast').limit(5).all()
    lunch_recipes = Recipe.query.filter_by(category='lunch').limit(5).all()
    dinner_recipes = Recipe.query.filter_by(category='dinner').limit(5).all()
    
    return render_template('recipes/meal_plan.html',
                         breakfast_recipes=breakfast_recipes,
                         lunch_recipes=lunch_recipes,
                         dinner_recipes=dinner_recipes,
                         field_key='recipes')

@recipes_bp.route('/nutrition-calculator')
def nutrition_calculator():
    """Nutrition calculator tool"""
    return render_template('recipes/nutrition_calculator.html',
                         field_key='recipes')

@recipes_bp.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Create new recipe"""
    data = request.get_json()
    
    try:
        recipe = Recipe(
            title=data['title'],
            description=data.get('description', ''),
            ingredients=json.dumps(data.get('ingredients', {})),
            instructions=data['instructions'],
            prep_time=data.get('prep_time', 0),
            cook_time=data.get('cook_time', 0),
            servings=data.get('servings', 1),
            difficulty=data.get('difficulty', 'easy'),
            category=data.get('category', 'main'),
            nutrition_info=json.dumps(data.get('nutrition_info', {}))
        )
        
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': recipe.id,
            'message': 'Recipe created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@recipes_bp.route('/api/recipes/<int:recipe_id>/rate', methods=['POST'])
def rate_recipe(recipe_id):
    """Rate a recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)
    data = request.get_json()
    
    new_rating = float(data.get('rating', 0))
    
    if recipe.rating_count == 0:
        recipe.rating = new_rating
        recipe.rating_count = 1
    else:
        # Calculate new average rating
        total_rating = recipe.rating * recipe.rating_count
        recipe.rating_count += 1
        recipe.rating = (total_rating + new_rating) / recipe.rating_count
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'new_rating': round(recipe.rating, 1),
        'rating_count': recipe.rating_count
    })

@recipes_bp.route('/api/weekly-meal-plan', methods=['POST'])
def generate_weekly_meal_plan():
    """Generate a weekly meal plan"""
    preferences = request.get_json()
    
    meal_plan = {}
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for day in days:
        day_plan = {}
        
        # Get random recipes for each meal
        if preferences.get('include_breakfast', True):
            breakfast = Recipe.query.filter_by(category='breakfast').order_by(db.func.random()).first()
            day_plan['breakfast'] = {
                'id': breakfast.id if breakfast else None,
                'title': breakfast.title if breakfast else 'No recipe found',
                'prep_time': breakfast.prep_time if breakfast else 0
            }
        
        if preferences.get('include_lunch', True):
            lunch = Recipe.query.filter_by(category='lunch').order_by(db.func.random()).first()
            day_plan['lunch'] = {
                'id': lunch.id if lunch else None,
                'title': lunch.title if lunch else 'No recipe found',
                'prep_time': lunch.prep_time if lunch else 0
            }
        
        if preferences.get('include_dinner', True):
            dinner = Recipe.query.filter_by(category='dinner').order_by(db.func.random()).first()
            day_plan['dinner'] = {
                'id': dinner.id if dinner else None,
                'title': dinner.title if dinner else 'No recipe found',
                'prep_time': dinner.prep_time if dinner else 0
            }
        
        meal_plan[day] = day_plan
    
    return jsonify({
        'success': True,
        'meal_plan': meal_plan
    })

def get_recipe_categories():
    """Get recipe categories"""
    return ['breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'beverage', 'appetizer', 'soup']

def get_average_prep_time():
    """Calculate average preparation time"""
    result = db.session.query(db.func.avg(Recipe.prep_time + Recipe.cook_time)).scalar()
    return round(result or 0, 1)

def get_recipe_difficulty_distribution():
    """Get difficulty distribution for recipes"""
    difficulties = ['easy', 'medium', 'hard']
    distribution = {}
    
    for difficulty in difficulties:
        count = Recipe.query.filter_by(difficulty=difficulty).count()
        distribution[difficulty] = count
    
    return distribution
