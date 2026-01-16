"""
Verification Routes - Cashier verification (Demo Mode)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Receipt, PaymentRecord, User
from app.services.receipt_service import ReceiptService
from app.services.report_service import ReportService
from datetime import date
from decimal import Decimal

verify_bp = Blueprint('verify', __name__)


def get_current_user():
    """Get demo user"""
    from app import DemoUser
    return DemoUser()


@verify_bp.route('/')
def index():
    """Verification main page"""
    # Get all operators
    operators = User.query.filter(
        User.role.in_([User.ROLE_OPERATOR, User.ROLE_SUPERVISOR, User.ROLE_ADMIN])
    ).filter_by(is_active=True).all()

    # Get verification summary for current month
    summaries = []
    for operator in operators:
        summary = ReportService.get_verification_summary(operator_id=operator.id)
        summary['operator'] = operator
        summaries.append(summary)

    return render_template('verify/index.html', summaries=summaries)


@verify_bp.route('/operator/<int:operator_id>')
def operator_detail(operator_id):
    """View unverified receipts for an operator"""
    operator = User.query.get_or_404(operator_id)
    summary = ReportService.get_verification_summary(operator_id=operator_id)

    return render_template('verify/operator_detail.html',
                          operator=operator,
                          summary=summary)


@verify_bp.route('/receipt/<int:receipt_id>', methods=['POST'])
def verify_single(receipt_id):
    """Verify a single receipt"""
    current_user = get_current_user()

    try:
        ReceiptService.verify_receipt(receipt_id, current_user)
        flash('收據驗證成功', 'success')
    except ValueError as e:
        flash(str(e), 'error')

    # Redirect back
    next_url = request.form.get('next') or url_for('verify.index')
    return redirect(next_url)


@verify_bp.route('/batch', methods=['POST'])
def verify_batch():
    """Verify multiple receipts at once"""
    current_user = get_current_user()
    receipt_ids = request.form.getlist('receipt_ids', type=int)

    if not receipt_ids:
        flash('請選擇要驗證的收據', 'error')
        return redirect(url_for('verify.index'))

    count = ReceiptService.batch_verify(receipt_ids, current_user)
    flash(f'已成功驗證 {count} 筆收據', 'success')

    next_url = request.form.get('next') or url_for('verify.index')
    return redirect(next_url)


@verify_bp.route('/payment/create/<int:operator_id>', methods=['GET', 'POST'])
def create_payment(operator_id):
    """Create payment record"""
    current_user = get_current_user()
    operator = User.query.get_or_404(operator_id)
    summary = ReportService.get_verification_summary(operator_id=operator_id)

    if request.method == 'POST':
        actual_amount = request.form.get('actual_amount', type=float)
        notes = request.form.get('notes', '').strip()

        if actual_amount is None:
            flash('請輸入實際繳款金額', 'error')
        else:
            system_amount = float(summary['total_amount'])
            difference = actual_amount - system_amount

            payment = PaymentRecord(
                operator_id=operator_id,
                period_start=summary['period_start'],
                period_end=summary['period_end'],
                system_amount=Decimal(str(system_amount)),
                actual_amount=Decimal(str(actual_amount)),
                difference=Decimal(str(difference)),
                received_by=current_user.id,
                notes=notes if notes else None
            )

            db.session.add(payment)
            db.session.commit()

            flash('繳款紀錄已建立', 'success')
            return redirect(url_for('verify.index'))

    return render_template('verify/create_payment.html',
                          operator=operator,
                          summary=summary)


@verify_bp.route('/payments')
def payment_list():
    """List all payment records"""
    payments = PaymentRecord.query.order_by(PaymentRecord.received_at.desc()).all()
    return render_template('verify/payment_list.html', payments=payments)
