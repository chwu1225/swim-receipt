"""
Initialization Service - Setup default data
"""
from app import db
from app.models import User, FeeItem


def init_default_data():
    """Initialize default users and fee items"""
    # Check if already initialized
    if User.query.first() is not None:
        return

    # Create default admin user
    admin = User(
        username='admin',
        full_name='\u7cfb\u7d71\u7ba1\u7406\u54e1',
        role=User.ROLE_ADMIN
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # Create default operator
    operator = User(
        username='operator',
        full_name='\u6ac3\u53f0\u4eba\u54e1',
        role=User.ROLE_OPERATOR
    )
    operator.set_password('operator123')
    db.session.add(operator)

    # Create default cashier
    cashier = User(
        username='cashier',
        full_name='\u51fa\u7d0d\u4eba\u54e1',
        role=User.ROLE_CASHIER
    )
    cashier.set_password('cashier123')
    db.session.add(cashier)

    # Create default supervisor
    supervisor = User(
        username='supervisor',
        full_name='\u4e3b\u7ba1',
        role=User.ROLE_SUPERVISOR
    )
    supervisor.set_password('supervisor123')
    db.session.add(supervisor)

    # Create default fee items
    fee_items = [
        # Admission tickets
        FeeItem(
            item_code='ADM-STU',
            item_name='\u6e38\u6cf3\u6c60\u5165\u5834\u5238-\u5b78\u751f',
            category=FeeItem.CATEGORY_ADMISSION,
            identity_type=FeeItem.IDENTITY_STUDENT,
            default_price=50,
            description='\u5b78\u751f\u55ae\u6b21\u5165\u5834',
            sort_order=1
        ),
        FeeItem(
            item_code='ADM-STAFF',
            item_name='\u6e38\u6cf3\u6c60\u5165\u5834\u5238-\u6559\u8077\u54e1',
            category=FeeItem.CATEGORY_ADMISSION,
            identity_type=FeeItem.IDENTITY_STAFF,
            default_price=80,
            description='\u6559\u8077\u54e1\u55ae\u6b21\u5165\u5834',
            sort_order=2
        ),
        FeeItem(
            item_code='ADM-EXT',
            item_name='\u6e38\u6cf3\u6c60\u5165\u5834\u5238-\u6821\u5916\u4eba\u58eb',
            category=FeeItem.CATEGORY_ADMISSION,
            identity_type=FeeItem.IDENTITY_EXTERNAL,
            default_price=150,
            description='\u6821\u5916\u4eba\u58eb\u55ae\u6b21\u5165\u5834',
            sort_order=3
        ),
        FeeItem(
            item_code='ADM-SENIOR',
            item_name='\u6e38\u6cf3\u6c60\u5165\u5834\u5238-\u656c\u8001\u512a\u60e0',
            category=FeeItem.CATEGORY_ADMISSION,
            identity_type=FeeItem.IDENTITY_DISCOUNT,
            default_price=50,
            description='65\u6b72\u4ee5\u4e0a\u512a\u60e0',
            sort_order=4
        ),
        FeeItem(
            item_code='ADM-DISABLED',
            item_name='\u6e38\u6cf3\u6c60\u5165\u5834\u5238-\u611b\u5fc3\u512a\u60e0',
            category=FeeItem.CATEGORY_ADMISSION,
            identity_type=FeeItem.IDENTITY_DISCOUNT,
            default_price=50,
            description='\u8eab\u5fc3\u969c\u7919\u512a\u60e0',
            sort_order=5
        ),
        # Pass tickets
        FeeItem(
            item_code='PASS-M-STU',
            item_name='\u6e38\u6cf3\u6c60\u6708\u7968-\u5b78\u751f',
            category=FeeItem.CATEGORY_PASS,
            identity_type=FeeItem.IDENTITY_STUDENT,
            default_price=800,
            description='\u5b78\u751f\u7576\u6708\u7121\u9650\u6b21',
            sort_order=10
        ),
        FeeItem(
            item_code='PASS-M-STAFF',
            item_name='\u6e38\u6cf3\u6c60\u6708\u7968-\u6559\u8077\u54e1',
            category=FeeItem.CATEGORY_PASS,
            identity_type=FeeItem.IDENTITY_STAFF,
            default_price=600,
            description='\u6559\u8077\u54e1\u7576\u6708\u7121\u9650\u6b21',
            sort_order=11
        ),
        FeeItem(
            item_code='PASS-M-EXT',
            item_name='\u6e38\u6cf3\u6c60\u6708\u7968-\u6821\u5916\u4eba\u58eb',
            category=FeeItem.CATEGORY_PASS,
            identity_type=FeeItem.IDENTITY_EXTERNAL,
            default_price=2000,
            description='\u6821\u5916\u4eba\u58eb\u7576\u6708\u7121\u9650\u6b21',
            sort_order=12
        ),
        FeeItem(
            item_code='PASS-S-STU',
            item_name='\u6e38\u6cf3\u6c60\u5b63\u7968-\u5b78\u751f',
            category=FeeItem.CATEGORY_PASS,
            identity_type=FeeItem.IDENTITY_STUDENT,
            default_price=2000,
            description='\u5b78\u751f\u4e09\u500b\u6708\u7121\u9650\u6b21',
            sort_order=13
        ),
        FeeItem(
            item_code='PASS-10-STU',
            item_name='\u6e38\u6cf3\u6c6010\u6b21\u5238-\u5b78\u751f',
            category=FeeItem.CATEGORY_PASS,
            identity_type=FeeItem.IDENTITY_STUDENT,
            default_price=400,
            description='\u5b78\u751f10\u6b21\u5165\u5834\u5238',
            sort_order=14
        ),
        # Rental
        FeeItem(
            item_code='RENT-LANE',
            item_name='\u6c34\u9053\u79df\u501f\u8cbb',
            category=FeeItem.CATEGORY_RENTAL,
            identity_type=None,
            default_price=500,
            description='\u55ae\u4e00\u6c34\u9053\u6bcf\u5c0f\u6642',
            sort_order=20
        ),
        FeeItem(
            item_code='LOCKER-FEE',
            item_name='\u7f6e\u7269\u6ac3\u79df\u91d1',
            category=FeeItem.CATEGORY_RENTAL,
            identity_type=None,
            default_price=50,
            description='\u81e8\u6642\u79df\u501f',
            sort_order=21
        ),
        # Other
        FeeItem(
            item_code='MISC',
            item_name='\u5176\u4ed6\u6536\u5165',
            category=FeeItem.CATEGORY_OTHER,
            identity_type=None,
            default_price=0,
            description='\u96dc\u9805\u6536\u5165\uff0c\u9700\u624b\u52d5\u8f38\u5165\u91d1\u984d',
            sort_order=99
        ),
    ]

    for item in fee_items:
        db.session.add(item)

    db.session.commit()
    print('Default data initialized successfully.')
