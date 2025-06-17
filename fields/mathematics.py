# fields/mathematics.py - Fixed with unique function names
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import MathProblem, BlogPost
import json
from datetime import datetime

math_bp = Blueprint('mathematics', __name__, template_folder='templates')

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

    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})
    
    return render_template('mathematics/index.html', 
                         recent_problems=recent_problems,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='mathematics',
                         field_info=field_info)

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
    
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})

    return render_template('mathematics/problems.html',
                         problems=problems,
                         categories=categories,
                         current_category=category,
                         current_difficulty=difficulty,
                         search_term=search,
                         field_key='mathematics',
                         field_info=field_info)

@math_bp.route('/api/problems/<int:problem_id>')
def api_problem_detail(problem_id):
    """API endpoint to get problem details"""
    try:
        problem = MathProblem.query.get_or_404(problem_id)
        
        return jsonify({
            'success': True,
            'problem': {
                'id': problem.id,
                'title': problem.title,
                'problem_text': problem.problem_text,
                'category': problem.category,
                'difficulty': problem.difficulty,
                'formula_used': problem.formula_used,
                'attempts': problem.attempts,
                'correct_attempts': problem.correct_attempts,
                'created_at': problem.created_at.isoformat() if problem.created_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

# fields/mathematics.py - Add the missing problem_detail route

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
    
    # Get field info
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})
    
    return render_template('mathematics/problem_detail.html',
                         problem=problem,
                         related_problems=related,
                         field_key='mathematics',
                         field_info=field_info)


@math_bp.route('/problems/create')
def create_problem_form():
    """Show create new math problem form with LaTeX editor"""
    # Get field info for styling
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})
    
    categories = get_math_categories()
    
    return render_template('mathematics/create_problem.html',
                         field_key='mathematics',
                         field_info=field_info,
                         categories=categories)

@math_bp.route('/api/problems', methods=['POST'])
def api_create_problem():
    """API endpoint to create math problem"""
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
            'message': 'Math problem created successfully'
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
    
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})

    return render_template('mathematics/formulas.html',
                         formulas=formulas_by_category,
                         field_key='mathematics',
                         field_info=field_info)

# Blog Routes
@math_bp.route('/blog')
def blog_posts():
    """List all math blog posts with search and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = 6
    search = request.args.get('search', '')
    tag = request.args.get('tag', '')
    
    # Build query
    query = BlogPost.query.filter_by(field='mathematics')
    
    # Apply search filter
    if search:
        query = query.filter(
            BlogPost.title.contains(search) | 
            BlogPost.content.contains(search) |
            BlogPost.tags.contains(search)
        )
    
    # Apply tag filter
    if tag:
        query = query.filter(BlogPost.tags.contains(tag))
    
    # Paginate results
    posts = query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get field info
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})
    
    return render_template('mathematics/blog_posts.html',
                         posts=posts,
                         field_key='mathematics',
                         field_info=field_info)

@math_bp.route('/blog/create')
def create_blog_post_form():
    """Show create new math blog post form with LaTeX editor"""
    # Get field info for styling
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})
    
    return render_template('mathematics/create_post.html',
                         field_key='mathematics',
                         field_info=field_info)

@math_bp.route('/blog/<int:post_id>')
def blog_post_detail(post_id):
    """View specific blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    # Increment views
    post.views += 1
    db.session.commit()
    
    # Get related posts
    related = BlogPost.query.filter(
        BlogPost.field == 'mathematics',
        BlogPost.id != post.id
    ).limit(3).all()
    
    # Get field info
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('mathematics', {})
    
    return render_template('mathematics/blog_post_detail.html',
                         post=post,
                         related_posts=related,
                         field_key='mathematics',
                         field_info=field_info)

# API Routes
@math_bp.route('/api/blog/posts', methods=['POST'])
def api_create_blog_post():
    """API endpoint to create blog post"""
    data = request.get_json()
    
    try:
        # Calculate reading time (rough estimate: 200 words per minute)
        word_count = len(data.get('content', '').split())
        reading_time = max(1, round(word_count / 200))
        
        blog_post = BlogPost(
            title=data['title'],
            content=data['content'],
            field='mathematics',
            author=data.get('author', 'Admin'),
            excerpt=data.get('excerpt', ''),
            tags=data.get('tags', ''),
            reading_time=reading_time,
            featured_image=data.get('featured_image', '')
        )
        
        db.session.add(blog_post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': blog_post.id,
            'message': 'Blog post created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Utility Functions
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
            },
            {
                'name': 'Difference of Squares',
                'formula': r'a^2 - b^2 = (a + b)(a - b)',
                'description': 'Factorization of difference of squares'
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
            },
            {
                'name': 'Fundamental Theorem of Calculus',
                'formula': r'\int_a^b f(x) \, dx = F(b) - F(a)',
                'description': 'Relationship between differentiation and integration'
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
            },
            {
                'name': 'Distance Formula',
                'formula': r'd = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}',
                'description': 'Distance between two points in 2D space'
            }
        ],
        'trigonometry': [
            {
                'name': 'Sine Rule',
                'formula': r'\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}',
                'description': 'Relationship between sides and angles in triangles'
            },
            {
                'name': 'Cosine Rule',
                'formula': r'c^2 = a^2 + b^2 - 2ab\cos C',
                'description': 'Generalization of Pythagorean theorem'
            },
            {
                'name': 'Euler\'s Formula',
                'formula': r'e^{i\theta} = \cos\theta + i\sin\theta',
                'description': 'Connection between trigonometry and complex exponentials'
            }
        ]
    }
