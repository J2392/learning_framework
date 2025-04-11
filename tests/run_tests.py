#!/usr/bin/env python3
"""
Script to run all tests with options
"""
import os
import sys
import argparse
import unittest
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('run_tests')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_environment():
    """Setup test environment"""
    # Create necessary directories
    directories = ['logs', 'test_results', 'bench_results']
    for directory in directories:
        os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), directory), exist_ok=True)
    
    # Check for .env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_file):
        logger.warning(".env file not found! Creating a sample .env file")
        with open(env_file, 'w') as f:
            f.write("""# API Keys
PERPLEXITY_API_KEY=pplx-REPLACE_WITH_YOUR_KEY

# Application settings
DEBUG=True
PORT=5001
HOST=127.0.0.1
DEVELOPMENT_MODE=True

# Cache settings
CACHE_ENABLED=True
CACHE_TIMEOUT=3600

# Test settings
QUICK_TEST=True

# Model settings
PERPLEXITY_MODEL=sonar
""")
        logger.info(f"Created sample .env file at {env_file}, please update with your API key")

def install_dependencies():
    """Install required dependencies for tests"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        logger.error(f"Requirements file not found at {requirements_path}")
        return False
    
    try:
        logger.info("Installing test dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def run_unittest_tests(test_pattern, verbose=False, stop_on_fail=False):
    """Run tests with unittest"""
    test_dir = os.path.dirname(__file__)
    
    # Discover tests
    logger.info(f"Discovering tests matching pattern: {test_pattern}")
    
    loader = unittest.TestLoader()
    if test_pattern:
        # Add _test or test_ prefix if not specified
        if not test_pattern.startswith('test_') and not test_pattern.endswith('_test'):
            patterns = [f'test_{test_pattern}*', f'*_test_{test_pattern}*', f'*{test_pattern}*_test*']
        else:
            patterns = [f'*{test_pattern}*']
            
        suite = unittest.TestSuite()
        for pattern in patterns:
            matched_tests = loader.discover(test_dir, pattern=pattern)
            suite.addTests(matched_tests)
    else:
        suite = loader.discover(test_dir)
    
    # Create runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=stop_on_fail)
    
    # Run tests
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', f'test_results_{timestamp}.log')
    logger.info(f"Writing test results to: {log_file}")
    
    with open(log_file, 'w') as f:
        # Redirect stdout to file
        original_stdout = sys.stdout
        sys.stdout = f
        
        # Run tests
        result = runner.run(suite)
        
        # Restore stdout
        sys.stdout = original_stdout
    
    # Log summary
    logger.info(f"Tests completed: {result.testsRun} run, {len(result.errors)} errors, {len(result.failures)} failures")
    
    # Print detailed errors and failures
    if result.errors:
        logger.error("Errors:")
        for test, error in result.errors:
            logger.error(f"  {test}: {error.splitlines()[0]}")
    
    if result.failures:
        logger.error("Failures:")
        for test, failure in result.failures:
            logger.error(f"  {test}: {failure.splitlines()[0]}")
    
    return len(result.errors) == 0 and len(result.failures) == 0

def run_pytest_tests(test_pattern, verbose=False, stop_on_fail=False):
    """Run tests with pytest"""
    test_dir = os.path.dirname(__file__)
    
    # Build command
    cmd = [sys.executable, '-m', 'pytest']
    
    # Add options
    if verbose:
        cmd.append('-v')
    if stop_on_fail:
        cmd.append('-x')
    
    # Add pattern if specified
    if test_pattern:
        cmd.append(f'{test_dir}/*{test_pattern}*.py')
    else:
        cmd.append(test_dir)
    
    # Run pytest
    logger.info(f"Running pytest with command: {' '.join(cmd)}")
    return subprocess.call(cmd) == 0

def run_coverage(test_pattern=None, report_type='term'):
    """Run tests with coverage"""
    test_dir = os.path.dirname(__file__)
    
    # Build command
    cmd = [sys.executable, '-m', 'coverage', 'run', '--source=../']
    
    # Add test module or pattern
    if test_pattern:
        cmd.extend(['-m', f'pytest {test_dir}/*{test_pattern}*.py'])
    else:
        cmd.extend(['-m', f'pytest {test_dir}'])
    
    # Run coverage
    logger.info(f"Running coverage with command: {' '.join(cmd)}")
    result = subprocess.call(cmd) == 0
    
    # Generate report
    report_cmd = [sys.executable, '-m', 'coverage', 'report']
    if report_type == 'html':
        report_cmd = [sys.executable, '-m', 'coverage', 'html']
        logger.info("Generating HTML coverage report")
    else:
        logger.info("Generating coverage report")
    
    subprocess.call(report_cmd)
    return result

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run tests for learning framework')
    parser.add_argument('--pattern', '-p', help='Test pattern to match', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--stop-on-fail', '-x', action='store_true', help='Stop on first failure')
    parser.add_argument('--setup', '-s', action='store_true', help='Setup test environment')
    parser.add_argument('--install-deps', '-i', action='store_true', help='Install dependencies')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--pytest', action='store_true', help='Use pytest instead of unittest')
    parser.add_argument('--single', help='Run a single test, e.g. test_environment.TestEnvironment.test_api_key_exists')
    
    args = parser.parse_args()
    
    # Setup if requested
    if args.setup:
        setup_environment()
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            return 1
    
    # Run tests
    success = False
    if args.single:
        logger.info(f"Running single test: {args.single}")
        success = subprocess.call([sys.executable, '-m', 'unittest', args.single]) == 0
    elif args.coverage:
        report_type = 'html' if args.html_report else 'term'
        success = run_coverage(args.pattern, report_type)
    elif args.pytest:
        success = run_pytest_tests(args.pattern, args.verbose, args.stop_on_fail)
    else:
        success = run_unittest_tests(args.pattern, args.verbose, args.stop_on_fail)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 