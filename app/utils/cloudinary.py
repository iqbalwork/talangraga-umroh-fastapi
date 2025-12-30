import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_image(file: UploadFile) -> str:
    """
    Uploads an image file to Cloudinary and returns the secure URL.
    """
    try:
        # Read file content
        content = file.file.read()
        
        # Upload to Cloudinary
        response = cloudinary.uploader.upload(content)
        
        return response.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
