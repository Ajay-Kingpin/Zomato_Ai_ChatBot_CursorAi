# Zomato AI Recommendation System

A modern AI-powered restaurant recommendation system built with Flask backend and Streamlit frontend, following **Zomato's Sushi Design System**.

## 🎨 Design System

This application follows **[Zomato's Sushi Design System](https://medium.com/zomato-technology/zomatos-new-sushi-design-system-d7f4f98664c5)** with:

- **� Primary Color**: Zomato Red (#E23744)
- **⚫ Dark Text**: Professional typography
- **🎯 Modern Cards**: Clean, rounded corners with shadows
- **📱 Responsive Design**: Mobile-first approach
- **✨ Smooth Animations**: Hover effects and transitions
- **🍽️ Restaurant Cards**: Zomato-style presentation

## �🚀 Streamlit Deployment

### Features
- 🍽️ AI-powered restaurant recommendations
- 🏙️ Multi-city support (Bangalore, Mumbai, Delhi, Pune, Hyderabad)
- 💰 Budget-based filtering
- 🥗 Dietary preference filtering (Veg/Non-veg)
- 📊 Real-time statistics
- 🎨 Zomato Sushi Design System UI
- 📱 Fully responsive design

### Design Highlights
- **Modern Header**: Gradient background with Zomato branding
- **Restaurant Cards**: Professional card layout with ratings and pricing
- **Interactive Elements**: Smooth hover effects and transitions
- **Statistics Dashboard**: Clean data visualization
- **Color System**: Consistent Zomato color palette

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run locally:**
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

3. **Deploy to Streamlit:**
   - Push to GitHub
   - Connect to Streamlit Cloud
   - Set environment variables

### Environment Variables
- `GOOGLE_STUDIO_API_KEY`: Your Google Studio API key

### Architecture
- **Backend**: Flask REST API (`working_app.py`)
- **Frontend**: Streamlit web interface (`streamlit_app.py`)
- **Design**: Zomato Sushi Design System
- **AI Integration**: Google Studio AI with fallback recommendations
- **Data**: Sample restaurant data with real API integration

### Deployment Steps

1. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Add Zomato AI Recommendation System with Sushi Design"
   git branch -M main
   git remote add origin https://github.com/yourusername/zomato-ai-recommendation.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [streamlit.io](https://streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select `streamlit_app.py` as main file
   - Set environment variables in deployment settings

3. **Backend Deployment (Optional)**
   - Deploy Flask app to Heroku/Railway/Render
   - Update `api_base_url` in `streamlit_app.py`

### 🌟 Live Demo
[Your Streamlit App URL]

### 🎨 UI Components

#### Header Section
- Zomato red gradient background
- Professional typography
- Responsive design

#### Restaurant Cards
- Rating badges with green background
- Price tags with orange background
- Location and cuisine information
- Popular dishes display

#### Statistics Dashboard
- Four-column responsive layout
- Hover effects on cards
- Clean data visualization

#### Footer
- Dark background with white text
- Professional branding
- Attribution to Zomato Design System

### 📱 Mobile Responsiveness
- Optimized for all screen sizes
- Touch-friendly interface
- Adaptive grid layouts
- Readable typography

### 🎯 Design Principles
- **Consistency**: Following Zomato's design language
- **Accessibility**: Clear contrast and readable fonts
- **Performance**: Optimized CSS and minimal JavaScript
- **User Experience**: Intuitive navigation and feedback

### Tech Stack
- **Backend**: Flask, Pandas, Requests
- **Frontend**: Streamlit, HTML/CSS (Zomato Design System)
- **AI**: Google Studio AI
- **Deployment**: Streamlit Cloud
- **Design**: Zomato Sushi Design System

### 📝 License
MIT License

### 🙏 Acknowledgments
- **Zomato**: For the amazing Sushi Design System
- **Streamlit**: For the powerful frontend framework
- **Google AI**: For the recommendation engine
