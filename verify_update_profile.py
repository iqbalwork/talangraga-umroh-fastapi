from unittest.mock import MagicMock, patch
from fastapi import UploadFile, HTTPException


def verify_update_profile_logic():
    print("Verifying update_own_profile logic...")

    # Patch dependencies
    with patch("app.api.routes.user.get_db"), \
         patch("app.api.routes.user.get_current_user"), \
         patch("app.api.routes.user.upload_image") as mock_upload_image, \
         patch("app.api.routes.user.hash_password") as mock_hash_password:

        from app.api.routes.user import update_own_profile
        from app.db.models.user import User

        # Setup mock user
        mock_user = MagicMock(spec=User)
        mock_user.fullname = "Original Name"
        mock_user.username = "originaluser"
        mock_user.email = "original@example.com"
        mock_user.phone_number = "12345"
        mock_user.domisili = "Original City"
        mock_user.password = "hashed_old_password"
        mock_user.image_profile_url = "http://original.com/image.jpg"
        mock_user.user_type = "user" # Required for Pydantic
        
        # Setup mock db
        mock_db = MagicMock()

        # Test Case 1: Send empty strings and empty file (should be ignored)
        print("\nTest Case 1: Sending empty values...")
        
        mock_empty_file = MagicMock(spec=UploadFile)
        mock_empty_file.filename = "" 

        response = update_own_profile(
            fullname="",
            username="",
            email="",
            phone_number="   ",
            domisili=None,
            password="",
            image_profile=mock_empty_file,
            db=mock_db,
            current_user=mock_user
        )

        assert mock_user.fullname == "Original Name"
        assert mock_user.username == "originaluser"
        assert mock_user.email == "original@example.com"
        
        print("  ✅ All empty/null values were IGNORED.")

        # Test Case 2: Send valid values (Success)
        print("\nTest Case 2: Sending valid values (Success)...")
        
        # Mock checks for uniqueness (return None means no existing user found)
        # Sequence: 1. check username -> None, 2. check email -> None
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, None]
        
        mock_valid_file = MagicMock(spec=UploadFile)
        mock_valid_file.filename = "new_pic.jpg"
        mock_upload_image.return_value = "http://new.com/image.jpg"
        mock_hash_password.return_value = "hashed_new_password"

        update_own_profile(
            fullname="New Name",
            username="newuser",
            email="new@example.com",
            phone_number="67890",
            domisili="New City",
            password="newpassword",
            image_profile=mock_valid_file,
            db=mock_db,
            current_user=mock_user
        )

        assert mock_user.fullname == "New Name"
        assert mock_user.username == "newuser"
        assert mock_user.email == "new@example.com"
        assert mock_user.phone_number == "67890"
        
        print("  ✅ Valid values UPDATED the profile correctly.")

        # Test Case 3: Duplicate Username (Failure)
        print("\nTest Case 3: Duplicate Username...")
        
        # Mock existing user found
        mock_existing_user = MagicMock(spec=User)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_existing_user]
        
        # Reset user username for test
        mock_user.username = "originaluser"

        try:
            update_own_profile(
                username="takenuser",
                # Pass None for other optional args checks to avoid default Form() object
                fullname=None,
                email=None,
                phone_number=None,
                domisili=None,
                password=None,
                db=mock_db,
                current_user=mock_user
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Username already registered"
            print("  ✅ Correctly caught duplicate username error.")
            
        # Test Case 4: Duplicate Email (Failure)
        print("\nTest Case 4: Duplicate Email...")
        
         # Reset side effect: 1. username check (None - ok), 2. email check (Existing User - fail)
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, mock_existing_user]
        
        # Reset user email
        mock_user.email = "original@example.com"

        try:
            update_own_profile(
                username="newuser_unique",
                email="taken@example.com",
                fullname=None,
                phone_number=None,
                domisili=None,
                password=None,
                db=mock_db,
                current_user=mock_user
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Email already registered"
            print("  ✅ Correctly caught duplicate email error.")

        # Test Case 5: Sending 'image_profile' as empty string (Postman behavior)
        print("\nTest Case 5: Sending 'image_profile' as empty string (Postman behavior)...")
        try:
            # Simulate sending image_profile as empty string
            mock_user.email, mock_user.username = "test@example.com", "testuser" # Reset checks
            update_own_profile(
                image_profile="", # Passing string instead of UploadFile
                fullname=None,
                username=None,
                email=None,
                phone_number=None,
                domisili=None,
                password=None,
                db=mock_db,
                current_user=mock_user
            )
            print("  ✅ Empty string for image_profile was IGNORED (Success).")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

if __name__ == "__main__":
    verify_update_profile_logic()
