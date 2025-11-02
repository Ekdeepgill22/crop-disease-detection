# disease_controller.py
from fastapi import HTTPException, UploadFile
from PIL import Image
from app.database import get_database, ensure_connection
from app.models.user import UserInDB, PyObjectId
from app.models.diagnosis import DiagnosisCreate, DiagnosisInDB, PredictionResult
from app.utils.image_utils import save_image, preprocess_image
from app.utils.kindwise_api import KindwiseAPI
from app.controllers.advisory_controller import AdvisoryController
from bson import ObjectId
from typing import Optional
import logging
import os
from app.utils.mongo_utils import convert_objectids_to_str

# Add crop-specific advisories
CROP_ADVISORIES = {
    "tomato": {
        "description": "General care and disease prevention for tomato crops.",
        "treatment_steps": [
            {"step": 1, "description": "Remove and destroy infected leaves."},
            {"step": 2, "description": "Apply recommended fungicide as per local guidelines."},
            {"step": 3, "description": "Ensure proper spacing and air circulation."}
        ],
        "prevention_tips": [
            "Rotate crops each season.",
            "Water at the base, not on leaves.",
            "Use disease-resistant varieties."
        ]
    },
    "potato": {
        "description": "General care and disease prevention for potato crops.",
        "treatment_steps": [
            {"step": 1, "description": "Remove and destroy infected plants."},
            {"step": 2, "description": "Apply appropriate fungicide."},
            {"step": 3, "description": "Avoid overhead irrigation."}
        ],
        "prevention_tips": [
            "Use certified disease-free seed potatoes.",
            "Practice crop rotation.",
            "Ensure good drainage."
        ]
    },
    "onion": {
        "description": "General care and disease prevention for onion crops.",
        "treatment_steps": [
            {"step": 1, "description": "Remove and destroy affected bulbs."},
            {"step": 2, "description": "Apply fungicide if necessary."},
            {"step": 3, "description": "Avoid waterlogging and ensure good air flow."}
        ],
        "prevention_tips": [
            "Use crop rotation.",
            "Plant in well-drained soil.",
            "Avoid overhead watering."
        ]
    },
    # ...add entries for all supported crops...
}

logger = logging.getLogger(__name__)

