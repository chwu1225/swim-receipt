"""
Authentication Routes - Login, Logout
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('\u6b64\u5e33\u865f\u5df2\u505c\u7528', 'error')
                return render_template('auth/login.html')

            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('\u5e33\u865f\u6216\u5bc6\u78bc\u932f\u8aa4', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('\u60a8\u5df2\u6210\u529f\u767b\u51fa', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_user.check_password(current_password):
            flash('\u76ee\u524d\u5bc6\u78bc\u932f\u8aa4', 'error')
        elif new_password != confirm_password:
            flash('\u65b0\u5bc6\u78bc\u8207\u78ba\u8a8d\u5bc6\u78bc\u4e0d\u7b26', 'error')
        elif len(new_password) < 6:
            flash('\u65b0\u5bc6\u78bc\u81f3\u5c11\u9700\u89816\u500b\u5b57\u5143', 'error')
        else:
            current_user.set_password(new_password)
            from app import db
            db.session.commit()
            flash('\u5bc6\u78bc\u5df2\u6210\u529f\u8b8a\u66f4', 'success')
            return redirect(url_for('main.dashboard'))

    return render_template('auth/change_password.html')
