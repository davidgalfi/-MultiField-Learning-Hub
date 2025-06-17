from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from database import db
from models import FlashCard, GrammarRule, BlogPost
import json
import random
from datetime import datetime

danish_bp = Blueprint('danish', __name__)

@danish_bp.route('/')
def index():
    """Danish learning overview"""
    # Get recent content
    recent_flashcards = FlashCard.query.filter_by(field='danish').order_by(FlashCard.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(field='danish').order_by(BlogPost.created_at.desc()).limit(3).all()
    
    # Get statistics
    stats = {
        'total_flashcards': FlashCard.query.filter_by(field='danish').count(),
        'total_posts': BlogPost.query.filter_by(field='danish').count(),
        'grammar_rules': GrammarRule.query.filter_by(field='danish').count(),
        'categories': get_danish_categories(),
        'difficulty_distribution': get_danish_difficulty_distribution()
    }
    
    # Get field info from global config
    from app import FIELDS_CONFIG
    field_info = FIELDS_CONFIG.get('danish', {})
    
    return render_template('danish/index.html',
                         recent_flashcards=recent_flashcards,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='danish',
                         field_info=field_info)

@danish_bp.route('/flashcards')
def flashcards():
    """Danish flash cards listing and practice"""
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    
    query = FlashCard.query.filter_by(field='danish')
    
    if category != 'all':
        query = query.filter(FlashCard.category == category)
    
    if difficulty != 'all':
        query = query.filter(FlashCard.difficulty == difficulty)
    
    flashcards = query.order_by(FlashCard.created_at.desc()).all()
    categories = get_danish_categories()
    
    return render_template('danish/flashcards.html',
                         flashcards=flashcards,
                         categories=categories,
                         current_category=category,
                         current_difficulty=difficulty)

@danish_bp.route('/culture')
def culture():
    """Danish culture and context learning"""
    cultural_topics = get_cultural_topics()
    
    return render_template('danish/culture.html',
                         topics=cultural_topics,
                         field_key='danish')

@danish_bp.route('/pronunciation')
def pronunciation():
    """Danish pronunciation guide"""
    pronunciation_rules = get_pronunciation_rules()
    
    return render_template('danish/pronunciation.html',
                         rules=pronunciation_rules,
                         field_key='danish')

@danish_bp.route('/api/flashcards', methods=['POST'])
def create_flashcard():
    """Create new Danish flash card"""
    data = request.get_json()
    
    try:
        flashcard = FlashCard(
            field='danish',
            front_text=data['front_text'],
            back_text=data['back_text'],
            category=data.get('category', 'vocabulary'),
            difficulty=data.get('difficulty', 'beginner')
        )
        
        db.session.add(flashcard)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': flashcard.id,
            'message': 'Danish flash card created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@danish_bp.route('/api/cultural-quiz')
def cultural_quiz():
    """Get random Danish cultural quiz questions"""
    questions = get_cultural_quiz_questions()
    random_questions = random.sample(questions, min(5, len(questions)))
    
    return jsonify({
        'questions': random_questions,
        'total': len(random_questions)
    })

def get_danish_categories():
    """Get Danish learning categories"""
    return ['vocabulary', 'grammar', 'pronunciation', 'culture', 'phrases', 'numbers']

def get_danish_difficulty_distribution():
    """Get difficulty distribution for Danish content"""
    difficulties = ['beginner', 'intermediate', 'advanced']
    distribution = {}
    
    for difficulty in difficulties:
        count = FlashCard.query.filter_by(field='danish', difficulty=difficulty).count()
        distribution[difficulty] = count
    
    return distribution

def get_cultural_topics():
    """Get Danish cultural learning topics"""
    return [
        {
            'title': 'Danish Hygge',
            'description': 'Understanding the concept of hygge in Danish culture',
            'content': 'Hygge is a Danish concept of cozy contentment and well-being through enjoying simple things.',
            'examples': ['Candlelit dinners', 'Cozy reading nooks', 'Quality time with friends'],
            'pronunciation': '[HOO-gah]'
        },
        {
            'title': 'Danish Food Culture',
            'description': 'Traditional Danish cuisine and dining customs',
            'content': 'Danish food culture emphasizes simplicity, quality ingredients, and seasonal eating.',
            'examples': ['Smørrebrød (open sandwiches)', 'Frikadeller (meatballs)', 'Rugbrød (rye bread)'],
            'pronunciation': '[SMUR-uh-brurth]'
        },
        {
            'title': 'Danish Social Customs',
            'description': 'Understanding Danish social behavior and etiquette',
            'content': 'Danes value punctuality, equality, and direct communication.',
            'examples': ['Being on time', 'Removing shoes indoors', 'Direct but polite communication'],
            'pronunciation': None
        }
    ]

def get_pronunciation_rules():
    """Get Danish pronunciation rules and examples"""
    return [
        {
            'rule': 'Stød (Glottal Stop)',
            'description': 'A unique Danish feature - a brief pause or catch in the voice',
            'examples': [
                {'word': 'hund', 'pronunciation': '[hun´]', 'meaning': 'dog'},
                {'word': 'bog', 'pronunciation': '[bo´]', 'meaning': 'book'}
            ]
        },
        {
            'rule': 'Silent D',
            'description': 'The letter D is often silent at the end of words',
            'examples': [
                {'word': 'mad', 'pronunciation': '[mah]', 'meaning': 'food'},
                {'word': 'ved', 'pronunciation': '[veh]', 'meaning': 'know'}
            ]
        },
        {
            'rule': 'Soft D',
            'description': 'When pronounced, D sounds like the "th" in "the"',
            'examples': [
                {'word': 'hedder', 'pronunciation': '[heh-ther]', 'meaning': 'is called'},
                {'word': 'åbne', 'pronunciation': '[awb-neh]', 'meaning': 'to open'}
            ]
        }
    ]

def get_cultural_quiz_questions():
    """Get cultural quiz questions for interactive learning"""
    return [
        {
            'question': 'What does "hygge" mean?',
            'options': ['Cozy contentment', 'Being busy', 'Formal dining', 'Exercise'],
            'correct': 0,
            'explanation': 'Hygge is about cozy contentment and enjoying simple pleasures.'
        },
        {
            'question': 'What is smørrebrød?',
            'options': ['A type of beer', 'Open sandwiches', 'Danish pastry', 'A greeting'],
            'correct': 1,
            'explanation': 'Smørrebrød are traditional Danish open-faced sandwiches.'
        },
        {
            'question': 'How many people speak Danish worldwide?',
            'options': ['About 3 million', 'About 6 million', 'About 10 million', 'About 15 million'],
            'correct': 1,
            'explanation': 'Approximately 6 million people speak Danish, mainly in Denmark.'
        }
    ]
