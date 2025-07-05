# disease_controller.py
from fastapi import HTTPException, UploadFile
from PIL import Image
from app.database import get_database, ensure_connection, is_database_connected
from app.models.user import UserInDB, PyObjectId
from app.models.diagnosis import DiagnosisCreate, DiagnosisInDB, PredictionResult
from app.utils.image_utils import save_image, preprocess_image
from app.utils.kindwise_api import KindwiseAPI
from app.controllers.advisory_controller import AdvisoryController
from bson import ObjectId
from typing import Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DiseaseController:
    def __init__(self):
        self.advisory_controller = AdvisoryController()
        self.kindwise_api = KindwiseAPI()
    
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
    
    async def predict_disease(self, file: UploadFile, crop_type: str, current_user: UserInDB) -> PredictionResult:
        """Predict disease from uploaded image using Kindwise API"""
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
            
            # Get advisory for the predicted disease
            advisory = await self.advisory_controller.get_advisory_by_disease(disease_name, crop_type)
            logger.info("Advisory retrieved successfully")
            
            # Try to save to database (optional - won't fail if DB is down)
            try:
                db = await self._get_db()
                if db is not None:
                    # Convert user ID to PyObjectId
                    user_id = PyObjectId(current_user.id)
                    
                    diagnosis_in_db = DiagnosisInDB(
                        user_id=user_id,
                        crop_type=crop_type,
                        image_path=file_path,
                        image_url=file_url,
                        predicted_disease=disease_name,
                        confidence_score=confidence_score,
                        advisory=advisory.dict() if advisory else None,
                        api_response=disease_info
                    )
                    
                    # Save to database
                    result = await db.diagnoses.insert_one(diagnosis_in_db.dict(by_alias=True))
                    logger.info(f"Diagnosis saved to database with ID: {result.inserted_id}")
                else:
                    logger.warning("Database not available, skipping diagnosis save")
            except Exception as db_error:
                logger.warning(f"Failed to save diagnosis to database: {db_error}")
                # Continue without database - don't fail the prediction
            
            return PredictionResult(
                disease_name=disease_name,
                confidence_score=confidence_score,
                crop_type=crop_type,
                advisory=advisory.dict() if advisory else {},
                api_response=disease_info
            )
            
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
                {"user_id": ObjectId(current_user.id)}
            ).sort("created_at", -1).limit(limit)
            
            diagnoses = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                diagnoses.append(doc)
            
            return diagnoses
        except Exception as e:
            logger.error(f"Failed to fetch diagnosis history: {str(e)}")
            # Return empty list instead of failing
            return []
    
    async def get_diagnosis_by_id(self, diagnosis_id: str, current_user: UserInDB):
        """Get specific diagnosis by ID"""
        try:
            db = await self._get_db()
            if db is None:
                raise HTTPException(status_code=503, detail="Database service unavailable")
            
            diagnosis = await db.diagnoses.find_one({
                "_id": ObjectId(diagnosis_id),
                "user_id": ObjectId(current_user.id)
            })
            
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            diagnosis["_id"] = str(diagnosis["_id"])
            return diagnosis
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch diagnosis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch diagnosis: {str(e)}")