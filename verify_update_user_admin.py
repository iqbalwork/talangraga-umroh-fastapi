from unittest.mock import MagicMock, patch
from fastapi import UploadFile

def verify_update_user_admin_logic():
    print("Verifying update_user (admin) logic...")

    # Patch dependencies
    with patch("app.api.routes.user.get_db"), \
         patch("app.api.routes.user.get_current_user"), \
         patch("app.api.routes.user.upload_image") as mock_upload_image, \
         patch("app.api.routes.user.hash_password") as mock_hash_password:

        from app.api.routes.user import update_user
        from app.db.models.user import User

        # Setup mock db
        mock_db = MagicMock()

        # Setup mock admin user
        mock_admin = MagicMock(spec=User)
        mock_admin.id = 1
        mock_admin.user_type = "admin"

        # Setup target user to be updated
        mock_target_user = MagicMock(spec=User)
        mock_target_user.id = 99
        mock_target_user.fullname = "Original Name"
        mock_target_user.email = "original@example.com"
        mock_target_user.user_type = "user"
        mock_target_user.image_profile_url = "http://original.com/image.jpg"
        
        mock_target_user.image_profile_url = "http://original.com/image.jpg"
        
        # Add required strings for Pydantic validation of response
        mock_target_user.username = "targetuser"
        mock_target_user.password = "hashed_pw"
        mock_target_user.phone_number = "12345"
        mock_target_user.domisili = "Original City"
        
        # Mock DB query to return target user
        # We use side_effect to handle sequence of calls:
        # 1. Get user by ID (returns mock_target_user)
        # 2. Check username uniqueness (returns None - success)
        # 3. Check email uniqueness (returns None - success)
        
        # Test Case 1: Send empty strings and empty file (should be ignored)
        print("\nTest Case 1: Sending empty values...")
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_target_user]
        
        mock_empty_file = MagicMock(spec=UploadFile)
        mock_empty_file.filename = "" 

        response = update_user(
            user_id=99,
            fullname="",
            username="",
            email="",
            user_type="",
            phone_number="",
            domisili="",
            password="",
            image_profile=mock_empty_file,
            db=mock_db,
            current_user=mock_admin
        )

        assert mock_target_user.fullname == "Original Name"
        assert mock_target_user.email == "original@example.com"
        assert mock_target_user.image_profile_url == "http://original.com/image.jpg"
        
        mock_upload_image.assert_not_called()
        mock_hash_password.assert_not_called()
        
        print("  ✅ All empty/null values were IGNORED. User profile remains unchanged.")

        # Test Case 2: Send valid values as Admin
        print("\nTest Case 2: Sending valid values as Admin...")
        
        # Reset side_effect for next call sequence
        # 1. Get user by ID
        # 2. Check username (returns None so it proceeds)
        # 3. Check email (returns None so it proceeds)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_target_user, None, None]
        
        mock_valid_file = MagicMock(spec=UploadFile)
        mock_valid_file.filename = "admin_upload.jpg"
        mock_upload_image.return_value = "http://new.com/admin_upload.jpg"
        
        # Reset mocks
        mock_upload_image.reset_mock()
        mock_hash_password.reset_mock()

        update_user(
            user_id=99,
            fullname="Admin Updated Name",
            username="admin_updated_user",
            email="admin_updated@example.com",
            user_type="admin", # Admin changing user type
            phone_number="11111",
            domisili="Admin City",
            password="newpassword",
            image_profile=mock_valid_file,
            db=mock_db,
            current_user=mock_admin
        )

        assert mock_target_user.fullname == "Admin Updated Name"
        assert mock_target_user.username == "admin_updated_user"
        assert mock_target_user.email == "admin_updated@example.com"
        assert mock_target_user.user_type == "admin"
        assert mock_target_user.image_profile_url == "http://new.com/admin_upload.jpg"
        
        mock_upload_image.assert_called_once()
        mock_hash_password.assert_called_once()
        
        print("  ✅ Valid values UPDATED the user correctly.")

if __name__ == "__main__":
    verify_update_user_admin_logic()
