"""
Phase 6 - Web Frontend
Flask web application for the Zomato AI Recommendation System.
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables with error handling
try:
    load_dotenv(project_root / "phase4_LLMRecommendation" / ".env")
except Exception:
    import os
    os.environ["GOOGLE_STUDIO_API_KEY"] = "AIzaSyArJ-GUufO3vFaOYjzONmfwCu5vpcQU3r8"

from phase5_DisplayCLI.main import ZomatoRecommendationApp


app = Flask(__name__)
recommendation_app = None


def initialize_app():
    """Initialize the recommendation system."""
    global recommendation_app
    try:
        recommendation_app = ZomatoRecommendationApp()
        return True, "System initialized successfully"
    except Exception as e:
        return False, f"Failed to initialize: {str(e)}"


@app.route('/')
def index():
    """Main page with the recommendation form."""
    return render_template('index.html')


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get restaurant recommendations."""
    try:
        data = request.get_json()
        
        # Validate input
        city = data.get('city', '').strip()
        price = data.get('price', '')
        diet = data.get('diet', '').strip()
        
        if not city:
            return jsonify({'error': 'City is required'}), 400
        
        try:
            price = int(price)
            if price <= 0:
                return jsonify({'error': 'Budget must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid budget amount'}), 400
        
        if diet not in ['veg', 'non-veg']:
            return jsonify({'error': 'Diet must be veg or non-veg'}), 400
        
        # Get recommendations
        recommendations = recommendation_app.get_recommendations(city, price, diet)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': f'System error: {str(e)}'}), 500


@app.route('/api/cities')
def get_cities():
    """Get available cities from the dataset."""
    try:
        cities = recommendation_app.get_available_cities()
        return jsonify({'cities': cities})
    except Exception as e:
        return jsonify({'error': f'Failed to load cities: {str(e)}'}), 500


@app.route('/api/stats')
def get_stats():
    """Get dataset statistics."""
    try:
        stats = recommendation_app.get_dataset_info()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Failed to load stats: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    if recommendation_app is None:
        return jsonify({'status': 'error', 'message': 'System not initialized'}), 503
    
    return jsonify({'status': 'healthy', 'message': 'System ready'})


if __name__ == '__main__':
    # Initialize the recommendation system
    success, message = initialize_app()
    print("Zomato AI Recommendation System - Web Frontend")
    print("=" * 50)
    print("System initialized successfully")
    print("Starting web server on http://localhost:5000")
    print("API endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /api/cities - Available cities")
    print("   GET  /api/stats - Dataset statistics")
    print("   POST /api/recommendations - Get recommendations")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
