"""
Void Management Routes - Request and approve void (Demo Mode)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Receipt, VoidRequest
from app.services.receipt_service import ReceiptService

void_bp = Blueprint('void', __name__)


def get_current_user():
    """Get demo user"""
    from app import DemoUser
    return DemoUser()


@void_bp.route('/')
def index():
    """Void management main page"""
    current_user = get_current_user()

    # Get pending requests
    pending_requests = VoidRequest.get_pending_requests()

    # Get recent requests
    my_requests = VoidRequest.query.order_by(
        VoidRequest.requested_at.desc()
    ).limit(20).all()

    return render_template('void/index.html',
                          pending_requests=pending_requests,
                          my_requests=my_requests)


@void_bp.route('/request/<int:receipt_id>', methods=['GET', 'POST'])
def request_void(receipt_id):
    """Request to void a receipt"""
    current_user = get_current_user()
    receipt = Receipt.query.get_or_404(receipt_id)

    if not receipt.can_void:
        if receipt.is_verified:
            flash('已驗證的收據不可作廢', 'error')
        else:
            flash('此收據無法作廢', 'error')
        return redirect(url_for('receipt.view', receipt_id=receipt_id))

    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()

        if not reason:
            flash('請輸入作廢原因', 'error')
        else:
            try:
                void_request = ReceiptService.request_void(
                    receipt_id=receipt_id,
                    reason=reason,
                    requester=current_user
                )
                flash('作廢申請已送出，等待審核', 'success')
                return redirect(url_for('void.index'))
            except ValueError as e:
                flash(str(e), 'error')

    return render_template('void/request.html', receipt=receipt)


@void_bp.route('/review/<int:request_id>', methods=['GET', 'POST'])
def review(request_id):
    """Review a void request"""
    current_user = get_current_user()
    void_request = VoidRequest.query.get_or_404(request_id)

    if void_request.status != VoidRequest.STATUS_PENDING:
        flash('此申請已經處理過', 'error')
        return redirect(url_for('void.index'))

    if request.method == 'POST':
        action = request.form.get('action')
        note = request.form.get('note', '').strip()

        try:
            if action == 'approve':
                ReceiptService.approve_void(
                    request_id=request_id,
                    reviewer=current_user,
                    note=note if note else None
                )
                flash('作廢申請已核准', 'success')
            elif action == 'reject':
                ReceiptService.reject_void(
                    request_id=request_id,
                    reviewer=current_user,
                    note=note if note else None
                )
                flash('作廢申請已駁回', 'info')
            else:
                flash('無效的操作', 'error')
                return redirect(url_for('void.review', request_id=request_id))

            return redirect(url_for('void.index'))

        except ValueError as e:
            flash(str(e), 'error')

    return render_template('void/review.html', void_request=void_request)


@void_bp.route('/history')
def history():
    """View void request history"""
    page = request.args.get('page', 1, type=int)

    requests = VoidRequest.query.order_by(
        VoidRequest.requested_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)

    return render_template('void/history.html', requests=requests)
