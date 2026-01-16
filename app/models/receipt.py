"""
Receipt Model - Swimming pool receipts
"""
from app import db
from datetime import datetime, date


class Receipt(db.Model):
    """Receipt model for swimming pool charges"""
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    receipt_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('fee_items.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)  # Denormalized for record keeping
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    amount_chinese = db.Column(db.String(50))  # Chinese numeral representation
    remark = db.Column(db.String(200))

    # Operator info
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operator_name = db.Column(db.String(50), nullable=False)  # Denormalized
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Status
    status = db.Column(db.String(20), default='active', index=True)

    # Verification info
    is_verified = db.Column(db.Boolean, default=False, index=True)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)

    # Void info
    void_reason = db.Column(db.String(200))
    voided_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    voided_at = db.Column(db.DateTime)

    # Relationships
    void_requests = db.relationship('VoidRequest', backref='receipt', lazy='dynamic')

    # Status constants
    STATUS_ACTIVE = 'active'
    STATUS_VOID_PENDING = 'void_pending'
    STATUS_VOIDED = 'voided'

    @classmethod
    def generate_receipt_no(cls, prefix='SWIM'):
        """Generate unique receipt number: SWIM-YYYYMMDD-XXXX"""
        today = date.today()
        date_str = today.strftime('%Y%m%d')
        prefix_pattern = f'{prefix}-{date_str}-'

        # Find the last receipt number for today
        last_receipt = cls.query.filter(
            cls.receipt_no.like(f'{prefix_pattern}%')
        ).order_by(cls.receipt_no.desc()).first()

        if last_receipt:
            # Extract sequence number and increment
            last_seq = int(last_receipt.receipt_no.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f'{prefix_pattern}{new_seq:04d}'

    @property
    def can_void(self):
        """Check if receipt can be voided"""
        return self.status == self.STATUS_ACTIVE and not self.is_verified

    @property
    def status_display(self):
        """Get status display name in Chinese"""
        status_names = {
            self.STATUS_ACTIVE: '\u6b63\u5e38',
            self.STATUS_VOID_PENDING: '\u5f85\u5be9\u6838\u4f5c\u5ee2',
            self.STATUS_VOIDED: '\u5df2\u4f5c\u5ee2'
        }
        return status_names.get(self.status, self.status)

    @classmethod
    def get_daily_receipts(cls, target_date=None, operator_id=None):
        """Get receipts for a specific date"""
        if target_date is None:
            target_date = date.today()

        query = cls.query.filter(
            db.func.date(cls.created_at) == target_date
        )

        if operator_id:
            query = query.filter_by(operator_id=operator_id)

        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_monthly_summary(cls, year, month, operator_id=None):
        """Get monthly summary statistics"""
        from sqlalchemy import func, and_
        from calendar import monthrange

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        query = cls.query.filter(
            and_(
                func.date(cls.created_at) >= start_date,
                func.date(cls.created_at) <= end_date
            )
        )

        if operator_id:
            query = query.filter_by(operator_id=operator_id)

        return query.all()

    def __repr__(self):
        return f'<Receipt {self.receipt_no}>'
