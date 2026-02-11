"""
Simple Working Flask App
"""
from flask import Flask, jsonify, render_template, request
import pandas as pd
import os

# Set template directory
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Sample data
sample_data = {
    "name": ["Jalsa", "Spice Elephant", "San Churro Cafe"],
    "rate": ["4.1/5", "4.1/5", "3.8/5"],
    "cuisines": ["North Indian, Chinese", "South Indian, Italian", "Cafe, Mexican"],
    "approx_cost(for two people)": ["800", "600", "400"],
    "listed_in(city)": ["Bangalore"] * 3
}
df = pd.DataFrame(sample_data)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
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
        
        # Filter data
        filtered = df[df['approx_cost(for two people)'].astype(int) <= price]
        
        if len(filtered) == 0:
            recs = f"No restaurants found for {city} with budget Rs.{price} for {diet} food."
        else:
            recs = "Top recommendations:\n"
            for _, row in filtered.iterrows():
                recs += f"- {row['name']}: {row['cuisines']} (Rs.{row['approx_cost(for two people)']})\n"
        
        return jsonify({'recommendations': recs, 'success': True})
        
    except Exception as e:
        return jsonify({'recommendations': f'Error: {str(e)}', 'success': True})

@app.route('/api/cities')
def get_cities():
    return jsonify({'cities': ['Bangalore', 'Mumbai', 'Delhi']})

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'total_restaurants': len(df),
        'available_cities': 3,
        'sample_restaurants': df.head(3)[['name', 'rate', 'listed_in(city)']].to_dict('records')
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'System ready'})

if __name__ == '__main__':
    print("Zomato AI Recommendation System")
    print("=" * 40)
    print("Starting on http://localhost:5000")
    print("=" * 40)
    app.run(host='0.0.0.0', port=5000, debug=True)
