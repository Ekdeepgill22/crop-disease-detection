from bson import ObjectId
from app.models.user import PyObjectId

def convert_objectids_to_str(doc):
    """
    Recursively convert ObjectId and PyObjectId instances to strings in a document.
    Handles nested dictionaries and lists to prevent Pydantic serialization warnings.
    """
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            if isinstance(v, (ObjectId, PyObjectId)):
                result[k] = str(v)
            elif isinstance(v, dict):
                result[k] = convert_objectids_to_str(v)
            elif isinstance(v, list):
                result[k] = [convert_objectids_to_str(i) if isinstance(i, (dict, ObjectId, PyObjectId)) 
                           else str(i) if isinstance(i, (ObjectId, PyObjectId)) else i for i in v]
            else:
                result[k] = v
        return result
    elif isinstance(doc, (ObjectId, PyObjectId)):
        return str(doc)
    elif isinstance(doc, list):
        return [convert_objectids_to_str(i) if isinstance(i, (dict, ObjectId, PyObjectId)) 
                else str(i) if isinstance(i, (ObjectId, PyObjectId)) else i for i in doc]
    else:
        return doc