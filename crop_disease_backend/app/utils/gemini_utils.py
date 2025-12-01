# app/utils/gemini_api.py
import google.generativeai as genai
from typing import Dict, Any, Optional
import logging
import json
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiAPI:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            logger.warning("Gemini API key not configured")
            self.model = None
    
    def generate_advisory(
        self, 
        disease_name: str, 
        crop_type: str,
        confidence_score: float,
        kindwise_response: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive advisory for detected disease using Gemini API
        
        Args:
            disease_name: Name of the detected disease
            crop_type: Type of crop affected
            confidence_score: Confidence score of disease detection
            kindwise_response: Raw response from Kindwise API (optional)
        
        Returns:
            Dictionary containing advisory information
        """
        if not self.model:
            logger.warning("Gemini model not initialized, returning fallback advisory")
            return self._get_fallback_advisory(disease_name, crop_type)
        
        try:
            # Extract additional context from Kindwise response if available
            additional_context = ""
            if kindwise_response and 'raw_response' in kindwise_response:
                suggestions = kindwise_response['raw_response'].get('result', {}).get('disease', {}).get('suggestions', [])
                for suggestion in suggestions:
                    if suggestion.get('name', '').lower() == disease_name.lower():
                        details = suggestion.get('details', {})
                        if details.get('description'):
                            additional_context = f"\n\nAdditional context: {details.get('description')}"
                        break
            
            # Create detailed prompt for Gemini
            prompt = f"""You are an expert agricultural advisor. Generate a comprehensive disease advisory for farmers.

Disease Detected: {disease_name}
Crop Type: {crop_type}
Detection Confidence: {confidence_score * 100:.1f}%{additional_context}

Please provide a detailed advisory in the following JSON format:
{{
    "disease_name": "{disease_name}",
    "crop_type": "{crop_type}",
    "severity": "mild/moderate/severe",
    "description": "A clear, farmer-friendly description of the disease (2-3 sentences)",
    "symptoms": [
        "List 4-6 specific visible symptoms farmers should look for"
    ],
    "treatment_steps": [
        {{
            "step": 1,
            "description": "Detailed first treatment step",
            "materials_needed": ["List of materials needed"]
        }},
        {{
            "step": 2,
            "description": "Detailed second treatment step",
            "materials_needed": ["List of materials needed"]
        }},
        {{
            "step": 3,
            "description": "Detailed third treatment step",
            "materials_needed": ["List of materials needed"]
        }}
    ],
    "recommended_pesticide": "Specific pesticide name and application instructions",
    "recommended_fertilizer": "Specific fertilizer recommendations for recovery",
    "prevention_tips": [
        "List 5-7 practical prevention tips for future"
    ],
    "estimated_recovery_time": "Realistic timeframe for recovery with proper treatment",
    "organic_alternatives": "Brief description of organic treatment options",
    "when_to_seek_help": "Conditions when farmer should consult agricultural extension officer"
}}

Important guidelines:
1. Use simple, clear language that farmers can understand
2. Provide practical, actionable advice
3. Include specific product names where possible
4. Focus on cost-effective solutions
5. Consider organic alternatives
6. Be realistic about recovery timeframes
7. Ensure all advice is scientifically accurate

Return ONLY the JSON object, no additional text."""

            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            advisory_data = json.loads(response_text)
            
            # Validate and ensure all required fields are present
            advisory_data = self._validate_advisory_structure(advisory_data, disease_name, crop_type)
            
            logger.info(f"Successfully generated advisory for {disease_name} on {crop_type}")
            return advisory_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return self._get_fallback_advisory(disease_name, crop_type)
        except Exception as e:
            logger.error(f"Error generating advisory with Gemini: {e}")
            return self._get_fallback_advisory(disease_name, crop_type)
    
    def _validate_advisory_structure(
        self, 
        advisory: Dict[str, Any], 
        disease_name: str, 
        crop_type: str
    ) -> Dict[str, Any]:
        """Ensure advisory has all required fields with proper structure"""
        
        # Set defaults for missing fields
        validated = {
            "disease_name": advisory.get("disease_name", disease_name),
            "crop_type": advisory.get("crop_type", crop_type),
            "severity": advisory.get("severity", "moderate"),
            "description": advisory.get("description", f"Disease detected in {crop_type} crop."),
            "symptoms": advisory.get("symptoms", []),
            "treatment_steps": [],
            "recommended_pesticide": advisory.get("recommended_pesticide", "Consult local agricultural store"),
            "recommended_fertilizer": advisory.get("recommended_fertilizer", "Balanced NPK fertilizer"),
            "prevention_tips": advisory.get("prevention_tips", []),
            "estimated_recovery_time": advisory.get("estimated_recovery_time", "2-4 weeks"),
            "organic_alternatives": advisory.get("organic_alternatives", ""),
            "when_to_seek_help": advisory.get("when_to_seek_help", "")
        }
        
        # Validate treatment steps structure
        treatment_steps = advisory.get("treatment_steps", [])
        for i, step in enumerate(treatment_steps):
            if isinstance(step, dict):
                validated["treatment_steps"].append({
                    "step": step.get("step", i + 1),
                    "description": step.get("description", ""),
                    "materials_needed": step.get("materials_needed", [])
                })
        
        # Ensure at least one treatment step exists
        if not validated["treatment_steps"]:
            validated["treatment_steps"] = [
                {
                    "step": 1,
                    "description": "Remove and destroy affected plant parts",
                    "materials_needed": ["Pruning shears", "Disposal bags"]
                },
                {
                    "step": 2,
                    "description": "Apply recommended treatment",
                    "materials_needed": ["Appropriate pesticide/fungicide"]
                }
            ]
        
        return validated
    
    def _get_fallback_advisory(self, disease_name: str, crop_type: str) -> Dict[str, Any]:
        """Provide basic fallback advisory when Gemini API is unavailable"""
        return {
            "disease_name": disease_name,
            "crop_type": crop_type,
            "severity": "moderate",
            "description": f"{disease_name} has been detected in your {crop_type} crop. Immediate action is recommended to prevent spread.",
            "symptoms": [
                "Visible spots or discoloration on leaves",
                "Wilting or drooping of plant parts",
                "Unusual growth patterns",
                "Fruit or vegetable damage"
            ],
            "treatment_steps": [
                {
                    "step": 1,
                    "description": "Immediately isolate affected plants to prevent disease spread to healthy crops",
                    "materials_needed": ["Gloves", "Pruning tools"]
                },
                {
                    "step": 2,
                    "description": "Remove and safely destroy all infected plant material by burning or deep burial",
                    "materials_needed": ["Disposal bags", "Disinfectant"]
                },
                {
                    "step": 3,
                    "description": "Apply appropriate fungicide or pesticide as recommended by local agricultural experts",
                    "materials_needed": ["Sprayer", "Recommended pesticide"]
                },
                {
                    "step": 4,
                    "description": "Monitor remaining plants daily for signs of disease spread",
                    "materials_needed": ["Observation log"]
                }
            ],
            "recommended_pesticide": "Consult with local agricultural extension officer for region-specific recommendations",
            "recommended_fertilizer": "Balanced NPK fertilizer to support plant recovery",
            "prevention_tips": [
                "Practice crop rotation each growing season",
                "Ensure proper plant spacing for good air circulation",
                "Water at the base of plants, avoid wetting leaves",
                "Remove plant debris and weeds regularly",
                "Use disease-resistant varieties when available",
                "Maintain proper soil drainage",
                "Sterilize tools between uses"
            ],
            "estimated_recovery_time": "2-4 weeks with proper treatment and monitoring",
            "organic_alternatives": "Neem oil spray, copper-based organic fungicides, or biological control agents may be effective. Consult organic farming experts.",
            "when_to_seek_help": "If disease spreads rapidly despite treatment, affects large areas of the crop, or if you're unsure about treatment methods, immediately contact your local agricultural extension officer."
        }