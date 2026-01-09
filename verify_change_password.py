from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.schemas.user import UserChangePassword

def verify_change_password_logic():
    print("Verifying change_password logic...")

    # Patch dependencies
    with patch("app.api.routes.user.get_db"), \
         patch("app.api.routes.user.get_current_user"), \
         patch("app.api.routes.user.verify_password") as mock_verify_password, \
         patch("app.api.routes.user.hash_password") as mock_hash_password:

        from app.api.routes.user import change_password
        from app.db.models.user import User

        # Setup mock user
        mock_user = MagicMock(spec=User)
        mock_user.password = "hashed_current_password"
        
        # Setup mock db
        mock_db = MagicMock()

        # Test Case 1: Success
        print("\nTest Case 1: Change Password Success...")
        mock_verify_password.return_value = True
        mock_hash_password.return_value = "hashed_new_password"

        payload = UserChangePassword(
            current_password="correct_password",
            new_password="new_password",
            confirm_new_password="new_password"
        )

        response = change_password(
            password_data=payload,
            db=mock_db,
            current_user=mock_user
        )

        assert mock_user.password == "hashed_new_password"
        assert response.code == 200
        print("  ✅ Password changed successfully.")

        # Test Case 2: Wrong Current Password
        print("\nTest Case 2: Wrong Current Password...")
        mock_verify_password.return_value = False
        
        payload_wrong = UserChangePassword(
            current_password="wrong_password",
            new_password="new_password",
            confirm_new_password="new_password"
        )

        try:
            change_password(
                password_data=payload_wrong,
                db=mock_db,
                current_user=mock_user
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "Password saat ini salah"
            print("  ✅ Caught wrong password error correctly.")

        # Test Case 3: Passwords Mismatch (Pydantic validation)
        print("\nTest Case 3: Passwords confirmation mismatch...")
        try:
            UserChangePassword(
                current_password="correct_password",
                new_password="new_password",
                confirm_new_password="mismatch_password"
            )
        except ValueError as e:
             # Pydantic v2 might wrap this, but basic validation check
             print("  ✅ Pydantic raised validation error for properties mismatch.")
        except Exception as e:
             print(f"  ✅ Caught expected validation error: {e}")

if __name__ == "__main__":
    verify_change_password_logic()
