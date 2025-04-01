"""
Main application entry point
"""

import os
import logging
import sys
from pathlib import Path
import json
import datetime
import asyncio

# Ensure the current directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Flask imports
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Third party imports
import aiohttp
import httpx
from asgiref.wsgi import WsgiToAsgi

# Local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyzers.perplexity_analyzer import PerplexityAnalyzer
from utils.logger import setup_logger
from config import Config  # Import Config class
from generators import AVAILABLE_GENERATORS
from api.routes import api_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Setup logging
logger = setup_logger('app', os.path.join(os.path.dirname(__file__), 'logs'))

# Create error handlers
def handle_400_error(error):
    """Handle 400 errors"""
    logger.error(f"400 error: {error}")
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

def handle_404_error(error):
    """Handle 404 errors"""
    logger.error(f"404 error: {error}")
    return render_template('404.html'), 404

def handle_500_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return render_template('500.html'), 500

# Register error handlers
app.register_error_handler(400, handle_400_error)
app.register_error_handler(404, handle_404_error)
app.register_error_handler(500, handle_500_error)

# Đăng ký blueprint trong phần setup app
app.register_blueprint(api_bp)

@app.route('/', methods=['GET'])
async def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
async def analyze():
    """Handle analysis form submission and results display"""
    if request.method == 'GET':
        # Display results from storage
        result_id = request.args.get('id', 'latest')
        
        # Initialize results_dir if it doesn't exist
        results_dir = os.path.join(Config.RESULTS_DIR)
        os.makedirs(results_dir, exist_ok=True)
        
        # Get latest result file if id is 'latest'
        if result_id == 'latest':
            result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
            if not result_files:
                return render_template('results.html', error="No analysis results found")
            
            result_files.sort(key=lambda f: os.path.getmtime(os.path.join(results_dir, f)), reverse=True)
            result_id = result_files[0].split('.')[0]
        
        # Try to load the results
        result_path = os.path.join(results_dir, f"{result_id}.json")
        try:
            if not os.path.exists(result_path):
                return render_template('results.html', error=f"Result with ID {result_id} not found")
            
            with open(result_path, 'r') as f:
                results = json.load(f)
            return render_template('results.html', results=results)
        except Exception as e:
            logger.error(f"Error loading result file {result_path}: {str(e)}")
            return render_template('results.html', error=f"Error loading results: {str(e)}")
    
    else:  # POST request
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
                
            # Initialize analyzer with validation
            try:
                analyzers = {"perplexity": PerplexityAnalyzer()}
            except Exception as e:
                logger.error(f"Error initializing analyzers: {str(e)}")
                # Return default content
                return render_template('results.html', results=get_default_results())
                
            # Perform analysis with enhanced error handling
            try:
                # Get basic analysis from perplexity
                analysis_results = await analyzers["perplexity"].analyze(text)
                
                # Apply requested generators to the analysis results
                generated_content = {}
                
                # Determine which generators to run
                generator_keys = list(AVAILABLE_GENERATORS.keys())
                if methods and 'all' not in methods:
                    generator_keys = [key for key in methods if key in AVAILABLE_GENERATORS]
                
                # Run the generators
                for key in generator_keys:
                    if key in AVAILABLE_GENERATORS:
                        try:
                            generator_fn = AVAILABLE_GENERATORS[key]
                            generated_content[key] = generator_fn(analysis_results)
                            logger.info(f"Successfully generated {key} content")
                        except Exception as e:
                            logger.error(f"Error generating {key} content: {str(e)}", exc_info=True)
                            generated_content[key] = {"error": f"Failed to generate {key} content: {str(e)}"}
                
                # Combine results
                final_results = {
                    "analysis": analysis_results,
                    "content": generated_content,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "text": text[:500] + "..." if len(text) > 500 else text  # Include truncated original text
                }
                
                # Save results
                result_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                results_dir = os.path.join(Config.RESULTS_DIR)
                os.makedirs(results_dir, exist_ok=True)
                
                with open(os.path.join(results_dir, f"{result_id}.json"), 'w') as f:
                    json.dump(final_results, f, indent=2)
                
                # Return results with ID for future reference
                final_results["id"] = result_id
                return jsonify(final_results)
                
            except ValueError as e:
                if "API key" in str(e):
                    return jsonify({
                        'error': str(e),
                        'help': "Update your .env file with a valid Perplexity API key"
                    }), 503
                return jsonify({'error': str(e)}), 400
            except aiohttp.ClientError as e:
                logger.error(f"API connection error: {str(e)}", exc_info=True)
                return jsonify({
                    'error': "Cannot connect to Perplexity API",
                    'details': str(e)
                }), 503
            except Exception as e:
                logger.error(f"Analysis error: {str(e)}", exc_info=True)
                return jsonify({'error': "Internal server error"}), 500
                
        except Exception as e:
            logger.error(f"Request processing error: {str(e)}", exc_info=True)
            return jsonify({'error': "Internal server error"}), 500

def get_default_results():
    """Return default results when API is unavailable"""
    return {
        "questions": ["What are the key concepts presented in this text?", 
                     "How do these ideas relate to real-world applications?"],
        "explanations": ["Basic explanation: The text discusses fundamental principles.",
                        "Advanced explanation: The concepts require deeper analysis."],
        "practice": ["Explain the main thesis in your own words.",
                    "Compare and contrast the different viewpoints presented."],
        "key_terms": ["Term 1: Basic definition", 
                     "Term 2: Technical meaning", 
                     "Term 3: Contextual usage"],
        "summary": ["This text explores important concepts and their applications."]
    }

if __name__ == '__main__':
    try:
        # Import uvicorn only when needed
        import uvicorn
        
        # Convert WSGI app to ASGI
        asgi_app = WsgiToAsgi(app)
        
        # Run with uvicorn
        logger.info("Starting server...")
        uvicorn.run(
            asgi_app,
            host="127.0.0.1",
            port=5000,
            log_level="info",
            timeout_keep_alive=60  # Increase keep-alive timeout
        )
    except ImportError as e:
        logger.error(f"Failed to import uvicorn: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise