"""
Void Request Model - Receipt void requests
"""
from app import db
from datetime import datetime
from app.timezone import now_tw


class VoidRequest(db.Model):
    """Void request model for receipt cancellation"""
    __tablename__ = 'void_requests'

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requested_at = db.Column(db.DateTime, default=now_tw)

    status = db.Column(db.String(20), default='pending', index=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    review_note = db.Column(db.String(200))

    # Relationships
    requester = db.relationship('User', foreign_keys=[requested_by],
                                backref='void_requests_made')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by],
                               backref='void_requests_reviewed')

    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    @property
    def status_display(self):
        """Get status display name in Chinese"""
        status_names = {
            self.STATUS_PENDING: '\u5f85\u5be9\u6838',
            self.STATUS_APPROVED: '\u5df2\u6838\u51c6',
            self.STATUS_REJECTED: '\u5df2\u99c1\u56de'
        }
        return status_names.get(self.status, self.status)

    @classmethod
    def get_pending_requests(cls):
        """Get all pending void requests"""
        return cls.query.filter_by(status=cls.STATUS_PENDING).order_by(
            cls.requested_at.desc()
        ).all()

    def __repr__(self):
        return f'<VoidRequest {self.id} for Receipt {self.receipt_id}>'
