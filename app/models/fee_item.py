"""
Fee Item Model - Swimming pool fee items
"""
from app import db
from datetime import datetime


class FeeItem(db.Model):
    """Fee item model for swimming pool charges"""
    __tablename__ = 'fee_items'

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Category: admission, pass, course, rental
    identity_type = db.Column(db.String(50))  # Identity: student, staff, external, discount
    default_price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    receipts = db.relationship('Receipt', backref='fee_item', lazy='dynamic')

    # Category constants
    CATEGORY_ADMISSION = '\u5165\u5834\u5238'
    CATEGORY_PASS = '\u7968\u5238'
    CATEGORY_COURSE = '\u8ab2\u7a0b'
    CATEGORY_RENTAL = '\u79df\u501f'
    CATEGORY_OTHER = '\u5176\u4ed6'

    # Identity type constants
    IDENTITY_STUDENT = '\u5b78\u751f'
    IDENTITY_STAFF = '\u6559\u8077\u54e1'
    IDENTITY_EXTERNAL = '\u6821\u5916\u4eba\u58eb'
    IDENTITY_DISCOUNT = '\u512a\u60e0\u7968'

    @classmethod
    def get_active_items(cls):
        """Get all active fee items ordered by category and sort_order"""
        return cls.query.filter_by(is_active=True).order_by(
            cls.category, cls.sort_order, cls.item_name
        ).all()

    @classmethod
    def get_items_by_category(cls, category):
        """Get active items by category"""
        return cls.query.filter_by(
            is_active=True, category=category
        ).order_by(cls.sort_order, cls.item_name).all()

    def __repr__(self):
        return f'<FeeItem {self.item_code}: {self.item_name}>'
