"""
User Model - Operators, Supervisors, Cashiers, Admins
"""
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    receipts = db.relationship('Receipt', backref='operator', lazy='dynamic',
                               foreign_keys='Receipt.operator_id')
    verified_receipts = db.relationship('Receipt', backref='verifier', lazy='dynamic',
                                        foreign_keys='Receipt.verified_by')

    # Role constants
    ROLE_OPERATOR = 'operator'      # Operator: create receipts
    ROLE_SUPERVISOR = 'supervisor'  # Supervisor: approve void requests
    ROLE_CASHIER = 'cashier'        # Cashier: verify receipts, receive payments
    ROLE_ADMIN = 'admin'            # Admin: full access

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def can_create_receipt(self):
        """Check if user can create receipts"""
        return self.role in [self.ROLE_OPERATOR, self.ROLE_SUPERVISOR, self.ROLE_ADMIN]

    def can_approve_void(self):
        """Check if user can approve void requests"""
        return self.role in [self.ROLE_SUPERVISOR, self.ROLE_CASHIER, self.ROLE_ADMIN]

    def can_verify_receipt(self):
        """Check if user can verify receipts"""
        return self.role in [self.ROLE_CASHIER, self.ROLE_ADMIN]

    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role == self.ROLE_ADMIN

    def can_manage_fee_items(self):
        """Check if user can manage fee items"""
        return self.role == self.ROLE_ADMIN

    def can_export_reports(self):
        """Check if user can export reports"""
        return self.role in [self.ROLE_SUPERVISOR, self.ROLE_CASHIER, self.ROLE_ADMIN]

    @property
    def role_display(self):
        """Get role display name in Chinese"""
        role_names = {
            self.ROLE_OPERATOR: '\u64cd\u4f5c\u54e1',
            self.ROLE_SUPERVISOR: '\u4e3b\u7ba1',
            self.ROLE_CASHIER: '\u51fa\u7d0d',
            self.ROLE_ADMIN: '\u7ba1\u7406\u54e1'
        }
        return role_names.get(self.role, self.role)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))
