import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi import UploadFile

# Mock dependencies before importing the module to avoid side effects if any
# (though importing usually is fine if we patch where it is used)

def verify_create_transaction_logic():
    print("Verifying create_transaction logic...")

    # We need to test the create_transaction function
    # But it relies on `Transaction` class and `upload_image` utility.
    
    # Patch the class definition itself to ensure all imports get the mock
    with patch("app.db.models.transaction.Transaction") as MockTransaction, \
         patch("app.api.routes.transaction.upload_image") as mock_upload_image, \
         patch("app.api.routes.transaction.get_db"), \
         patch("app.api.routes.transaction.get_current_user"), \
         patch("app.schemas.transaction.TransactionOut") as MockTransactionOut:

        from app.api.routes.transaction import create_transaction
        from app.db.models.user import User

        # Setup mocks
        mock_db = MagicMock()
        mock_current_user = MagicMock(spec=User)
        mock_current_user.id = 999 
        mock_upload_image.return_value = "http://cloudinary.com/image.jpg"
        
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.jpg"

        # Mock TransactionOut.from_orm
        MockTransactionOut.from_orm.return_value = {"id": 123} # Return a dict which is safer for BaseResponse data

        # Use a fixed datetime for comparison
        tx_date = datetime.now()

        print("\nTest Case 1: userId=10, reportedByUserId=None")

        # Mock the return value of Transaction(...) to be added to DB
        mock_tx_instance = MagicMock()
        MockTransaction.return_value = mock_tx_instance
        
        response = create_transaction(
            userId=10,
            reportedByUserId=None,
            amount=50000,
            transaction_date=tx_date,
            periode_id=1,
            payment_id=2,
            file=mock_file,
            db=mock_db,
            current_user=mock_current_user
        )

        MockTransaction.assert_called_with(
            amount=50000,
            transaction_date=tx_date,
            bukti_transfer_url="http://cloudinary.com/image.jpg",
            periode_id=1,
            payment_id=2,
            reported_by_id=999, 
            user_id=10
        )
        print("  ✅ Transaction created with correct user_id=10 and reported_by_id=999")

        # Test Case 2: Explicit reportedByUserId
        print("\nTest Case 2: userId=10, reportedByUserId=55")
        create_transaction(
            userId=10,
            reportedByUserId=55,
            amount=50000,
            transaction_date=datetime.now(),
            periode_id=1,
            payment_id=2,
            file=mock_file,
            db=mock_db,
            current_user=mock_current_user
        )

        # Assertions
        # Get the call args
        call_args = MockTransaction.call_args_list[-1] # GET LAST CALL
        # args, kwargs = call_args
        kwargs = call_args[1]
        
        assert kwargs["user_id"] == 10
        assert kwargs["reported_by_id"] == 55
        print("  ✅ Transaction created with correct user_id=10 and reported_by_id=55")

if __name__ == "__main__":
    verify_create_transaction_logic()
