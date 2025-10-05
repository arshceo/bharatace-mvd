"""
Fees Tool
Retrieves and manages student fee information.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, date
from database import get_supabase_admin

logger = logging.getLogger(__name__)


def get_student_fee_status(student_id: str, semester: Optional[int] = None) -> Dict[str, Any]:
    """
    Get fee payment status for a student.
    
    Args:
        student_id: The student's database ID (UUID)
        semester: Optional semester number to filter
        
    Returns:
        Dictionary containing fee records and payment status
    """
    try:
        supabase = get_supabase_admin()
        
        # Build query
        query = supabase.table("fees")\
            .select("*")\
            .eq("student_id", student_id)\
            .order("semester", desc=True)
        
        if semester:
            query = query.eq("semester", semester)
        
        response = query.execute()
        
        if not response.data:
            return {
                "records": [],
                "summary": {
                    "total_due": 0.0,
                    "total_paid": 0.0,
                    "balance": 0.0,
                    "overdue_amount": 0.0
                },
                "message": "No fee records found",
                "success": True
            }
        
        records = response.data
        
        # Calculate summary
        total_due = sum(float(r['total_amount']) for r in records)
        total_paid = sum(float(r['amount_paid']) for r in records)
        balance = total_due - total_paid
        
        # Calculate overdue amount
        today = date.today()
        overdue_amount = 0.0
        overdue_fees = []
        
        for record in records:
            if record['payment_status'] in ['pending', 'partial', 'overdue']:
                due_date = datetime.fromisoformat(record['due_date']).date()
                if due_date < today:
                    outstanding = float(record['total_amount']) - float(record['amount_paid'])
                    overdue_amount += outstanding
                    overdue_fees.append({
                        "semester": record['semester'],
                        "academic_year": record['academic_year'],
                        "amount": outstanding,
                        "due_date": record['due_date'],
                        "days_overdue": (today - due_date).days
                    })
        
        logger.info(f"Retrieved fee status for student {student_id}: Balance ₹{balance:.2f}")
        
        return {
            "records": records,
            "summary": {
                "total_due": round(total_due, 2),
                "total_paid": round(total_paid, 2),
                "balance": round(balance, 2),
                "overdue_amount": round(overdue_amount, 2),
                "payment_percentage": round((total_paid / total_due * 100) if total_due > 0 else 100.0, 2)
            },
            "overdue_fees": overdue_fees,
            "has_overdue": len(overdue_fees) > 0,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting fee status: {str(e)}")
        return {
            "records": [],
            "summary": {},
            "success": False,
            "error": str(e)
        }


def get_fee_history(student_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get payment transaction history for a student.
    
    Args:
        student_id: The student's database ID
        limit: Maximum number of transactions to return
        
    Returns:
        Dictionary containing payment history
    """
    try:
        supabase = get_supabase_admin()
        
        response = supabase.table("fee_transactions")\
            .select("*, fees(semester, academic_year, total_amount)")\
            .eq("student_id", student_id)\
            .order("transaction_date", desc=True)\
            .limit(limit)\
            .execute()
        
        if not response.data:
            return {
                "transactions": [],
                "total_paid": 0.0,
                "message": "No payment history found",
                "success": True
            }
        
        transactions = response.data
        total_paid = sum(float(t['amount']) for t in transactions if t['payment_status'] == 'success')
        
        logger.info(f"Retrieved {len(transactions)} payment transactions for student {student_id}")
        
        return {
            "transactions": transactions,
            "total_paid": round(total_paid, 2),
            "transaction_count": len(transactions),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting fee history: {str(e)}")
        return {
            "transactions": [],
            "success": False,
            "error": str(e)
        }


def calculate_late_fee(student_id: str, fee_id: str) -> Dict[str, Any]:
    """
    Calculate late fee for an overdue payment.
    
    Args:
        student_id: The student's database ID
        fee_id: The fee record ID
        
    Returns:
        Dictionary with late fee calculation
    """
    try:
        supabase = get_supabase_admin()
        
        response = supabase.table("fees")\
            .select("*")\
            .eq("id", fee_id)\
            .eq("student_id", student_id)\
            .execute()
        
        if not response.data:
            return {
                "late_fee": 0.0,
                "success": False,
                "message": "Fee record not found"
            }
        
        fee_record = response.data[0]
        due_date = datetime.fromisoformat(fee_record['due_date']).date()
        today = date.today()
        
        if today <= due_date:
            return {
                "late_fee": 0.0,
                "days_overdue": 0,
                "message": "Payment not yet overdue",
                "success": True
            }
        
        days_overdue = (today - due_date).days
        outstanding = float(fee_record['total_amount']) - float(fee_record['amount_paid'])
        
        # Late fee calculation: ₹100 per day for first 7 days, then ₹200 per day
        if days_overdue <= 7:
            late_fee = days_overdue * 100
        else:
            late_fee = (7 * 100) + ((days_overdue - 7) * 200)
        
        # Cap late fee at 20% of outstanding amount
        max_late_fee = outstanding * 0.20
        late_fee = min(late_fee, max_late_fee)
        
        return {
            "late_fee": round(late_fee, 2),
            "days_overdue": days_overdue,
            "outstanding_amount": round(outstanding, 2),
            "total_payable": round(outstanding + late_fee, 2),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error calculating late fee: {str(e)}")
        return {
            "late_fee": 0.0,
            "success": False,
            "error": str(e)
        }


def get_semester_fee_breakdown(student_id: str, semester: int) -> Dict[str, Any]:
    """
    Get detailed fee breakdown for a specific semester.
    
    Args:
        student_id: The student's database ID
        semester: Semester number
        
    Returns:
        Dictionary with detailed fee breakdown
    """
    try:
        supabase = get_supabase_admin()
        
        # Get fee record for the semester
        fee_response = supabase.table("fees")\
            .select("*")\
            .eq("student_id", student_id)\
            .eq("semester", semester)\
            .execute()
        
        if not fee_response.data:
            return {
                "breakdown": {},
                "success": False,
                "message": f"No fee record found for semester {semester}"
            }
        
        fee_record = fee_response.data[0]
        
        # Get payment transactions for this fee
        transactions_response = supabase.table("fee_transactions")\
            .select("*")\
            .eq("fee_id", fee_record['id'])\
            .order("transaction_date", desc=True)\
            .execute()
        
        # Standard fee breakdown (you can customize this based on your institution)
        total_amount = float(fee_record['total_amount'])
        breakdown = {
            "tuition_fee": round(total_amount * 0.60, 2),
            "library_fee": round(total_amount * 0.10, 2),
            "lab_fee": round(total_amount * 0.15, 2),
            "sports_fee": round(total_amount * 0.05, 2),
            "development_fee": round(total_amount * 0.10, 2)
        }
        
        return {
            "semester": semester,
            "academic_year": fee_record['academic_year'],
            "breakdown": breakdown,
            "total_amount": round(total_amount, 2),
            "amount_paid": round(float(fee_record['amount_paid']), 2),
            "balance": round(total_amount - float(fee_record['amount_paid']), 2),
            "payment_status": fee_record['payment_status'],
            "due_date": fee_record['due_date'],
            "transactions": transactions_response.data,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting fee breakdown: {str(e)}")
        return {
            "breakdown": {},
            "success": False,
            "error": str(e)
        }


def check_fee_clearance(student_id: str) -> Dict[str, Any]:
    """
    Check if student has cleared all fees (for exam eligibility, etc.).
    
    Args:
        student_id: The student's database ID
        
    Returns:
        Dictionary with clearance status
    """
    try:
        fee_status = get_student_fee_status(student_id)
        
        if not fee_status['success']:
            return fee_status
        
        balance = fee_status['summary']['balance']
        has_overdue = fee_status['has_overdue']
        
        is_cleared = balance == 0.0 and not has_overdue
        
        return {
            "is_cleared": is_cleared,
            "balance": balance,
            "has_overdue": has_overdue,
            "overdue_amount": fee_status['summary']['overdue_amount'],
            "message": "All fees cleared" if is_cleared else f"Outstanding balance: ₹{balance:.2f}",
            "eligible_for_exam": is_cleared or balance < 1000.0,  # Allow small balance
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error checking fee clearance: {str(e)}")
        return {
            "is_cleared": False,
            "success": False,
            "error": str(e)
        }

