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
        self.base_url = "https://api.kindwise.com/v1"
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
        """Predict disease using Kindwise API"""
        try:
            # Encode image
            image_base64 = self.encode_image(image)
            
            # Prepare request payload
            payload = {
                "images": [image_base64],
                "modifiers": ["health_all", "disease_similar_images"],
                "plant_details": ["common_names", "url", "wiki_description", "taxonomy"]
            }
            
            # Add crop type if provided
            if crop_type:
                payload["plant_details"].append("common_names")
                payload["modifiers"].append("crop_specific")
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/identification",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Kindwise API error: {response.status_code} - {response.text}")
                raise Exception(f"API request failed: {response.status_code}")
            
            result = response.json()
            
            # Parse the response
            if not result.get("result") or not result["result"].get("classification"):
                raise Exception("No classification results found")
            
            classification = result["result"]["classification"]
            
            # Get the best match
            if not classification.get("suggestions"):
                raise Exception("No disease suggestions found")
            
            best_match = classification["suggestions"][0]
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
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in disease prediction: {e}")
            raise
    
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