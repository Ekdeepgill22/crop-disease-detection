# advisory_controller.py
from typing import Optional, List, Dict, Any
from app.database import get_database, ensure_connection
from app.models.advisory import Advisory, Treatment, WeatherAdvice
from app.utils.weather_utils import get_weather_data, generate_weather_advice
from bson import ObjectId
import logging
from app.utils.mongo_utils import convert_objectids_to_str

logger = logging.getLogger(__name__)

class AdvisoryController:
    async def _get_db(self):
        """Get database instance with proper error handling"""
        try:
            await ensure_connection()
            return get_database()
        except Exception as e:
            logger.error(f"Database connection error in advisory controller: {e}")
            raise
    
    async def get_advisory_by_disease(self, disease_name: str, crop_type: str) -> Optional[Dict[str, Any]]:
        """Get advisory for specific disease and crop type"""
        try:
            db = await self._get_db()
            
            # Try exact match first
            advisory = await db.advisories.find_one({
                "disease_name": {"$regex": f"^{disease_name}$", "$options": "i"},
                "crop_type": {"$regex": f"^{crop_type}$", "$options": "i"}
            })
            
            if not advisory:
                # Try with just disease name if crop-specific not found
                advisory = await db.advisories.find_one({
                    "disease_name": {"$regex": f"^{disease_name}$", "$options": "i"}
                })
            
            if not advisory:
                logger.info(f"No existing advisory found for {disease_name} on {crop_type}")
                return None
            
            advisory = convert_objectids_to_str(advisory)
            
            # Filter out empty/blank treatment steps and prevention tips
            if 'treatment_steps' in advisory:
                advisory['treatment_steps'] = [
                    step for step in advisory['treatment_steps'] 
                    if step.get('description', '').strip()
                ]
            
            if 'prevention_tips' in advisory:
                advisory['prevention_tips'] = [
                    tip for tip in advisory['prevention_tips'] 
                    if tip and tip.strip()
                ]
            
            if not advisory.get('description') or not advisory['description'].strip():
                advisory['description'] = 'No description available.'
            
            logger.info(f"Found existing advisory for {disease_name} on {crop_type}")
            return advisory
            
        except Exception as e:
            logger.error(f"Error getting advisory: {e}")
            return None
    
    async def create_advisory(self, advisory_data: Dict[str, Any]) -> Optional[str]:
        """Create a new advisory in the database"""
        try:
            db = await self._get_db()
            
            # Check if advisory already exists
            existing = await db.advisories.find_one({
                "disease_name": advisory_data.get("disease_name"),
                "crop_type": advisory_data.get("crop_type")
            })
            
            if existing:
                logger.info(f"Advisory already exists for {advisory_data.get('disease_name')} on {advisory_data.get('crop_type')}")
                return str(existing["_id"])
            
            # Insert new advisory
            result = await db.advisories.insert_one(advisory_data)
            logger.info(f"Created new advisory with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating advisory: {e}")
            return None
    
    async def update_advisory(self, disease_name: str, crop_type: str, advisory_data: Dict[str, Any]) -> bool:
        """Update an existing advisory"""
        try:
            db = await self._get_db()
            
            result = await db.advisories.update_one(
                {
                    "disease_name": disease_name,
                    "crop_type": crop_type
                },
                {"$set": advisory_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated advisory for {disease_name} on {crop_type}")
                return True
            else:
                logger.warning(f"No advisory found to update for {disease_name} on {crop_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating advisory: {e}")
            return False
    
    async def get_all_advisories(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all advisories from database"""
        try:
            db = await self._get_db()
            cursor = db.advisories.find().limit(limit)
            
            advisories = []
            async for advisory in cursor:
                advisories.append(convert_objectids_to_str(advisory))
            
            return advisories
            
        except Exception as e:
            logger.error(f"Error getting all advisories: {e}")
            return []
    
    async def get_weather_advice(self, region: str) -> Optional[WeatherAdvice]:
        """Get weather-based agricultural advice"""
        weather_data = await get_weather_data(region)
        if weather_data:
            return generate_weather_advice(weather_data)
        return None
    
    async def initialize_default_advisories(self):
        """Initialize database with default advisories - now optional since we use Gemini"""
        try:
            db = await self._get_db()
            
            # Count existing advisories
            count = await db.advisories.count_documents({})
            
            if count > 0:
                logger.info(f"Database already has {count} advisories, skipping initialization")
                return
            
            # Only add a minimal default advisory as fallback
            default_advisory = {
                "disease_name": "General_Disease",
                "crop_type": "General",
                "severity": "moderate",
                "description": "General disease advisory - specific advisories will be generated using AI.",
                "symptoms": ["Various symptoms depending on disease type"],
                "treatment_steps": [
                    {
                        "step": 1, 
                        "description": "Consult with agricultural expert for specific treatment", 
                        "materials_needed": []
                    }
                ],
                "recommended_pesticide": "As recommended by expert",
                "recommended_fertilizer": "As recommended by expert",
                "prevention_tips": [
                    "Practice good agricultural hygiene",
                    "Monitor crops regularly"
                ],
                "estimated_recovery_time": "Varies by disease"
            }
            
            await db.advisories.insert_one(default_advisory)
            logger.info("Initialized minimal default advisory")
            
        except Exception as e:
            logger.error(f"Error initializing default advisories: {e}")