# kindwise_api.py
import requests
import base64
import json
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import io
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class KindwiseAPI:
    def __init__(self):
        self.api_key = settings.KINDWISE_API_KEY
        self.base_url = "https://crop.kindwise.com/api/v1"
        self.headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def encode_image(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        try:
            # Convert image to RGB if it's not
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image if too large (Kindwise has limits)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes and encode
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise
    
    def predict_disease(self, image: Image.Image, crop_type: Optional[str] = None) -> Tuple[str, float, Dict[str, Any]]:
        """Predict disease using Kindwise API or return mock data if API key not available"""
        
        # If no API key is provided, return mock data for testing
        if not self.api_key or self.api_key == "your-kindwise-api-key-here":
            logger.warning("Using mock data - Kindwise API key not configured")
            return self._get_mock_prediction(crop_type)
        
        try:
            # Encode image
            image_base64 = self.encode_image(image)
            
            # Prepare request payload
            payload = {
                "images": [image_base64],
                "similar_images": True
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/identification",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code not in (200, 201):
                logger.error(f"Kindwise API error: {response.status_code} - {response.text}")
                raise Exception(f"Kindwise API error: {response.status_code} - {response.text}")
            logger.info(f"Kindwise API success: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Parse the response
            if not result.get("result") or not result["result"].get("disease"):
                logger.warning("No disease results found, using mock data")
                return self._get_mock_prediction(crop_type)
            
            classification = result["result"]["disease"]
            
            # Get the best match
            if not classification.get("suggestions"):
                logger.warning("No disease suggestions found, using mock data")
                return self._get_mock_prediction(crop_type)
            
            suggestions = classification["suggestions"]
            best_match = max(suggestions, key=lambda s: s.get("probability", 0.0))
            disease_name = best_match.get("name", "Unknown Disease")
            confidence = best_match.get("probability", 0.0)
            
            # Extract additional information
            disease_info = {
                "disease_name": disease_name,
                "confidence": confidence,
                "similar_images": best_match.get("similar_images", []),
                "plant_details": result["result"].get("plant_details", {}),
                "raw_response": result
            }
            
            return disease_name, confidence, disease_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Kindwise API call: {e}")
            return self._get_mock_prediction(crop_type)
        except Exception as e:
            logger.error(f"Error in disease prediction: {e}")
            return self._get_mock_prediction(crop_type)
    
    def _get_mock_prediction(self, crop_type: Optional[str] = None) -> Tuple[str, float, Dict[str, Any]]:
        """Return mock prediction data for testing purposes"""
        import random
        
        # Mock diseases based on crop type
        crop_diseases = {
            "tomato": ["Early_Blight", "Late_Blight", "Bacterial_Spot", "Leaf_Mold"],
            "potato": ["Early_Blight", "Late_Blight", "Common_Scab", "Black_Scurf"],
            "pepper": ["Bacterial_Spot", "Anthracnose", "Phytophthora_Blight"],
            "corn": ["Northern_Corn_Leaf_Blight", "Gray_Leaf_Spot", "Common_Rust"],
            "wheat": ["Stripe_Rust", "Leaf_Rust", "Powdery_Mildew"],
            "rice": ["Blast", "Brown_Spot", "Bacterial_Leaf_Blight"],
        }
        
        # Default diseases if crop type not found
        default_diseases = ["Early_Blight", "Bacterial_Spot", "Leaf_Spot", "Powdery_Mildew"]
        
        diseases = crop_diseases.get(crop_type or "unknown", default_diseases)
        disease_name = random.choice(diseases)
        confidence = random.uniform(0.75, 0.95)  # High confidence for demo
        
        disease_info = {
            "disease_name": disease_name,
            "confidence": confidence,
            "similar_images": [],
            "plant_details": {
                "common_names": [crop_type] if crop_type else ["Unknown Plant"],
                "description": f"Mock analysis for {crop_type or 'unknown crop'}"
            },
            "mock_data": True,
            "note": "This is mock data for demonstration. Configure KINDWISE_API_KEY for real predictions."
        }
        
        return disease_name, confidence, disease_info
    
    def get_disease_details(self, disease_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific disease"""
        try:
            # This would typically call a separate Kindwise endpoint
            # For now, we'll return basic structure
            return {
                "name": disease_name,
                "description": f"Information about {disease_name}",
                "symptoms": [],
                "treatments": [],
                "prevention": []
            }
        except Exception as e:
            logger.error(f"Error getting disease details: {e}")
            return {}