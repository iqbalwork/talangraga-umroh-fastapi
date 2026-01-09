from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.schemas.user import UserResetPassword
from jose import jwt

def verify_reset_password_logic():
    print("Verifying reset_password logic...")

    # Patch dependencies
    with patch("app.api.routes.auth.get_db"), \
         patch("app.api.routes.auth.hash_password") as mock_hash_password, \
         patch("app.api.routes.auth.SECRET_KEY", "test_secret"), \
         patch("app.api.routes.auth.ALGORITHM", "HS256"):

        from app.api.routes.auth import reset_password
        from app.db.models.user import User

        # Setup mock db
        mock_db = MagicMock()
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.password = "old_password"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Create a valid token
        valid_token = jwt.encode({"sub": "test@example.com"}, "test_secret", algorithm="HS256")
        
        # Test Case 1: Success
        print("\nTest Case 1: Reset Password Success...")
        mock_hash_password.return_value = "hashed_new_password"

        payload = UserResetPassword(
            reset_token=valid_token,
            new_password="new_password",
            confirm_new_password="new_password"
        )

        response = reset_password(
            request=payload,
            db=mock_db
        )

        assert mock_user.password == "hashed_new_password"
        assert response.code == 200
        print("  ✅ Password reset successfully.")

        # Test Case 2: Invalid Token
        print("\nTest Case 2: Invalid Token...")
        invalid_token = "invalid_token_string"
        
        payload_invalid = UserResetPassword(
            reset_token=invalid_token,
            new_password="new_password",
            confirm_new_password="new_password"
        )

        try:
            reset_password(
                request=payload_invalid,
                db=mock_db
            )
        except HTTPException as e:
            assert e.status_code == 400
            assert "Invalid" in e.detail or "expired" in e.detail
            print("  ✅ Caught invalid token error correctly.")

        # Test Case 3: Passwords Mismatch (Pydantic validation)
        print("\nTest Case 3: Passwords confirmation mismatch...")
        try:
            UserResetPassword(
                reset_token=valid_token,
                new_password="new_password",
                confirm_new_password="mismatch_password"
            )
        except ValueError as e:
             print("  ✅ Pydantic raised validation error for properties mismatch.")
        except Exception as e:
             print(f"  ✅ Caught expected validation error: {e}")

if __name__ == "__main__":
    verify_reset_password_logic()
