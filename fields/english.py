from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import FlashCard, GrammarRule, BlogPost, db
import json
import random
from datetime import datetime

english_bp = Blueprint('english', __name__, template_folder='../templates/fields/english')

@english_bp.route('/')
def index():
    """English learning overview"""
    # Get recent content
    recent_flashcards = FlashCard.query.filter_by(field='english').order_by(FlashCard.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(field='english').order_by(BlogPost.created_at.desc()).limit(3).all()
    
    # Get statistics
    stats = {
        'total_flashcards': FlashCard.query.filter_by(field='english').count(),
        'total_posts': BlogPost.query.filter_by(field='english').count(),
        'grammar_rules': GrammarRule.query.filter_by(field='english').count(),
        'categories': get_english_categories()
    }
    
    return render_template('english/index.html',
                         recent_flashcards=recent_flashcards,
                         recent_posts=recent_posts,
                         stats=stats,
                         field_key='english')

@english_bp.route('/flashcards')
def flashcards():
    """Flash cards listing and practice"""
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    
    query = FlashCard.query.filter_by(field='english')
    
    if category != 'all':
        query = query.filter(FlashCard.category == category)
    
    if difficulty != 'all':
        query = query.filter(FlashCard.difficulty == difficulty)
    
    flashcards = query.order_by(FlashCard.created_at.desc()).all()
    categories = get_english_categories()
    
    return render_template('english/flashcards.html',
                         flashcards=flashcards,
                         categories=categories,
                         current_category=category,
                         current_difficulty=difficulty)

@english_bp.route('/flashcards/practice')
def practice_flashcards():
    """Flash card practice session"""
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    count = int(request.args.get('count', 10))
    
    query = FlashCard.query.filter_by(field='english')
    
    if category != 'all':
        query = query.filter(FlashCard.category == category)
    
    if difficulty != 'all':
        query = query.filter(FlashCard.difficulty == difficulty)
    
    # Get random cards for practice
    all_cards = query.all()
    practice_cards = random.sample(all_cards, min(count, len(all_cards)))
    
    return render_template('english/practice.html',
                         cards=practice_cards,
                         session_config={
                             'category': category,
                             'difficulty': difficulty,
                             'count': count
                         })

@english_bp.route('/api/flashcards', methods=['POST'])
def create_flashcard():
    """Create new flash card"""
    data = request.get_json()
    
    try:
        flashcard = FlashCard(
            field='english',
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
            'message': 'Flash card created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@english_bp.route('/api/flashcards/<int:card_id>/review', methods=['POST'])
def review_flashcard(card_id):
    """Record flash card review"""
    flashcard = FlashCard.query.get_or_404(card_id)
    data = request.get_json()
    
    is_correct = data.get('correct', False)
    
    flashcard.times_reviewed += 1
    if is_correct:
        flashcard.correct_answers += 1
    
    db.session.commit()
    
    success_rate = (flashcard.correct_answers / flashcard.times_reviewed * 100) if flashcard.times_reviewed > 0 else 0
    
    return jsonify({
        'success': True,
        'times_reviewed': flashcard.times_reviewed,
        'correct_answers': flashcard.correct_answers,
        'success_rate': round(success_rate, 1)
    })

@english_bp.route('/grammar')
def grammar():
    """Grammar rules and exercises"""
    category = request.args.get('category', 'all')
    
    query = GrammarRule.query.filter_by(field='english')
    
    if category != 'all':
        query = query.filter(GrammarRule.category == category)
    
    grammar_rules = query.order_by(GrammarRule.created_at.desc()).all()
    categories = get_grammar_categories()
    
    return render_template('english/grammar.html',
                         grammar_rules=grammar_rules,
                         categories=categories,
                         current_category=category)

def get_english_categories():
    """Get English learning categories"""
    return ['vocabulary', 'grammar', 'pronunciation', 'idioms', 'business', 'academic']

def get_grammar_categories():
    """Get grammar categories"""
    return ['tenses', 'articles', 'prepositions', 'conditionals', 'passive-voice', 'reported-speech']
