"""
Phase 5 - Main Application
Integrates all phases to provide complete restaurant recommendation functionality.
"""

import sys
from pathlib import Path
from typing import Optional

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

import pandas as pd
from phase1_DataLoading.data_loader import ZomatoDataLoader
from phase2_UserInput.user_input import UserInput, UserInputHandler
from phase3_Integration.integrator import Integrator
from phase4_LLMRecommendation.recommender import Recommender
from phase5_DisplayCLI.display import RecommendationDisplay


class ZomatoRecommendationApp:
    """Main application integrating all phases of the recommendation system."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize the complete recommendation system.
        
        Args:
            data_path: Optional path to local CSV data file
        """
        # Initialize all phases
        self.data_loader = ZomatoDataLoader(data_path=data_path)
        self.user_input_handler = UserInputHandler()
        self.integrator = Integrator()
        self.recommender = Recommender()
        self.display = RecommendationDisplay()
        
        # Load data
        self._load_data()
    
    def _load_data(self):
        """Load restaurant data."""
        try:
            self.data = self.data_loader.load(prefer_local=True)
            print(f"Loaded {len(self.data)} restaurants successfully!")
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Falling back to Hugging Face dataset...")
            try:
                self.data = self.data_loader.load_from_huggingface()
                print(f"Loaded {len(self.data)} restaurants from Hugging Face!")
            except Exception as e2:
                print(f"Failed to load data from all sources: {e2}")
                raise
    
    def get_recommendations(self, city: str, price: int, diet: str) -> str:
        """
        Get complete restaurant recommendations.
        
        Args:
            city: City/area name
            price: Budget for two people
            diet: Dietary preference ('veg' or 'non-veg')
            
        Returns:
            Formatted recommendation string
        """
        try:
            # Phase 2: Process user input
            user_input = self.user_input_handler.parse(city, price, diet)
            
            # Phase 3: Filter restaurants based on user preferences
            context = self.integrator.prepare_context(self.data, user_input)
            
            # Phase 4: Get AI recommendations
            result = self.recommender.get_recommendations(context)
            
            # Phase 5: Format and display recommendations
            formatted_output = self.display.format_recommendations(result, user_input)
            
            # Add statistics
            stats = self.display.display_summary_stats(
                total_restaurants=len(self.data),
                filtered_restaurants=context.total_matches,
                recommendations_count=len(result.recommendations)
            )
            
            return f"{formatted_output}\n{stats}"
            
        except Exception as e:
            return f"""
╔══════════════════════════════════════════════════════════════╗
║                       ERROR OCCURRED                        ║
╚══════════════════════════════════════════════════════════════╝

Sorry, we encountered an error while processing your request:

Error: {str(e)}

Suggestions:
• Check if all input values are correct
• Ensure the city name is spelled correctly
• Verify your budget is a reasonable number
• Make sure dietary preference is 'veg' or 'non-veg'

Please try again with different inputs!
"""
    
    def get_available_cities(self) -> list[str]:
        """Get list of available cities from the dataset."""
        return self.data_loader.get_unique_cities()
    
    def get_dataset_info(self) -> dict:
        """Get information about the loaded dataset."""
        return {
            "total_restaurants": len(self.data),
            "available_cities": len(self.get_available_cities()),
            "columns": list(self.data.columns),
            "sample_restaurants": self.data.head(3)[['name', 'listed_in(city)', 'rate']].to_dict('records')
        }


def main():
    """Main function to run the application."""
    print("Zomato AI Restaurant Recommendation System")
    print("=" * 60)
    
    try:
        # Initialize the app
        app = ZomatoRecommendationApp()
        
        # Show dataset info
        info = app.get_dataset_info()
        print(f"Dataset Info:")
        print(f"   Total restaurants: {info['total_restaurants']:,}")
        print(f"   Available cities: {info['available_cities']}")
        print(f"   Sample restaurants: {[r['name'] for r in info['sample_restaurants']]}")
        print()
        
        # Get user input
        print("Enter your preferences:")
        city = input("City/Area: ").strip()
        if not city:
            print("City cannot be empty!")
            return
        
        try:
            price = int(input("Budget for two people (Rs.): ").strip())
            if price <= 0:
                print("Budget must be positive!")
                return
        except ValueError:
            print("Please enter a valid number for budget!")
            return
        
        diet = input("Diet preference (veg/non-veg): ").strip().lower()
        if diet not in ['veg', 'non-veg']:
            print("Diet must be 'veg' or 'non-veg'!")
            return
        
        print("\nProcessing your request...")
        
        # Get recommendations
        recommendations = app.get_recommendations(city, price, diet)
        
        print("\n" + recommendations)
        
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
