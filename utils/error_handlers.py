"""
Error handlers for the application
"""

from flask import jsonify
from typing import Tuple, Dict, Any

def handle_400_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle 400 Bad Request errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

def handle_404_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle 404 Not Found errors"""
    return jsonify({
        'error': 'Not Found',
        'message': str(error)
    }), 404

def handle_500_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle 500 Internal Server Error"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500