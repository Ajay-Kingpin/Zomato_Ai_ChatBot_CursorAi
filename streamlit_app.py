import streamlit as st
import pandas as pd
import requests
import json
from typing import List, Dict

# Page configuration with Zomato branding
st.set_page_config(
    page_title="Zomato AI Recommendation System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Zomato Sushi Design System CSS
st.markdown("""
<style>
    /* Zomato Design System Colors */
    :root {
        --zomato-red: #E23744;
        --zomato-dark: #1C1C1C;
        --zomato-gray: #696969;
        --zomato-light-gray: #F8F8F8;
        --zomato-white: #FFFFFF;
        --zomato-green: #48C479;
        --zomato-orange: #FF6B35;
        --zomato-blue: #2E86AB;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--zomato-light-gray);
    }

    /* Header Styles */
    .zomato-header {
        background: linear-gradient(135deg, var(--zomato-red) 0%, #C41E3A 100%);
        color: var(--zomato-white);
        padding: 3rem 2rem;
        border-radius: 0 0 2rem 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(226, 55, 68, 0.3);
        margin-bottom: 2rem;
    }

    .zomato-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .zomato-header p {
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 400;
    }

    /* Card Styles */
    .zomato-card {
        background: var(--zomato-white);
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        height: 100%;
    }

    .zomato-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    /* Recommendation Card */
    .recommendation-card {
        background: var(--zomato-white);
        border-radius: 1rem;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 4px solid var(--zomato-red);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }

    .recommendation-card h4 {
        color: var(--zomato-dark);
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Stats Card */
    .stats-card {
        background: var(--zomato-white);
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }

    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }

    .stats-number {
        font-size: 3rem;
        font-weight: 700;
        color: var(--zomato-red);
        margin-bottom: 0.5rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stats-label {
        color: var(--zomato-gray);
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* Restaurant Grid */
    .restaurant-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }

    .restaurant-card {
        background: var(--zomato-white);
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .restaurant-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .restaurant-header {
        background: linear-gradient(135deg, var(--zomato-red) 0%, #C41E3A 100%);
        color: var(--zomato-white);
        padding: 1.5rem;
        font-weight: 600;
        font-size: 1.3rem;
    }

    .restaurant-body {
        padding: 1.5rem;
    }

    .rating-badge {
        background: var(--zomato-green);
        color: var(--zomato-white);
        padding: 0.3rem 0.8rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .price-tag {
        background: var(--zomato-orange);
        color: var(--zomato-white);
        padding: 0.3rem 0.8rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    /* Footer */
    .zomato-footer {
        background: var(--zomato-dark);
        color: var(--zomato-white);
        padding: 2rem;
        text-align: center;
        border-radius: 1rem 1rem 0 0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sample data (fallback if API fails)
SAMPLE_RESTAURANTS = [
    {
        "name": "Jalsa",
        "rate": "4.1/5",
        "cuisines": "North Indian, Chinese",
        "approx_cost(for two people)": "800",
        "listed_in(city)": "Bangalore",
        "dish_liked": "Pasta, Pizza, Burger",
        "location": "Banashankari"
    },
    {
        "name": "Spice Elephant",
        "rate": "4.1/5",
        "cuisines": "South Indian, Italian",
        "approx_cost(for two people)": "600",
        "listed_in(city)": "Bangalore",
        "dish_liked": "Biryani, Kebab",
        "location": "Indiranagar"
    },
    {
        "name": "San Churro Cafe",
        "rate": "3.8/5",
        "cuisines": "Cafe, Mexican",
        "approx_cost(for two people)": "400",
        "listed_in(city)": "Bangalore",
        "dish_liked": "Churros, Coffee",
        "location": "Koramangala"
    },
    {
        "name": "Grand Village",
        "rate": "4.2/5",
        "cuisines": "North Indian, Chinese",
        "approx_cost(for two people)": "500",
        "listed_in(city)": "Bangalore",
        "dish_liked": "North Indian, Chinese",
        "location": "HSR Layout"
    },
    {
        "name": "Empire Restaurant",
        "rate": "4.5/5",
        "cuisines": "Mughlai, North Indian",
        "approx_cost(for two people)": "900",
        "listed_in(city)": "Bangalore",
        "dish_liked": "Mughlai, Tandoori",
        "location": "Whitefield"
    }
]

class ZomatoRecommendationApp:
    def __init__(self):
        self.api_base_url = "https://your-app-url.herokuapp.com"  # Update with your deployed URL
        
    def get_cities(self) -> List[str]:
        """Get available cities from API or return sample data"""
        try:
            response = requests.get(f"{self.api_base_url}/api/cities", timeout=5)
            if response.status_code == 200:
                return response.json().get('cities', ['Bangalore', 'Mumbai', 'Delhi'])
        except:
            pass
        return ['Bangalore', 'Mumbai', 'Delhi']
    
    def get_stats(self) -> Dict:
        """Get system statistics from API or return sample data"""
        try:
            response = requests.get(f"{self.api_base_url}/api/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {
            'total_restaurants': len(SAMPLE_RESTAURANTS),
            'available_cities': 3,
            'sample_restaurants': SAMPLE_RESTAURANTS
        }
    
    def get_recommendations(self, city: str, price: int, diet: str) -> str:
        """Get recommendations from API or generate fallback recommendations"""
        try:
            response = requests.post(
                f"{self.api_base_url}/api/recommendations",
                json={"city": city, "price": price, "diet": diet},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('recommendations', 'No recommendations available')
        except:
            pass
        
        # Fallback recommendations
        filtered = [r for r in SAMPLE_RESTAURANTS if int(r["approx_cost(for two people)"]) <= price]
        if not filtered:
            return f"No restaurants found for {city} with budget Rs.{price} for {diet} food."
        
        recommendations = f"Top recommendations for {city} (Budget: Rs.{price}, Diet: {diet}):\n\n"
        for i, restaurant in enumerate(filtered[:3], 1):
            recommendations += f"{i}. **{restaurant['name']}**\n"
            recommendations += f"   - Cuisines: {restaurant['cuisines']}\n"
            recommendations += f"   - Rating: {restaurant['rate']}\n"
            recommendations += f"   - Cost: Rs.{restaurant['approx_cost(for two people)']} for two\n\n"
        
        return recommendations

# Initialize app
app = ZomatoRecommendationApp()

# Header with Zomato branding
st.markdown("""
<div class="zomato-header">
    <h1>🍽️ Zomato AI Recommendation System</h1>
    <p>Discover amazing restaurants with AI-powered recommendations</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with Zomato styling
st.markdown('<div class="sidebar-title">🔍 Search Preferences</div>', unsafe_allow_html=True)

# City selection
cities = app.get_cities()
selected_city = st.selectbox(
    "🏙️ Select City",
    options=cities,
    index=0 if cities else None,
    key="city_select"
)

# Budget input
budget = st.number_input(
    "💰 Budget for Two People (Rs.)",
    min_value=100,
    max_value=5000,
    value=800,
    step=50,
    key="budget_input"
)

# Dietary preference
diet_preference = st.selectbox(
    "🥗 Dietary Preference",
    options=["veg", "non-veg"],
    index=0,
    key="diet_select"
)

# Get recommendations button
if st.button("🔍 Get Recommendations", type="primary", use_container_width=True):
    with st.spinner("🤖 AI is analyzing restaurants..."):
        recommendations = app.get_recommendations(selected_city, budget, diet_preference)
        
        st.markdown("### 🎯 Your Personalized Recommendations")
        st.markdown(f"""
        <div class="recommendation-card">
            <div style="white-space: pre-line; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
{recommendations}
            </div>
        </div>
        """, unsafe_allow_html=True)

# System Statistics
st.markdown("---")
st.markdown("### 📊 System Statistics")

stats = app.get_stats()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['total_restaurants']}</div>
        <div class="stats-label">Total Restaurants</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats['available_cities']}</div>
        <div class="stats-label">Available Cities</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">🤖</div>
        <div class="stats-label">AI Powered</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">⚡</div>
        <div class="stats-label">Real-time</div>
    </div>
    """, unsafe_allow_html=True)

# Sample restaurants display with Zomato-style cards
if 'sample_restaurants' in stats:
    st.markdown("### 🍽️ Featured Restaurants")
    
    # Create restaurant grid
    cols = st.columns(3)
    for i, restaurant in enumerate(stats['sample_restaurants'][:3]):
        with cols[i]:
            st.markdown(f"""
            <div class="restaurant-card">
                <div class="restaurant-header">
                    {restaurant['name']}
                </div>
                <div class="restaurant-body">
                    <span class="rating-badge">⭐ {restaurant['rate']}</span>
                    <span class="price-tag">💰 Rs.{restaurant['approx_cost(for two people)']}</span>
                    <p><strong>🍴 Cuisines:</strong> {restaurant['cuisines']}</p>
                    <p><strong>📍 Location:</strong> {restaurant['location']}</p>
                    <p><strong>🥘 Popular:</strong> {restaurant['dish_liked']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer with Zomato branding
st.markdown("""
<div class="zomato-footer">
    <h3>🍽️ Zomato AI Recommendation System</h3>
    <p>Powered by AI | Built with ❤️ using Streamlit</p>
    <p><small>© 2024 Zomato AI Recommendation System | Inspired by Zomato's Sushi Design System</small></p>
</div>
""", unsafe_allow_html=True)