class DiseaseController:
    def __init__(self):
        self.advisory_controller = AdvisoryController()
        self.kindwise_api = KindwiseAPI()
    
    async def _get_db(self):
        """Get database instance with proper error handling and connection check"""
        try:
            await ensure_connection()
            return get_database()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Database connection is not initialized."
            )
    
    async def predict_disease(self, file: UploadFile, crop_type: str, current_user: UserInDB) -> dict:
        """Predict disease from uploaded image using Kindwise API"""
        try:
            logger.info(f"Starting disease prediction for user {current_user.email}")
            
            # Ensure database connection
            db = await self._get_db()
            logger.info("Database connection verified")
            
            # Save uploaded image
            file_path, file_url = await save_image(file)
            logger.info(f"Image saved: {file_path}")
            
            # Load and preprocess image
            image = preprocess_image(file_path)
            logger.info("Image preprocessed successfully")
            
            # Predict disease using Kindwise API
            disease_name, confidence_score, disease_info = self.kindwise_api.predict_disease(image, crop_type)
            logger.info(f"Disease prediction completed: {disease_name} with confidence {confidence_score}")
            
            # Get advisory for the predicted disease
            advisory = await self.advisory_controller.get_advisory_by_disease(disease_name, crop_type)
            logger.info("Advisory retrieved successfully")

            # If not found, extract from Kindwise API response and store in DB
            if not advisory:
                details = None
                if disease_info and 'raw_response' in disease_info:
                    suggestions = disease_info['raw_response'].get('result', {}).get('disease', {}).get('suggestions', [])
                    for s in suggestions:
                        if s.get('name', '').lower() == disease_name.lower():
                            details = s.get('details', {})
                            break
                if details:
                    advisory_dict = None
                    # Check if Kindwise details have any meaningful treatment/prevention info
                    treatment = details.get("treatment", {})
                    has_treatment = any([treatment.get("biological"), treatment.get("chemical"), treatment.get("prevention")])
                    has_prevention = bool(treatment.get("prevention"))
                    if not has_treatment and not has_prevention:
                        # Insert crop-specific default advisory if Kindwise has no info
                        crop_advisory = CROP_ADVISORIES.get(crop_type.lower())
                        if crop_advisory:
                            advisory_dict = {
                                "disease_name": disease_name,
                                "crop_type": crop_type,
                                "severity": "moderate",
                                "description": crop_advisory.get("description", "No description available."),
                                "symptoms": [],
                                "treatment_steps": crop_advisory.get("treatment_steps", []),
                                "recommended_pesticide": None,
                                "recommended_fertilizer": None,
                                "prevention_tips": crop_advisory.get("prevention_tips", []),
                                "estimated_recovery_time": "",
                            }
                            await db.advisories.insert_one(advisory_dict)
                            advisory = advisory_dict
                            logger.info(f"Inserted crop-specific default advisory for {disease_name}, {crop_type}")
                    elif has_treatment or has_prevention:
                        treatment_steps = []
                        step_num = 1
                        if treatment.get("biological"):
                            treatment_steps.append({"step": step_num, "description": treatment["biological"]})
                            step_num += 1
                        if treatment.get("chemical"):
                            treatment_steps.append({"step": step_num, "description": treatment["chemical"]})
                            step_num += 1
                        if treatment.get("prevention"):
                            treatment_steps.append({"step": step_num, "description": treatment["prevention"]})

                        prevention_tips = []
                        if treatment.get("prevention"):
                            prevention_tips.append(treatment["prevention"])

                        advisory_dict = {
                            "disease_name": disease_name,
                            "crop_type": crop_type,
                            "severity": details.get("severity") or "moderate",
                            "description": details.get("description", "No description available."),
                            "symptoms": [details.get("symptoms", "")],
                            "treatment_steps": treatment_steps,
                            "recommended_pesticide": None,
                            "recommended_fertilizer": None,
                            "prevention_tips": prevention_tips,
                            "estimated_recovery_time": "",
                        }
                        await db.advisories.insert_one(advisory_dict)
                        advisory = advisory_dict
                        logger.info(f"Inserted Kindwise advisory for {disease_name}, {crop_type}")
                    if not advisory_dict:
                        # Fallback advisory if not found in Kindwise details
                        crop_advisory = CROP_ADVISORIES.get(crop_type.lower())
                        if crop_advisory:
                            advisory = crop_advisory
                        else:
                            advisory = {
                                "description": "No specific treatment found for this crop. Please consult an expert or local agricultural extension officer.",
                                "treatment_steps": [
                                    {"step": 1, "description": "Isolate affected plants to prevent spread."},
                                    {"step": 2, "description": "Remove and safely dispose of diseased plant material."},
                                    {"step": 3, "description": "Maintain good field hygiene and monitor regularly."}
                                ],
                                "prevention_tips": [
                                    "Practice crop rotation and use disease-free seeds.",
                                    "Ensure proper spacing and avoid overhead irrigation.",
                                    "Consult local experts for further guidance."
                                ]
                            }
            
            # Convert user ID to string
            user_id = str(current_user.id)
            
            if not isinstance(advisory, dict) and advisory is not None:
                advisory = advisory.dict()
            diagnosis_in_db = DiagnosisInDB(
                user_id=user_id,
                crop_type=crop_type,
                image_path=file_path,
                image_url=file_url,
                predicted_disease=disease_name,
                confidence_score=confidence_score,
                advisory=advisory,
                api_response=disease_info
            )
            
            # Save to database
            result = await db.diagnoses.insert_one(diagnosis_in_db.dict(by_alias=True))
            logger.info(f"Diagnosis saved to database with ID: {result.inserted_id}")
            
            # Fetch the inserted document and return with ObjectIds as strings
            diagnosis = await db.diagnoses.find_one({"_id": result.inserted_id})
            if not diagnosis:
                raise HTTPException(status_code=500, detail="Failed to fetch saved diagnosis.")
            diagnosis = convert_objectids_to_str(diagnosis)
            # Map to frontend-expected keys for immediate display
            return {
                "disease_name": diagnosis.get("predicted_disease", "N/A"),
                "confidence_score": diagnosis.get("confidence_score", 0.0),
                "crop_type": diagnosis.get("crop_type", ""),
                "advisory": diagnosis.get("advisory", {}),
                "api_response": diagnosis.get("api_response", {}),
                "image_url": diagnosis.get("image_url", ""),
                "created_at": diagnosis.get("created_at", ""),
                "_id": diagnosis.get("_id", "")
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    
    async def get_diagnosis_history(self, current_user: UserInDB, limit: int = 10):
        """Get user's diagnosis history"""
        try:
            db = await self._get_db()
            cursor = db.diagnoses.find(
                {"user_id": str(current_user.id)}
            ).sort("created_at", -1).limit(limit)
            
            diagnoses = []
            async for doc in cursor:
                diagnoses.append(convert_objectids_to_str(doc))
            
            return diagnoses
        except Exception as e:
            logger.error(f"Failed to fetch diagnosis history: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch diagnosis history: {str(e)}")
    
    async def get_diagnosis_by_id(self, diagnosis_id: str, current_user: UserInDB):
        """Get specific diagnosis by ID"""
        try:
            db = await self._get_db()
            diagnosis = await db.diagnoses.find_one({
                "_id": ObjectId(diagnosis_id),
                "user_id": str(current_user.id)
            })
            
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            return convert_objectids_to_str(diagnosis)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch diagnosis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch diagnosis: {str(e)}")
    
    async def delete_diagnosis(self, diagnosis_id: str, current_user: UserInDB):
        """Delete a diagnosis and its image file"""
        try:
            db = await self._get_db()
            diagnosis = await db.diagnoses.find_one({
                "_id": ObjectId(diagnosis_id),
                "user_id": str(current_user.id)
            })
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            # Delete the image file if it exists
            image_path = diagnosis.get("image_path")
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            # Delete the diagnosis from the database
            await db.diagnoses.delete_one({"_id": ObjectId(diagnosis_id)})
            return {"detail": "Diagnosis and image deleted successfully."}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete diagnosis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete diagnosis: {str(e)}")