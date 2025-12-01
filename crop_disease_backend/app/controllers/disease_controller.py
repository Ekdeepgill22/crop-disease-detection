# disease_controller.py
from fastapi import HTTPException, UploadFile
from PIL import Image
from app.database import get_database, ensure_connection, is_database_connected
from app.models.user import UserInDB, PyObjectId
from app.models.diagnosis import DiagnosisCreate, DiagnosisInDB, PredictionResult
from app.utils.image_utils import save_image, preprocess_image
from app.utils.kindwise_api import KindwiseAPI
from app.utils.gemini_utils import GeminiAPI
from app.controllers.advisory_controller import AdvisoryController
from bson import ObjectId
from typing import Optional
import logging
import os
from app.utils.mongo_utils import convert_objectids_to_str

logger = logging.getLogger(__name__)

class DiseaseController:
    def __init__(self):
        self.advisory_controller = AdvisoryController()
        self.kindwise_api = KindwiseAPI()
        self.gemini_api = GeminiAPI()
    
    async def _get_db(self):
        """Get database instance with proper error handling and connection check"""
        try:
            if not is_database_connected():
                logger.warning("Database not connected, attempting to connect...")
                await ensure_connection()
            
            if not is_database_connected():
                logger.error("Failed to establish database connection")
                return None
                
            return get_database()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    async def predict_disease(self, file: UploadFile, crop_type: str, current_user: UserInDB) -> dict:
        """Predict disease from uploaded image and generate advisory using Gemini API"""
        try:
            logger.info(f"Starting disease prediction for user {current_user.email}")
            
            # Save uploaded image
            file_path, file_url = await save_image(file)
            logger.info(f"Image saved: {file_path}")
            
            # Load and preprocess image
            image = preprocess_image(file_path)
            logger.info("Image preprocessed successfully")
            
            # Predict disease using Kindwise API
            disease_name, confidence_score, disease_info = self.kindwise_api.predict_disease(image, crop_type)
            logger.info(f"Disease prediction completed: {disease_name} with confidence {confidence_score}")
            
            # Get database connection
            db = await self._get_db()
            if db is None:
                raise HTTPException(status_code=503, detail="Database service unavailable")
            
            # First, check if we already have an advisory for this disease-crop combination
            existing_advisory = await self.advisory_controller.get_advisory_by_disease(disease_name, crop_type)
            
            if existing_advisory:
                logger.info(f"Using existing advisory for {disease_name} on {crop_type}")
                advisory = existing_advisory if isinstance(existing_advisory, dict) else existing_advisory.dict()
            else:
                # Generate new advisory using Gemini API
                logger.info(f"Generating new advisory using Gemini API for {disease_name} on {crop_type}")
                advisory = self.gemini_api.generate_advisory(
                    disease_name=disease_name,
                    crop_type=crop_type,
                    confidence_score=confidence_score,
                    kindwise_response=disease_info
                )
                
                # Store the generated advisory in database for future use
                try:
                    advisory_with_timestamp = advisory.copy()
                    from datetime import datetime
                    advisory_with_timestamp['created_at'] = datetime.utcnow()
                    
                    await db.advisories.insert_one(advisory_with_timestamp)
                    logger.info(f"Stored new advisory for {disease_name} on {crop_type}")
                except Exception as e:
                    logger.warning(f"Failed to store advisory in database: {e}")
                    # Continue even if storage fails
            
            # Convert user ID to string
            user_id = str(current_user.id)
            
            # Create diagnosis record
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
            if db is None:
                logger.warning("Database not available, returning empty history")
                return []
            
            cursor = db.diagnoses.find(
                {"user_id": str(current_user.id)}
            ).sort("created_at", -1).limit(limit)
            
            diagnoses = []
            async for doc in cursor:
                diagnoses.append(convert_objectids_to_str(doc))
            
            return diagnoses
        except Exception as e:
            logger.error(f"Failed to fetch diagnosis history: {str(e)}")
            return []
    
    async def get_diagnosis_by_id(self, diagnosis_id: str, current_user: UserInDB):
        """Get specific diagnosis by ID"""
        try:
            db = await self._get_db()
            if db is None:
                raise HTTPException(status_code=503, detail="Database service unavailable")
            
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
            if db is None:
                raise HTTPException(status_code=503, detail="Database service unavailable")
            
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