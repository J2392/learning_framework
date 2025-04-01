"""
API Routes for learning framework
"""
from flask import Blueprint, request, jsonify
import os
import logging
import json
import datetime
import asyncio
from analyzers.perplexity_analyzer import PerplexityAnalyzer
from utils.logger import setup_logger

# Khởi tạo blueprint và logger
api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = setup_logger('api', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))

@api_bp.route('/analyze', methods=['POST'])
async def analyze():
    """API endpoint for text analysis"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 415
                
        data = request.get_json()
        text = data.get('text', '').strip()
        methods = data.get('methods', ['all'])
            
        if not text:
            return jsonify({
                'error': 'Text content is required'
            }), 400
                
        # Initialize analyzer
        try:
            analyzer = PerplexityAnalyzer()
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            return jsonify({
                'error': f"API configuration error: {str(e)}",
                'help': "Please check your .env file and ensure PERPLEXITY_API_KEY is set correctly"
            }), 503
                
        # Perform analysis
        try:
            results = await analyzer.analyze(text)
            
            # Save results if needed
            result_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            with open(os.path.join(results_dir, f"{result_id}.json"), 'w') as f:
                json.dump(results, f)
            
            return jsonify(results)
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return jsonify({'error': str(e)}), 500
                
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500