# advisory_controller.py
from typing import Optional, List, Dict, Any
from app.database import get_database
from app.models.advisory import Advisory, Treatment, WeatherAdvice
from app.utils.weather_utils import get_weather_data, generate_weather_advice
from bson import ObjectId

class AdvisoryController:
    def __init__(self):
        self.db = get_database()
    
    async def get_advisory_by_disease(self, disease_name: str, crop_type: str) -> Optional[Advisory]:
        """Get advisory for specific disease and crop type"""
        advisory = await self.db.advisories.find_one({
            "disease_name": disease_name,
            "crop_type": crop_type
        })
        
        if not advisory:
            # Return default advisory if specific not found
            advisory = await self.get_default_advisory(disease_name)
        
        if advisory:
            return Advisory(**advisory)
        return None
    
    async def get_default_advisory(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """Get default advisory for disease (fallback)"""
        default_advisories = {
            "Bacterial_Spot": {
                "disease_name": "Bacterial_Spot",
                "crop_type": "General",
                "severity": "moderate",
                "description": "Bacterial spot causes small, dark spots on leaves and fruits.",
                "symptoms": ["Small dark spots on leaves", "Water-soaked lesions", "Yellowing around spots"],
                "treatment_steps": [
                    {"step": 1, "description": "Remove affected plant parts", "materials_needed": ["Pruning shears", "Disinfectant"]},
                    {"step": 2, "description": "Apply copper-based fungicide", "materials_needed": ["Copper fungicide", "Sprayer"]},
                    {"step": 3, "description": "Improve air circulation", "materials_needed": ["Pruning tools"]}
                ],
                "recommended_pesticide": "Copper hydroxide",
                "recommended_fertilizer": "Balanced NPK fertilizer",
                "prevention_tips": [
                    "Avoid overhead watering",
                    "Ensure proper plant spacing",
                    "Remove plant debris regularly"
                ],
                "estimated_recovery_time": "2-3 weeks"
            },
            "Early_Blight": {
                "disease_name": "Early_Blight",
                "crop_type": "General",
                "severity": "moderate",
                "description": "Early blight causes brown spots with concentric rings on leaves.",
                "symptoms": ["Brown spots with target-like rings", "Yellowing of lower leaves", "Defoliation"],
                "treatment_steps": [
                    {"step": 1, "description": "Remove infected leaves", "materials_needed": ["Gloves", "Pruning shears"]},
                    {"step": 2, "description": "Apply fungicide", "materials_needed": ["Chlorothalonil fungicide", "Sprayer"]},
                    {"step": 3, "description": "Mulch around plants", "materials_needed": ["Organic mulch"]}
                ],
                "recommended_pesticide": "Chlorothalonil",
                "recommended_fertilizer": "Potassium-rich fertilizer",
                "prevention_tips": [
                    "Practice crop rotation",
                    "Water at soil level",
                    "Maintain good air circulation"
                ],
                "estimated_recovery_time": "3-4 weeks"
            }
        }
        
        return default_advisories.get(disease_name)
    
    async def get_weather_advice(self, region: str) -> Optional[WeatherAdvice]:
        """Get weather-based agricultural advice"""
        weather_data = await get_weather_data(region)
        if weather_data:
            return generate_weather_advice(weather_data)
        return None
    
    async def initialize_default_advisories(self):
        """Initialize database with default advisories"""
        default_advisories = [
            {
                "disease_name": "Bacterial_Spot",
                "crop_type": "Tomato",
                "severity": "moderate",
                "description": "Bacterial spot is a common disease affecting tomato plants.",
                "symptoms": ["Small dark spots on leaves", "Water-soaked lesions", "Fruit spotting"],
                "treatment_steps": [
                    {"step": 1, "description": "Remove affected leaves immediately", "materials_needed": ["Sterile pruning shears", "Disinfectant"]},
                    {"step": 2, "description": "Apply copper-based bactericide", "materials_needed": ["Copper bactericide", "Sprayer"]},
                    {"step": 3, "description": "Improve ventilation around plants", "materials_needed": ["Stakes", "Ties"]}
                ],
                "recommended_pesticide": "Copper hydroxide spray",
                "recommended_fertilizer": "Low nitrogen, high potassium fertilizer",
                "prevention_tips": [
                    "Avoid overhead irrigation",
                    "Practice crop rotation",
                    "Use certified disease-free seeds",
                    "Maintain proper plant spacing"
                ],
                "estimated_recovery_time": "2-3 weeks with proper treatment"
            }
        ]
        
        for advisory in default_advisories:
            existing = await self.db.advisories.find_one({
                "disease_name": advisory["disease_name"],
                "crop_type": advisory["crop_type"]
            })
            if not existing:
                await self.db.advisories.insert_one(advisory)