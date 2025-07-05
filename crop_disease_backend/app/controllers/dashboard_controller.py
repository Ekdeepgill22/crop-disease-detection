# dashboard_controller.py
from typing import List
from app.database import get_database
from app.models.user import UserInDB
from app.models.diagnosis import DiagnosisResponse
from bson import ObjectId

class DashboardController:
    def __init__(self):
        pass
    
    async def get_user_diagnosis_history(self, current_user: UserInDB, limit: int = 50) -> List[DiagnosisResponse]:
        """Get diagnosis history for a user"""
        self.db = get_database()
        try:
            cursor = self.db.diagnoses.find(
                {"user_id": ObjectId(current_user.id)}
            ).sort("created_at", -1).limit(limit)
            
            diagnoses = []
            async for diagnosis in cursor:
                diagnoses.append(DiagnosisResponse(
                    id=str(diagnosis["_id"]),
                    crop_type=diagnosis["crop_type"],
                    image_url=diagnosis["image_url"],
                    predicted_disease=diagnosis["predicted_disease"],
                    confidence_score=diagnosis["confidence_score"],
                    advisory=diagnosis.get("advisory"),
                    created_at=diagnosis["created_at"]
                ))
            
            return diagnoses
        except Exception as e:
            raise Exception(f"Failed to fetch diagnosis history: {str(e)}")
    
    async def get_user_statistics(self, current_user: UserInDB) -> dict:
        """Get user statistics"""
        self.db = get_database()
        try:
            # Total diagnoses
            total_diagnoses = await self.db.diagnoses.count_documents(
                {"user_id": ObjectId(current_user.id)}
            )
            
            # Most common diseases
            pipeline = [
                {"$match": {"user_id": ObjectId(current_user.id)}},
                {"$group": {"_id": "$predicted_disease", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            common_diseases = []
            async for result in self.db.diagnoses.aggregate(pipeline):
                common_diseases.append({
                    "disease": result["_id"],
                    "count": result["count"]
                })
            
            # Most common crops
            pipeline[1]["$group"]["_id"] = "$crop_type"
            common_crops = []
            async for result in self.db.diagnoses.aggregate(pipeline):
                common_crops.append({
                    "crop": result["_id"],
                    "count": result["count"]
                })
            
            return {
                "total_diagnoses": total_diagnoses,
                "most_common_diseases": common_diseases,
                "most_common_crops": common_crops
            }
        except Exception as e:
            raise Exception(f"Failed to fetch user statistics: {str(e)}")
