"""
Payment Record Model - Monthly payment records
"""
from app import db
from datetime import datetime


class PaymentRecord(db.Model):
    """Payment record for monthly settlements"""
    __tablename__ = 'payment_records'

    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)

    system_amount = db.Column(db.Numeric(12, 2), nullable=False)  # Calculated amount
    actual_amount = db.Column(db.Numeric(12, 2), nullable=False)  # Actual received amount
    difference = db.Column(db.Numeric(12, 2))  # Difference

    received_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(500))

    # Relationships
    operator = db.relationship('User', foreign_keys=[operator_id],
                               backref='payment_records')
    receiver = db.relationship('User', foreign_keys=[received_by],
                               backref='payments_received')

    def __repr__(self):
        return f'<PaymentRecord {self.id}: {self.period_start} to {self.period_end}>'
