"""
API routes for the application
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
import asyncio
import os
import json
import datetime
from functools import wraps
from config import Config
from analyzers.perplexity_analyzer import PerplexityAnalyzer

api = Blueprint('api', __name__)

@api.route('/analyze', methods=['POST'])
async def analyze():
    """
    Handle analysis requests
    """
    try:
        # Ensure we have JSON data
        if not request.is_json:
            current_app.logger.error("Invalid content type")
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 415

        data = request.get_json()
        
        if not data or 'text' not in data:
            current_app.logger.error("No text provided")
            return jsonify({
                'error': 'No text provided'
            }), 400

        # Process the analysis request
        try:
            text = data['text']
            methods = data.get('methods', ['all'])
            use_ai = data.get('use_ai', True)

            # Log analysis start
            current_app.logger.info(f"Starting analysis for methods: {methods}")

            # Perform analysis with timeout
            try:
                analyzer = PerplexityAnalyzer()
                results = await analyzer.analyze(text)
                
                if not results:
                    raise ValueError("Analysis returned no results")
                
                # Save results for later retrieval
                result_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                results_dir = os.path.join(Config.RESULTS_DIR)
                os.makedirs(results_dir, exist_ok=True)
                
                with open(os.path.join(results_dir, f"{result_id}.json"), 'w') as f:
                    json.dump(results, f)
                
                # Add ID to results
                results['id'] = result_id
                
                current_app.logger.info(f"Analysis completed successfully. Result ID: {result_id}")
                return jsonify(results)

            except asyncio.TimeoutError:
                current_app.logger.error("Analysis timed out")
                return jsonify({
                    'error': 'Analysis timed out. Please try with shorter text.'
                }), 504

        except Exception as e:
            current_app.logger.error(f"Analysis error: {str(e)}")
            return jsonify({
                'error': f'Analysis failed: {str(e)}'
            }), 500

    except Exception as e:
        current_app.logger.error(f"Request processing error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500
