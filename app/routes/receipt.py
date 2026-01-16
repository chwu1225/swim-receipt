"""
Receipt Routes - Create, view, print receipts (Demo Mode)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, g
from app.models import Receipt, FeeItem
from app.services.receipt_service import ReceiptService
from app.services.pdf_service import ReceiptPDFService
from decimal import Decimal

receipt_bp = Blueprint('receipt', __name__)


def get_current_user():
    """Get demo user"""
    from app import DemoUser
    return DemoUser()


@receipt_bp.route('/')
def index():
    """Receipt list page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Receipt.query
    receipts = query.order_by(Receipt.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('receipt/list.html', receipts=receipts)


@receipt_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new receipt"""
    fee_items = FeeItem.get_active_items()
    current_user = get_current_user()

    if request.method == 'POST':
        item_id = request.form.get('item_id', type=int)
        amount = request.form.get('amount', type=float)
        remark = request.form.get('remark', '').strip()

        if not item_id:
            flash('請選擇收費項目', 'error')
        elif not amount or amount <= 0:
            flash('請輸入有效金額', 'error')
        else:
            try:
                receipt = ReceiptService.create_receipt(
                    item_id=item_id,
                    amount=Decimal(str(amount)),
                    operator=current_user,
                    remark=remark if remark else None
                )
                flash(f'收據 {receipt.receipt_no} 已成功開立', 'success')
                return redirect(url_for('receipt.print_receipt', receipt_id=receipt.id))
            except ValueError as e:
                flash(str(e), 'error')

    return render_template('receipt/create.html', fee_items=fee_items)


@receipt_bp.route('/<int:receipt_id>')
def view(receipt_id):
    """View receipt details"""
    receipt = Receipt.query.get_or_404(receipt_id)
    return render_template('receipt/view.html', receipt=receipt)


@receipt_bp.route('/<int:receipt_id>/print')
def print_receipt(receipt_id):
    """Print receipt page"""
    receipt = Receipt.query.get_or_404(receipt_id)
    return render_template('receipt/print.html', receipt=receipt)


@receipt_bp.route('/<int:receipt_id>/pdf')
def download_pdf(receipt_id):
    """Download receipt as PDF"""
    receipt = Receipt.query.get_or_404(receipt_id)

    pdf_service = ReceiptPDFService()
    pdf_buffer = pdf_service.generate(receipt)

    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename=receipt_{receipt.receipt_no}.pdf'
        }
    )


@receipt_bp.route('/search')
def search():
    """Search receipts"""
    receipt_no = request.args.get('receipt_no', '').strip()

    if receipt_no:
        receipt = ReceiptService.get_receipt_by_no(receipt_no)
        if receipt:
            return redirect(url_for('receipt.view', receipt_id=receipt.id))
        else:
            flash(f'找不到收據編號: {receipt_no}', 'error')

    return redirect(url_for('receipt.index'))


@receipt_bp.route('/api/fee-item/<int:item_id>')
def get_fee_item(item_id):
    """API: Get fee item details"""
    item = FeeItem.query.get_or_404(item_id)
    return {
        'id': item.id,
        'item_code': item.item_code,
        'item_name': item.item_name,
        'default_price': float(item.default_price),
        'description': item.description
    }
