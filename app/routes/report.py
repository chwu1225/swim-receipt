"""
Report Routes - Daily/Monthly reports (Demo Mode)
"""
from flask import Blueprint, render_template, request, Response
from app.services.report_service import ReportService
from app.services.pdf_service import ReceiptPDFService
from app.services.number_chinese import amount_to_chinese
from datetime import date
from io import BytesIO

report_bp = Blueprint('report', __name__)


@report_bp.route('/daily')
def daily():
    """Daily report page"""
    target_date_str = request.args.get('date')
    operator_id = request.args.get('operator_id', type=int)

    if target_date_str:
        try:
            target_date = date.fromisoformat(target_date_str)
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    report_data = ReportService.get_daily_report(
        target_date=target_date,
        operator_id=operator_id
    )

    return render_template('report/daily.html', report=report_data)


@report_bp.route('/monthly')
def monthly():
    """Monthly report page"""
    year = request.args.get('year', type=int) or date.today().year
    month = request.args.get('month', type=int) or date.today().month
    operator_id = request.args.get('operator_id', type=int)

    report_data = ReportService.get_monthly_report(
        year=year,
        month=month,
        operator_id=operator_id
    )

    # Add Chinese amount
    report_data['summary']['net_total_chinese'] = amount_to_chinese(
        report_data['summary']['net_total']
    )

    return render_template('report/monthly.html', report=report_data)


@report_bp.route('/monthly/print')
def monthly_print():
    """Monthly report print view"""
    year = request.args.get('year', type=int) or date.today().year
    month = request.args.get('month', type=int) or date.today().month
    operator_id = request.args.get('operator_id', type=int)

    report_data = ReportService.get_monthly_report(
        year=year,
        month=month,
        operator_id=operator_id
    )

    report_data['summary']['net_total_chinese'] = amount_to_chinese(
        report_data['summary']['net_total']
    )

    return render_template('report/monthly_print.html', report=report_data)


@report_bp.route('/export/excel')
def export_excel():
    """Export receipts to Excel"""
    year = request.args.get('year', type=int) or date.today().year
    month = request.args.get('month', type=int) or date.today().month
    operator_id = request.args.get('operator_id', type=int)

    report_data = ReportService.get_monthly_report(year, month, operator_id)
    receipts = report_data['receipts']

    # Prepare Excel data
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, Border, Side

        wb = Workbook()
        ws = wb.active
        ws.title = f'{year}{month:02d}月報表'

        # Header
        headers = ['收據編號', '日期時間', '收費項目', '金額', '備註', '狀態', '經辦員', '驗證狀態']
        ws.append(headers)

        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # Data rows
        for r in receipts:
            ws.append([
                r.receipt_no,
                r.created_at.strftime('%Y/%m/%d %H:%M:%S') if r.created_at else '',
                r.item_name,
                float(r.amount),
                r.remark or '',
                r.status_display,
                r.operator_name,
                '已驗證' if r.is_verified else '未驗證'
            ])

        # Summary
        ws.append([])
        ws.append(['合計', '', '', float(report_data['summary']['net_total'])])

        # Auto-fit column width
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[column_letter].width = max_length + 2

        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = f'swim_report_{year}{month:02d}.xlsx'
        return Response(
            buffer.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )

    except ImportError:
        return '缺少 openpyxl 套件，無法匯出 Excel', 500
