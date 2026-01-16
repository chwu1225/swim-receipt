"""
Report Service - Generate reports and statistics
"""
from app import db
from app.models import Receipt, FeeItem
from sqlalchemy import func, and_
from datetime import date, datetime
from calendar import monthrange
from decimal import Decimal


class ReportService:
    """Service for generating reports"""

    @staticmethod
    def get_daily_report(target_date=None, operator_id=None):
        """
        Get daily report data

        Args:
            target_date: Date to report (default: today)
            operator_id: Filter by operator (optional)

        Returns:
            dict with receipts and summary
        """
        if target_date is None:
            target_date = date.today()

        query = Receipt.query.filter(
            func.date(Receipt.created_at) == target_date
        )

        if operator_id:
            query = query.filter_by(operator_id=operator_id)

        receipts = query.order_by(Receipt.created_at.desc()).all()

        # Calculate summary
        active_receipts = [r for r in receipts if r.status == Receipt.STATUS_ACTIVE]
        voided_receipts = [r for r in receipts if r.status == Receipt.STATUS_VOIDED]

        active_total = sum(r.amount for r in active_receipts)
        voided_total = sum(r.amount for r in voided_receipts)

        return {
            'date': target_date,
            'receipts': receipts,
            'summary': {
                'active_count': len(active_receipts),
                'active_total': active_total,
                'voided_count': len(voided_receipts),
                'voided_total': voided_total,
                'net_total': active_total
            }
        }

    @staticmethod
    def get_monthly_report(year, month, operator_id=None):
        """
        Get monthly report data

        Args:
            year: Year
            month: Month (1-12)
            operator_id: Filter by operator (optional)

        Returns:
            dict with receipts, summary, and breakdown by item
        """
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        query = Receipt.query.filter(
            and_(
                func.date(Receipt.created_at) >= start_date,
                func.date(Receipt.created_at) <= end_date
            )
        )

        if operator_id:
            query = query.filter_by(operator_id=operator_id)

        receipts = query.order_by(Receipt.created_at.desc()).all()

        # Calculate summary
        active_receipts = [r for r in receipts if r.status == Receipt.STATUS_ACTIVE]
        voided_receipts = [r for r in receipts if r.status == Receipt.STATUS_VOIDED]

        active_total = sum(r.amount for r in active_receipts)
        voided_total = sum(r.amount for r in voided_receipts)

        # Breakdown by item
        item_breakdown = {}
        for receipt in active_receipts:
            if receipt.item_name not in item_breakdown:
                item_breakdown[receipt.item_name] = {
                    'count': 0,
                    'total': Decimal('0')
                }
            item_breakdown[receipt.item_name]['count'] += 1
            item_breakdown[receipt.item_name]['total'] += receipt.amount

        # Calculate percentages
        for item_name in item_breakdown:
            if active_total > 0:
                item_breakdown[item_name]['percentage'] = \
                    float(item_breakdown[item_name]['total']) / float(active_total) * 100
            else:
                item_breakdown[item_name]['percentage'] = 0

        return {
            'year': year,
            'month': month,
            'period_start': start_date,
            'period_end': end_date,
            'receipts': receipts,
            'summary': {
                'active_count': len(active_receipts),
                'active_total': active_total,
                'voided_count': len(voided_receipts),
                'voided_total': voided_total,
                'net_total': active_total
            },
            'item_breakdown': item_breakdown
        }

    @staticmethod
    def get_unverified_receipts(operator_id=None):
        """
        Get receipts that haven't been verified yet

        Args:
            operator_id: Filter by operator (optional)

        Returns:
            List of unverified receipts
        """
        query = Receipt.query.filter_by(
            status=Receipt.STATUS_ACTIVE,
            is_verified=False
        )

        if operator_id:
            query = query.filter_by(operator_id=operator_id)

        return query.order_by(Receipt.created_at.desc()).all()

    @staticmethod
    def get_verification_summary(operator_id=None, year=None, month=None):
        """
        Get summary for verification/payment

        Args:
            operator_id: Operator ID
            year: Year (default: current)
            month: Month (default: current)

        Returns:
            dict with verification summary
        """
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        query = Receipt.query.filter(
            and_(
                func.date(Receipt.created_at) >= start_date,
                func.date(Receipt.created_at) <= end_date,
                Receipt.status == Receipt.STATUS_ACTIVE
            )
        )

        if operator_id:
            query = query.filter_by(operator_id=operator_id)

        receipts = query.all()

        verified = [r for r in receipts if r.is_verified]
        unverified = [r for r in receipts if not r.is_verified]

        return {
            'period_start': start_date,
            'period_end': end_date,
            'total_count': len(receipts),
            'total_amount': sum(r.amount for r in receipts),
            'verified_count': len(verified),
            'verified_amount': sum(r.amount for r in verified),
            'unverified_count': len(unverified),
            'unverified_amount': sum(r.amount for r in unverified),
            'unverified_receipts': unverified
        }

    @staticmethod
    def export_to_excel_data(receipts):
        """
        Prepare receipt data for Excel export

        Args:
            receipts: List of Receipt objects

        Returns:
            List of dicts for Excel export
        """
        data = []
        for r in receipts:
            data.append({
                '\u6536\u64da\u7de8\u865f': r.receipt_no,
                '\u65e5\u671f\u6642\u9593': r.created_at.strftime('%Y/%m/%d %H:%M:%S') if r.created_at else '',
                '\u6536\u8cbb\u9805\u76ee': r.item_name,
                '\u91d1\u984d': float(r.amount),
                '\u5099\u8a3b': r.remark or '',
                '\u72c0\u614b': r.status_display,
                '\u7d93\u8fa6\u54e1': r.operator_name,
                '\u9a57\u8b49\u72c0\u614b': '\u5df2\u9a57\u8b49' if r.is_verified else '\u672a\u9a57\u8b49'
            })
        return data
