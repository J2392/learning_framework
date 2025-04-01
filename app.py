"""
Main application entry point
"""

from flask import Flask, render_template, request, jsonify
from typing import Dict, Any
import os
import asyncio
import httpx
from asgiref.wsgi import WsgiToAsgi
from flask_cors import CORS

try:
    from config import Config
    from api.routes import api
    from utils.logger import setup_logger
    from utils.error_handlers import (
        handle_400_error,
        handle_404_error,
        handle_500_error
    )
    from analyzers.perplexity_analyzer import PerplexityAnalyzer
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

# Register error handlers
app.register_error_handler(400, handle_400_error)
app.register_error_handler(404, handle_404_error)
app.register_error_handler(500, handle_500_error)

@app.route('/', methods=['GET'])
async def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def analyze():
    """Handle analysis form submission"""
    text = request.form.get('text')
    if not text:
        return render_template('results.html', error="No text provided")
    
    try:
        analyzer = PerplexityAnalyzer()
        results = await analyzer.analyze(text)
        return render_template('results.html', results=results)
    except Exception as e:
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