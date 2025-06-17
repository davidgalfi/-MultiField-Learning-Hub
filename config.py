# config.py - Configuration management
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///learning_hub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Field themes configuration
    THEMES = {
        'math-theme': {
            'primary_color': '#4CAF50',
            'secondary_color': '#81C784',
            'accent_color': '#2E7D32',
            'background': 'linear-gradient(135deg, #4CAF50 0%, #81C784 100%)',
            'font_family': 'STIX Two Text, serif'
        },
        'code-theme': {
            'primary_color': '#2196F3',
            'secondary_color': '#64B5F6',
            'accent_color': '#1976D2',
            'background': 'linear-gradient(135deg, #2196F3 0%, #64B5F6 100%)',
            'font_family': 'Fira Code, monospace'
        },
        'language-theme': {
            'primary_color': '#FF9800',
            'secondary_color': '#FFB74D',
            'accent_color': '#F57C00',
            'background': 'linear-gradient(135deg, #FF9800 0%, #FFB74D 100%)',
            'font_family': 'Merriweather, serif'
        },
        'danish-theme': {
            'primary_color': '#F44336',
            'secondary_color': '#EF5350',
            'accent_color': '#D32F2F',
            'background': 'linear-gradient(135deg, #F44336 0%, #EF5350 100%)',
            'font_family': 'Open Sans, sans-serif'
        },
        'recipe-theme': {
            'primary_color': '#8BC34A',
            'secondary_color': '#AED581',
            'accent_color': '#689F38',
            'background': 'linear-gradient(135deg, #8BC34A 0%, #AED581 100%)',
            'font_family': 'Playfair Display, serif'
        }
    }
    
    # Animation settings
    ANIMATIONS = {
        'fade_duration': '0.6s',
        'slide_duration': '0.8s',
        'bounce_duration': '1.2s',
        'scale_duration': '0.4s'
    }
