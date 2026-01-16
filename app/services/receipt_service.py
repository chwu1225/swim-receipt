"""
Receipt Service - Business logic for receipts
"""
from app import db
from app.models import Receipt, FeeItem, VoidRequest
from app.services.number_chinese import amount_to_chinese
from datetime import datetime


class ReceiptService:
    """Service class for receipt operations"""

    @staticmethod
    def create_receipt(item_id, amount, operator, remark=None):
        """
        Create a new receipt

        Args:
            item_id: Fee item ID
            amount: Amount to charge
            operator: User object (operator)
            remark: Optional remark

        Returns:
            Receipt object if successful, None otherwise
        """
        fee_item = FeeItem.query.get(item_id)
        if not fee_item:
            raise ValueError('Invalid fee item')

        receipt = Receipt(
            receipt_no=Receipt.generate_receipt_no(),
            item_id=item_id,
            item_name=fee_item.item_name,
            amount=amount,
            amount_chinese=amount_to_chinese(amount),
            remark=remark,
            operator_id=operator.id,
            operator_name=operator.full_name,
            status=Receipt.STATUS_ACTIVE
        )

        db.session.add(receipt)
        db.session.commit()

        return receipt

    @staticmethod
    def get_receipt(receipt_id):
        """Get receipt by ID"""
        return Receipt.query.get(receipt_id)

    @staticmethod
    def get_receipt_by_no(receipt_no):
        """Get receipt by receipt number"""
        return Receipt.query.filter_by(receipt_no=receipt_no).first()

    @staticmethod
    def request_void(receipt_id, reason, requester):
        """
        Request to void a receipt

        Args:
            receipt_id: Receipt ID to void
            reason: Reason for voiding
            requester: User requesting the void

        Returns:
            VoidRequest object if successful
        """
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            raise ValueError('Receipt not found')

        if not receipt.can_void:
            raise ValueError('This receipt cannot be voided')

        # Check if there's already a pending request
        existing = VoidRequest.query.filter_by(
            receipt_id=receipt_id,
            status=VoidRequest.STATUS_PENDING
        ).first()

        if existing:
            raise ValueError('A void request is already pending for this receipt')

        # Create void request
        void_request = VoidRequest(
            receipt_id=receipt_id,
            reason=reason,
            requested_by=requester.id
        )

        # Update receipt status
        receipt.status = Receipt.STATUS_VOID_PENDING

        db.session.add(void_request)
        db.session.commit()

        return void_request

    @staticmethod
    def approve_void(request_id, reviewer, note=None):
        """
        Approve a void request

        Args:
            request_id: VoidRequest ID
            reviewer: User approving the request
            note: Optional review note
        """
        void_request = VoidRequest.query.get(request_id)
        if not void_request:
            raise ValueError('Void request not found')

        if void_request.status != VoidRequest.STATUS_PENDING:
            raise ValueError('This request has already been processed')

        # Update void request
        void_request.status = VoidRequest.STATUS_APPROVED
        void_request.reviewed_by = reviewer.id
        void_request.reviewed_at = datetime.utcnow()
        void_request.review_note = note

        # Update receipt
        receipt = void_request.receipt
        receipt.status = Receipt.STATUS_VOIDED
        receipt.void_reason = void_request.reason
        receipt.voided_by = reviewer.id
        receipt.voided_at = datetime.utcnow()

        db.session.commit()

        return void_request

    @staticmethod
    def reject_void(request_id, reviewer, note=None):
        """
        Reject a void request

        Args:
            request_id: VoidRequest ID
            reviewer: User rejecting the request
            note: Optional review note
        """
        void_request = VoidRequest.query.get(request_id)
        if not void_request:
            raise ValueError('Void request not found')

        if void_request.status != VoidRequest.STATUS_PENDING:
            raise ValueError('This request has already been processed')

        # Update void request
        void_request.status = VoidRequest.STATUS_REJECTED
        void_request.reviewed_by = reviewer.id
        void_request.reviewed_at = datetime.utcnow()
        void_request.review_note = note

        # Restore receipt status
        receipt = void_request.receipt
        receipt.status = Receipt.STATUS_ACTIVE

        db.session.commit()

        return void_request

    @staticmethod
    def verify_receipt(receipt_id, verifier):
        """
        Verify a receipt (by cashier)

        Args:
            receipt_id: Receipt ID
            verifier: User (cashier) verifying
        """
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            raise ValueError('Receipt not found')

        if receipt.status != Receipt.STATUS_ACTIVE:
            raise ValueError('Only active receipts can be verified')

        if receipt.is_verified:
            raise ValueError('Receipt is already verified')

        receipt.is_verified = True
        receipt.verified_by = verifier.id
        receipt.verified_at = datetime.utcnow()

        db.session.commit()

        return receipt

    @staticmethod
    def batch_verify(receipt_ids, verifier):
        """
        Verify multiple receipts at once

        Args:
            receipt_ids: List of receipt IDs
            verifier: User (cashier) verifying

        Returns:
            Number of successfully verified receipts
        """
        count = 0
        for receipt_id in receipt_ids:
            try:
                ReceiptService.verify_receipt(receipt_id, verifier)
                count += 1
            except ValueError:
                continue

        return count
