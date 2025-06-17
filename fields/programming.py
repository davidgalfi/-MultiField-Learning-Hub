from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import CodeExample, BlogPost, db
import json
from datetime import datetime

programming_bp = Blueprint('programming', __name__, template_folder='../templates/fields/programming')

@programming_bp.route('/')
def index():
    """Programming field overview"""
    # Get recent examples and posts
    recent_examples = CodeExample.query.order_by(CodeExample.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(field='programming').order_by(BlogPost.created_at.desc()).limit(3).all()
    
    # Get statistics
    stats = {
        'total_examples': CodeExample.query.count(),
        'total_posts': BlogPost.query.filter_by(field='programming').count(),
        'languages': get_programming_languages(),
        'categories': get_programming_categories(),
        'language_distribution': get_language_distribution()
    }
    
    return render_template('programming/index.html',
                         recent_examples=recent_examples,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='programming')

@programming_bp.route('/examples')
def examples():
    """Code examples listing"""
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
        query = query.filter(CodeExample.title.contains(search))
    
    examples = query.order_by(CodeExample.created_at.desc()).all()
    
    return render_template('programming/examples.html',
                         examples=examples,
                         languages=get_programming_languages(),
                         categories=get_programming_categories(),
                         current_language=language,
                         current_category=category,
                         current_difficulty=difficulty,
                         search_term=search)

@programming_bp.route('/examples/<int:example_id>')
def example_detail(example_id):
    """View specific code example"""
    example = CodeExample.query.get_or_404(example_id)
    
    # Get related examples
    related = CodeExample.query.filter(
        CodeExample.language == example.language,
        CodeExample.id != example.id
    ).limit(3).all()
    
    return render_template('programming/example_detail.html',
                         example=example,
                         related_examples=related)

@programming_bp.route('/api/examples', methods=['POST'])
def create_example():
    """Create new code example"""
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
def like_example(example_id):
    """Like a code example"""
    example = CodeExample.query.get_or_404(example_id)
    example.likes += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'likes': example.likes
    })

@programming_bp.route('/tutorials')
def tutorials():
    """Programming tutorials"""
    tutorials_data = get_programming_tutorials()
    
    return render_template('programming/tutorials.html',
                         tutorials=tutorials_data)

@programming_bp.route('/playground')
def playground():
    """Code playground for testing"""
    return render_template('programming/playground.html',
                         languages=get_programming_languages())

def get_programming_languages():
    """Get supported programming languages"""
    return ['python', 'javascript', 'java', 'csharp', 'cpp', 'go', 'rust', 'php', 'ruby']

def get_programming_categories():
    """Get programming categories"""
    return ['algorithms', 'data-structures', 'web-development', 'desktop-apps', 'apis', 'databases', 'testing', 'deployment']

def get_language_distribution():
    """Get language distribution for stats"""
    languages = get_programming_languages()
    distribution = {}
    
    for language in languages:
        count = CodeExample.query.filter_by(language=language).count()
        distribution[language] = count
    
    return distribution

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
        ]
    }
