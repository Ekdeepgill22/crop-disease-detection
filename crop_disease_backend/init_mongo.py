from pymongo import MongoClient
import os 

# Update this if your MongoDB is not running locally or uses authentication
MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = "crop_disease_db"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Create collections (MongoDB creates them automatically when you insert data)
users = db["users"]
diagnoses = db["diagnoses"]
advisories = db["advisories"]

# Insert a sample advisory if not already present
sample_advisory = {
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

# Only insert if not already present
if not advisories.find_one({"disease_name": "Bacterial_Spot", "crop_type": "Tomato"}):
    advisories.insert_one(sample_advisory)
    print("Sample advisory inserted.")
else:
    print("Sample advisory already exists.")

print("Database initialized successfully.")

client.close()
