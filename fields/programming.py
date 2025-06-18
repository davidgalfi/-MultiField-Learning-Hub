# fields/programming.py - Enhanced programming field blueprint
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import CodeExample, BlogPost
import json
from datetime import datetime

programming_bp = Blueprint('programming', __name__)

@programming_bp.route('/')
def index():
    """Programming field overview"""
    recent_examples = CodeExample.query.order_by(CodeExample.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(field='programming').order_by(BlogPost.created_at.desc()).limit(3).all()
    
    stats = {
        'total_examples': CodeExample.query.count(),
        'total_posts': BlogPost.query.filter_by(field='programming').count(),
        'languages': get_programming_languages(),
        'language_distribution': get_language_distribution(),
        'categories': get_programming_categories()
    }

    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/index.html',
                         recent_examples=recent_examples,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/examples')
def examples():
    """Code examples listing with filtering"""
    language = request.args.get('language', 'all')
    category = request.args.get('category', 'all') 
    difficulty = request.args.get('difficulty', 'all')
    search = request.args.get('search', '')
    
    query = CodeExample.query
    
    if language != 'all':
        query = query.filter(CodeExample.language == language)
    
    if category != 'all':
        query = query.filter(CodeExample.category == category)
        
    if difficulty != 'all':
        query = query.filter(CodeExample.difficulty == difficulty)
    
    if search:
        query = query.filter(
            (CodeExample.title.contains(search)) |
            (CodeExample.description.contains(search)) |
            (CodeExample.tags.contains(search))
        )
    
    examples = query.order_by(CodeExample.created_at.desc()).all()
    
    return render_template('programming/examples.html',
                         examples=examples,
                         languages=get_programming_languages(),
                         categories=get_programming_categories(),
                         current_language=language,
                         current_category=category,
                         current_difficulty=difficulty,
                         search_term=search,
                         field_key='programming',
                         field_info=FIELDS_CONFIG.get('programming', {}))

@programming_bp.route('/examples/<int:example_id>')
def example_detail(example_id):
    """View specific code example"""
    example = CodeExample.query.get_or_404(example_id)
    
    # Increment views/likes
    example.likes += 1
    db.session.commit()
    
    # Get related examples
    related = CodeExample.query.filter(
        CodeExample.language == example.language,
        CodeExample.id != example.id
    ).limit(3).all()
    
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/example_detail.html',
                         example=example,
                         related_examples=related,
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/examples/create')
def create_example_form():
    """Show create code example form"""
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/create_example.html',
                         languages=get_programming_languages(),
                         categories=get_programming_categories(),
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/blog')
def blog_posts():
    """Programming blog posts listing"""
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    posts = BlogPost.query.filter_by(field='programming').order_by(
        BlogPost.created_at.desc()
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/blog_posts.html',
                         posts=posts,
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/blog/create')
def create_blog_post_form():
    """Show create programming blog post form"""
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/create_post.html',
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/blog/<int:post_id>')
def blog_post_detail(post_id):
    """View specific programming blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    # Increment views
    post.views += 1
    db.session.commit()
    
    # Get related posts
    related = BlogPost.query.filter(
        BlogPost.field == 'programming',
        BlogPost.id != post.id
    ).limit(3).all()
    
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/blog_post_detail.html',
                         post=post,
                         related_posts=related,
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/playground')
def code_playground():
    """Interactive code playground"""
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/playground.html',
                         languages=get_programming_languages(),
                         field_key='programming',
                         field_info=field_info)

@programming_bp.route('/tutorials')
def tutorials():
    """Programming tutorials listing"""
    tutorials_data = get_programming_tutorials()
    
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('programming', {})
    
    return render_template('programming/tutorials.html',
                         tutorials=tutorials_data,
                         field_key='programming',
                         field_info=field_info)

# API Routes
@programming_bp.route('/api/examples', methods=['POST'])
def api_create_example():
    """API endpoint to create code example"""
    data = request.get_json()
    
    try:
        example = CodeExample(
            title=data['title'],
            description=data.get('description', ''),
            language=data['language'],
            code=data['code'],
            explanation=data.get('explanation', ''),
            difficulty=data.get('difficulty', 'beginner'),
            category=data.get('category', 'general'),
            tags=data.get('tags', '')
        )
        
        db.session.add(example)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': example.id,
            'message': 'Code example created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@programming_bp.route('/api/examples/<int:example_id>/like', methods=['POST'])
def api_like_example(example_id):
    """Like a code example"""
    try:
        example = CodeExample.query.get_or_404(example_id)
        example.likes += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes': example.likes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@programming_bp.route('/api/blog/posts', methods=['POST'])
def api_create_blog_post():
    """API endpoint to create programming blog post"""
    data = request.get_json()
    
    try:
        # Calculate reading time
        word_count = len(data.get('content', '').split())
        reading_time = max(1, round(word_count / 200))
        
        blog_post = BlogPost(
            title=data['title'],
            content=data['content'],
            field='programming',
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
def get_programming_languages():
    """Get supported programming languages"""
    return ['python', 'javascript', 'java', 'csharp', 'cpp', 'go', 'rust', 'php', 'ruby', 'typescript', 'swift', 'kotlin']

def get_programming_categories():
    """Get programming categories"""
    return ['algorithms', 'data-structures', 'web-development', 'mobile-development', 'desktop-apps', 'apis', 'databases', 'testing', 'deployment', 'machine-learning', 'game-development', 'security']

def get_language_distribution():
    """Get language distribution for stats, sorted by popularity."""
    languages = get_programming_languages()
    distribution = {}
    
    for language in languages:
        count = CodeExample.query.filter_by(language=language).count()
        if count > 0:  # Only include languages with at least one example
            distribution[language] = count
    
    # Sort the dictionary by count (value) in descending order
    sorted_distribution = sorted(distribution.items(), key=lambda item: item[1], reverse=True)
    
    return sorted_distribution

def get_programming_tutorials():
    """Get structured programming tutorials"""
    return {
        'python': [
            {
                'title': 'Python Basics',
                'description': 'Learn Python fundamentals',
                'lessons': ['Variables', 'Functions', 'Classes', 'Modules'],
                'difficulty': 'beginner'
            },
            {
                'title': 'Advanced Python',
                'description': 'Advanced Python concepts',
                'lessons': ['Decorators', 'Generators', 'Context Managers', 'Metaclasses'],
                'difficulty': 'advanced'
            }
        ],
        'javascript': [
            {
                'title': 'Modern JavaScript',
                'description': 'ES6+ features and best practices',
                'lessons': ['Arrow Functions', 'Promises', 'Async/Await', 'Modules'],
                'difficulty': 'intermediate'
            }
        ],
        'web-development': [
            {
                'title': 'Full Stack Development',
                'description': 'Complete web application development',
                'lessons': ['Frontend Frameworks', 'Backend APIs', 'Databases', 'Deployment'],
                'difficulty': 'intermediate'
            }
        ]
    }
