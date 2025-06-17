from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import MathProblem, BlogPost, db
import json
from datetime import datetime

math_bp = Blueprint('mathematics', __name__, template_folder='../templates/fields/mathematics')

@math_bp.route('/')
def index():
    """Mathematics field overview"""
    # Get recent problems and posts
    recent_problems = MathProblem.query.order_by(MathProblem.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(field='mathematics').order_by(BlogPost.created_at.desc()).limit(3).all()
    
    # Get statistics
    stats = {
        'total_problems': MathProblem.query.count(),
        'total_posts': BlogPost.query.filter_by(field='mathematics').count(),
        'categories': get_math_categories(),
        'difficulty_distribution': get_difficulty_distribution()
    }
    
    return render_template('mathematics/index.html', 
                         recent_problems=recent_problems,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='mathematics')

@math_bp.route('/problems')
def problems():
    """Mathematics problems listing"""
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    search = request.args.get('search', '')
    
    query = MathProblem.query
    
    if category != 'all':
        query = query.filter(MathProblem.category == category)
    
    if difficulty != 'all':
        query = query.filter(MathProblem.difficulty == difficulty)
    
    if search:
        query = query.filter(MathProblem.title.contains(search))
    
    problems = query.order_by(MathProblem.created_at.desc()).all()
    categories = get_math_categories()
    
    return render_template('mathematics/problems.html',
                         problems=problems,
                         categories=categories,
                         current_category=category,
                         current_difficulty=difficulty,
                         search_term=search)

@math_bp.route('/problems/<int:problem_id>')
def problem_detail(problem_id):
    """View specific math problem"""
    problem = MathProblem.query.get_or_404(problem_id)
    
    # Increment views
    problem.attempts += 1
    db.session.commit()
    
    # Get related problems
    related = MathProblem.query.filter(
        MathProblem.category == problem.category,
        MathProblem.id != problem.id
    ).limit(3).all()
    
    return render_template('mathematics/problem_detail.html',
                         problem=problem,
                         related_problems=related)

@math_bp.route('/api/problems', methods=['POST'])
def create_problem():
    """Create new math problem"""
    data = request.get_json()
    
    try:
        problem = MathProblem(
            title=data['title'],
            problem_text=data['problem_text'],
            solution=data['solution'],
            explanation=data.get('explanation', ''),
            category=data.get('category', 'algebra'),
            difficulty=data.get('difficulty', 'beginner'),
            formula_used=data.get('formula_used', '')
        )
        
        db.session.add(problem)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': problem.id,
            'message': 'Problem created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@math_bp.route('/api/problems/<int:problem_id>/attempt', methods=['POST'])
def attempt_problem(problem_id):
    """Record problem attempt"""
    problem = MathProblem.query.get_or_404(problem_id)
    data = request.get_json()
    
    is_correct = data.get('correct', False)
    
    problem.attempts += 1
    if is_correct:
        problem.correct_attempts += 1
    
    db.session.commit()
    
    success_rate = (problem.correct_attempts / problem.attempts * 100) if problem.attempts > 0 else 0
    
    return jsonify({
        'success': True,
        'attempts': problem.attempts,
        'correct_attempts': problem.correct_attempts,
        'success_rate': round(success_rate, 1)
    })

@math_bp.route('/formulas')
def formulas():
    """Mathematical formulas reference"""
    formulas_by_category = get_formulas_by_category()
    
    return render_template('mathematics/formulas.html',
                         formulas=formulas_by_category)

def get_math_categories():
    """Get available math categories"""
    return ['algebra', 'calculus', 'geometry', 'statistics', 'discrete', 'linear-algebra']

def get_difficulty_distribution():
    """Get difficulty distribution for stats"""
    difficulties = ['beginner', 'intermediate', 'advanced']
    distribution = {}
    
    for difficulty in difficulties:
        count = MathProblem.query.filter_by(difficulty=difficulty).count()
        distribution[difficulty] = count
    
    return distribution

def get_formulas_by_category():
    """Get mathematical formulas organized by category"""
    return {
        'algebra': [
            {
                'name': 'Quadratic Formula',
                'formula': r'x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}',
                'description': 'Solves quadratic equations of the form ax² + bx + c = 0'
            },
            {
                'name': 'Binomial Theorem',
                'formula': r'(a + b)^n = \sum_{k=0}^{n} \binom{n}{k} a^{n-k} b^k',
                'description': 'Expansion of binomial expressions'
            }
        ],
        'calculus': [
            {
                'name': 'Derivative of Power Function',
                'formula': r'\frac{d}{dx}x^n = nx^{n-1}',
                'description': 'Basic differentiation rule for power functions'
            },
            {
                'name': 'Integration by Parts',
                'formula': r'\int u \, dv = uv - \int v \, du',
                'description': 'Method for integrating products of functions'
            }
        ],
        'geometry': [
            {
                'name': 'Circle Area',
                'formula': r'A = \pi r^2',
                'description': 'Area of a circle with radius r'
            },
            {
                'name': 'Pythagorean Theorem',
                'formula': r'a^2 + b^2 = c^2',
                'description': 'Relationship between sides of a right triangle'
            }
        ]
    }
