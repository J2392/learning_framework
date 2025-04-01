# Learning Framework with Perplexity API

An advanced learning tool that applies 7 thinking methods to any text, enhanced with AI capabilities through Perplexity API.

## Features

- **Text Analysis**: Extracts key concepts, entities, and themes using spaCy NLP
- **AI Enhancement**: Uses Perplexity API for deeper analysis and higher-quality content generation
- **7 Thinking Methods**:
  - Socratic Questioning
  - Multi-level Explanations
  - Practice Questions
  - Summarizing and Comparing
  - Key Terms Categorization
  - Bloom's Taxonomy Challenges
  - Analogies and Real-life Examples

## Installation

1. Clone this repository:

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the environment variables in `.env` file:
```bash
# Replace default values with real ones
SECRET_KEY=your-secret-key-here
PERPLEXITY_API_KEY=pplx-your-actual-key-here
```

## Troubleshooting

### API 404 Not Found Error
If you get a 404 error when calling the API, check:
1. Verify your API key in the `.env` file
2. Make sure the API key has the correct format (starts with `pplx-`)
3. Check your network connection

### Port Already in Use Error
If you encounter "address already in use" error:
```bash
# Find and stop the process using port 5000
lsof -ti :5000 | xargs kill -9
```

## API Endpoints

- `GET /` - Home page
- `POST /api/analyze` - Analyze text
- `POST /api/perplexity/analyze` - Analyze text using Perplexity API

## Supported Models

Perplexity API supports the following models:

### Search Models:
- sonar-pro (recommended for complex queries)
- sonar (lightweight, cost-effective)

### Research Models:
- sonar-deep-research (comprehensive research)

### Reasoning Models:
- sonar-reasoning-pro (advanced reasoning with CoT)
- sonar-reasoning (real-time reasoning)

### Offline Models:
- r1-1776 (uncensored, unbiased information)

In our testing, the following models have been confirmed to work:
- sonar-pro
- sonar

## API Key Setup

This application can run in two modes:

### 1. Development Mode (No API Key Required)

By default, the application runs in development mode with a mock API that doesn't require an actual Perplexity API key. This is perfect for testing and development.

### 2. Production Mode (API Key Required)

To use the real Perplexity API:

1. Create an account at [Perplexity AI](https://www.perplexity.ai)
2. Navigate to [API Settings](https://www.perplexity.ai/settings/api)
3. Generate a new API key
4. Add your API key to `.env` file:
   ```
   PERPLEXITY_API_KEY=pplx-your_actual_key_here
   ```
5. Set `DEVELOPMENT_MODE = False` in `config.py`

### API Authentication Errors

If you see a 401 Unauthorized error:
1. Your API key is not valid or has expired
2. You may have copied the key incorrectly - ensure no extra spaces
3. Generate a new key and update your .env file

## API Key Setup for Perplexity Pro Users

If you have a Perplexity Pro account, you can use the full API capabilities:

1. Navigate to [API Settings](https://www.perplexity.ai/settings/api) in your Perplexity account
2. Generate a new API key
3. Add your API key to `.env` file:
   ```
   PERPLEXITY_API_KEY=pplx-your_actual_key_here
   ```
4. Set `DEVELOPMENT_MODE = False` in `config.py`
5. Verify your key works by running: `python check_api_key.py`

### Recommended Models for Pro Users

- `sonar-medium-online` - Best balance of quality and speed
- `sonar-small-online` - Faster for simpler tasks
- `claude-3-opus-20240229` - High quality for complex content
- `llama-3-70b-8192` - Alternative high-quality model