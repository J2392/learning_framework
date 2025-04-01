"""
Main application entry point
"""

from flask import Flask, render_template, request, jsonify
from typing import Dict, Any
import os
import asyncio
import httpx
import json
import datetime
from asgiref.wsgi import WsgiToAsgi
from flask_cors import CORS
from analyzers import PerplexityAnalyzer

try:
    from config import Config
    from api.routes import api
    from api.perplexity import perplexity_api
    from utils.logger import setup_logger
    from utils.error_handlers import (
        handle_400_error,
        handle_404_error,
        handle_500_error
    )
except ImportError as e:
    print(f"Error importing dependencies: {str(e)}")
    raise

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Setup logging
logger = setup_logger(
    'learning_framework',
    os.path.join('logs', 'app.log')
)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(perplexity_api, url_prefix='/api/perplexity')

# Register error handlers
app.register_error_handler(400, handle_400_error)
app.register_error_handler(404, handle_404_error)
app.register_error_handler(500, handle_500_error)

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
            
            # Sort by modification time (newest first)
            result_files.sort(key=lambda f: os.path.getmtime(os.path.join(results_dir, f)), reverse=True)
            result_id = result_files[0].split('.')[0]  # Remove .json extension
        
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
    
    # Handle direct form post (fallback for non-JavaScript clients)
    text = request.form.get('text')
    if not text:
        return render_template('results.html', error="No text provided")
    
    try:
        analyzer = PerplexityAnalyzer()
        results = await analyzer.analyze(text)
        
        # Save results
        result_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        results_dir = os.path.join(Config.RESULTS_DIR)
        os.makedirs(results_dir, exist_ok=True)
        
        with open(os.path.join(results_dir, f"{result_id}.json"), 'w') as f:
            json.dump(results, f)
            
        return render_template('results.html', results=results)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return render_template('results.html', error=str(e))

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