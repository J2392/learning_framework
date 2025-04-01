# api/perplexity.py
"""
Perplexity API integration
"""

from flask import Blueprint, request, jsonify
from config import Config
from analyzers.perplexity_analyzer import PerplexityAnalyzer

perplexity_api = Blueprint('perplexity_api', __name__)

@perplexity_api.route('/analyze', methods=['POST'])
async def analyze():
    """
    Handle Perplexity API analysis requests
    """
    try:
        if not Config.PERPLEXITY_API_KEY:
            return jsonify({
                'error': 'Perplexity API is not configured'
            }), 503

        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'error': 'No text provided'
            }), 400

        text = data['text']
        context = data.get('context', 'general')

        # Perform analysis
        analyzer = PerplexityAnalyzer()
        result = await analyzer.analyze(text)
        
        if result.get('error'):
            return jsonify({
                'error': result['error']
            }), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500