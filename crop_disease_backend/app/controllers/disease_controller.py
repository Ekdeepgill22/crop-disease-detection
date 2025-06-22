# disease_controller.py
from fastapi import HTTPException, UploadFile
from PIL import Image
from app.database import get_database
from app.models.user import UserInDB, PyObjectId
from app.models.diagnosis import DiagnosisCreate, DiagnosisInDB, PredictionResult
from app.utils.image_utils import save_image, preprocess_image
from app.utils.kindwise_api import KindwiseAPI
from app.controllers.advisory_controller import AdvisoryController
from bson import ObjectId
from typing import Optional

class DiseaseController:
    def __init__(self):
        self.db = get_database()
        self.advisory_controller = AdvisoryController()
        self.kindwise_api = KindwiseAPI()
    
    def _get_db(self):
        """Get database instance with proper error handling"""
        if self.db is None:
            raise HTTPException(status_code=500, detail="Database connection not available")
        return self.db
    
    async def predict_disease(self, file: UploadFile, crop_type: str, current_user: UserInDB) -> PredictionResult:
        """Predict disease from uploaded image using Kindwise API"""
        try:
            # Save uploaded image
            file_path, file_url = await save_image(file)
            
            # Load and preprocess image
            image = preprocess_image(file_path)
            
            # Predict disease using Kindwise API
            disease_name, confidence_score, disease_info = self.kindwise_api.predict_disease(image, crop_type)
            
            # Get advisory for the predicted disease
            advisory = await self.advisory_controller.get_advisory_by_disease(disease_name, crop_type)
            
            # Save diagnosis to database
            diagnosis_data = DiagnosisCreate(
                crop_type=crop_type,
                image_path=file_path,
                predicted_disease=disease_name,
                confidence_score=confidence_score
            )
            
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
            db = self._get_db()
            await db.diagnoses.insert_one(diagnosis_in_db.dict(by_alias=True))
            
            return PredictionResult(
                disease_name=disease_name,
                confidence_score=confidence_score,
                crop_type=crop_type,
                advisory=advisory.dict() if advisory else {},
                api_response=disease_info
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    
    async def get_diagnosis_history(self, current_user: UserInDB, limit: int = 10):
        """Get user's diagnosis history"""
        try:
            db = self._get_db()
            cursor = db.diagnoses.find(
                {"user_id": ObjectId(current_user.id)}
            ).sort("created_at", -1).limit(limit)
            
            diagnoses = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                diagnoses.append(doc)
            
            return diagnoses
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch diagnosis history: {str(e)}")
    
    async def get_diagnosis_by_id(self, diagnosis_id: str, current_user: UserInDB):
        """Get specific diagnosis by ID"""
        try:
            db = self._get_db()
            diagnosis = await db.diagnoses.find_one({
                "_id": ObjectId(diagnosis_id),
                "user_id": ObjectId(current_user.id)
            })
            
            if not diagnosis:
                raise HTTPException(status_code=404, detail="Diagnosis not found")
            
            diagnosis["_id"] = str(diagnosis["_id"])
            return diagnosis
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch diagnosis: {str(e)}")