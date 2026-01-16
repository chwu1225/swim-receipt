"""
Admin Routes - System administration (Demo Mode)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User, FeeItem
from decimal import Decimal

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
def index():
    """Admin dashboard"""
    user_count = User.query.count()
    item_count = FeeItem.query.filter_by(is_active=True).count()

    return render_template('admin/index.html',
                          user_count=user_count,
                          item_count=item_count)


# User Management
@admin_bp.route('/users')
def users():
    """User list"""
    all_users = User.query.order_by(User.role, User.username).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
def create_user():
    """Create new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', User.ROLE_OPERATOR)

        if not username:
            flash('請輸入帳號', 'error')
        elif not full_name:
            flash('請輸入姓名', 'error')
        elif len(password) < 6:
            flash('密碼至少需要6個字元', 'error')
        elif User.query.filter_by(username=username).first():
            flash('帳號已存在', 'error')
        else:
            user = User(
                username=username,
                full_name=full_name,
                role=role
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'使用者 {username} 已建立', 'success')
            return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', user=None)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', User.ROLE_OPERATOR)
        is_active = request.form.get('is_active') == 'on'
        new_password = request.form.get('new_password', '')

        if not full_name:
            flash('請輸入姓名', 'error')
        else:
            user.full_name = full_name
            user.role = role
            user.is_active = is_active

            if new_password:
                if len(new_password) < 6:
                    flash('密碼至少需要6個字元', 'error')
                    return render_template('admin/user_form.html', user=user)
                user.set_password(new_password)

            db.session.commit()
            flash('使用者資料已更新', 'success')
            return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', user=user)


# Fee Item Management
@admin_bp.route('/fee-items')
def fee_items():
    """Fee item list"""
    items = FeeItem.query.order_by(FeeItem.category, FeeItem.sort_order).all()
    return render_template('admin/fee_items.html', items=items)


@admin_bp.route('/fee-items/create', methods=['GET', 'POST'])
def create_fee_item():
    """Create new fee item"""
    if request.method == 'POST':
        item_code = request.form.get('item_code', '').strip()
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        identity_type = request.form.get('identity_type', '').strip()
        default_price = request.form.get('default_price', type=float)
        description = request.form.get('description', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)

        if not item_code:
            flash('請輸入項目代碼', 'error')
        elif not item_name:
            flash('請輸入項目名稱', 'error')
        elif default_price is None or default_price < 0:
            flash('請輸入有效的預設金額', 'error')
        elif FeeItem.query.filter_by(item_code=item_code).first():
            flash('項目代碼已存在', 'error')
        else:
            item = FeeItem(
                item_code=item_code,
                item_name=item_name,
                category=category if category else None,
                identity_type=identity_type if identity_type else None,
                default_price=Decimal(str(default_price)),
                description=description if description else None,
                sort_order=sort_order
            )
            db.session.add(item)
            db.session.commit()
            flash(f'收費項目 {item_name} 已建立', 'success')
            return redirect(url_for('admin.fee_items'))

    return render_template('admin/fee_item_form.html', item=None)


@admin_bp.route('/fee-items/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_fee_item(item_id):
    """Edit fee item"""
    item = FeeItem.query.get_or_404(item_id)

    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        identity_type = request.form.get('identity_type', '').strip()
        default_price = request.form.get('default_price', type=float)
        description = request.form.get('description', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        is_active = request.form.get('is_active') == 'on'

        if not item_name:
            flash('請輸入項目名稱', 'error')
        elif default_price is None or default_price < 0:
            flash('請輸入有效的預設金額', 'error')
        else:
            item.item_name = item_name
            item.category = category if category else None
            item.identity_type = identity_type if identity_type else None
            item.default_price = Decimal(str(default_price))
            item.description = description if description else None
            item.sort_order = sort_order
            item.is_active = is_active

            db.session.commit()
            flash('收費項目已更新', 'success')
            return redirect(url_for('admin.fee_items'))

    return render_template('admin/fee_item_form.html', item=item)
