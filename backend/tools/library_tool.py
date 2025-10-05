"""
Library Tool
Manages library books, searches, loans, and reservations.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta, date
from database import get_supabase_admin
import uuid

logger = logging.getLogger(__name__)


def search_books(
    query: str,
    category: Optional[str] = None,
    available_only: bool = False
) -> Dict[str, Any]:
    """
    Search for books in the library.
    
    Args:
        query: Search query (searches in title, author, ISBN)
        category: Optional category filter
        available_only: If True, only return available books
        
    Returns:
        Dictionary containing search results
    """
    try:
        supabase = get_supabase_admin()
        
        # Build search query
        search_query = supabase.table("library_books").select("*")
        
        # Search in title, author, or ISBN
        if query:
            search_query = search_query.or_(
                f"title.ilike.%{query}%,author.ilike.%{query}%,isbn.ilike.%{query}%"
            )
        
        if category:
            search_query = search_query.eq("category", category)
        
        if available_only:
            search_query = search_query.gt("available_copies", 0)
        
        response = search_query.limit(20).execute()
        
        books = response.data
        
        logger.info(f"Found {len(books)} books matching query: {query}")
        
        return {
            "books": books,
            "total_results": len(books),
            "query": query,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error searching books: {str(e)}")
        return {
            "books": [],
            "success": False,
            "error": str(e)
        }


def get_book_details(book_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific book.
    
    Args:
        book_id: The book's database ID
        
    Returns:
        Dictionary with book details and availability
    """
    try:
        supabase = get_supabase_admin()
        
        response = supabase.table("library_books")\
            .select("*")\
            .eq("id", book_id)\
            .execute()
        
        if not response.data:
            return {
                "book": None,
                "success": False,
                "message": "Book not found"
            }
        
        book = response.data[0]
        
        # Get active loans for this book
        loans_response = supabase.table("book_loans")\
            .select("*, students(first_name, last_name, student_id)")\
            .eq("book_id", book_id)\
            .eq("loan_status", "active")\
            .execute()
        
        return {
            "book": book,
            "is_available": book['available_copies'] > 0,
            "active_loans": loans_response.data,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting book details: {str(e)}")
        return {
            "book": None,
            "success": False,
            "error": str(e)
        }


def get_student_book_loans(student_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all book loans for a student.
    
    Args:
        student_id: The student's database ID
        status: Optional status filter ('active', 'returned', 'overdue', 'lost')
        
    Returns:
        Dictionary containing loan records
    """
    try:
        supabase = get_supabase_admin()
        
        query = supabase.table("book_loans")\
            .select("*, library_books(title, author, isbn)")\
            .eq("student_id", student_id)\
            .order("issue_date", desc=True)
        
        if status:
            query = query.eq("loan_status", status)
        
        response = query.execute()
        
        loans = response.data
        
        # Calculate statistics
        active_loans = [l for l in loans if l['loan_status'] == 'active']
        overdue_loans = [l for l in loans if l['loan_status'] == 'overdue']
        total_fines = sum(float(l['fine_amount']) for l in loans)
        
        logger.info(f"Retrieved {len(loans)} book loans for student {student_id}")
        
        return {
            "loans": loans,
            "statistics": {
                "total_loans": len(loans),
                "active_loans": len(active_loans),
                "overdue_loans": len(overdue_loans),
                "total_fines": round(total_fines, 2)
            },
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting book loans: {str(e)}")
        return {
            "loans": [],
            "success": False,
            "error": str(e)
        }


def reserve_library_book(student_id: str, book_title: str) -> Dict[str, Any]:
    """
    Reserve/issue a library book to a student.
    
    This is an ACTION tool - it writes data, not just reads.
    
    Args:
        student_id: The student's database ID
        book_title: Title of the book to reserve
        
    Returns:
        Dictionary with reservation confirmation
    """
    try:
        supabase = get_supabase_admin()
        
        # Search for the book
        book_response = supabase.table("library_books")\
            .select("*")\
            .ilike("title", f"%{book_title}%")\
            .execute()
        
        if not book_response.data:
            return {
                "success": False,
                "message": f"Book not found: {book_title}"
            }
        
        book = book_response.data[0]
        
        # Check if book is available
        if book['available_copies'] <= 0:
            return {
                "success": False,
                "message": f"Book '{book['title']}' is currently not available. All copies are issued."
            }
        
        # Check if student already has this book
        existing_loan = supabase.table("book_loans")\
            .select("*")\
            .eq("student_id", student_id)\
            .eq("book_id", book['id'])\
            .eq("loan_status", "active")\
            .execute()
        
        if existing_loan.data:
            return {
                "success": False,
                "message": f"You already have this book issued. Please return it before borrowing again."
            }
        
        # Check student's current active loans (limit to 3 books)
        active_loans = supabase.table("book_loans")\
            .select("*")\
            .eq("student_id", student_id)\
            .eq("loan_status", "active")\
            .execute()
        
        if len(active_loans.data) >= 3:
            return {
                "success": False,
                "message": "You have reached the maximum limit of 3 books. Please return a book before issuing another."
            }
        
        # Check for overdue books or unpaid fines
        overdue_check = supabase.table("book_loans")\
            .select("*")\
            .eq("student_id", student_id)\
            .or_("loan_status.eq.overdue,fine_amount.gt.0")\
            .execute()
        
        if overdue_check.data:
            total_fine = sum(float(l['fine_amount']) for l in overdue_check.data)
            return {
                "success": False,
                "message": f"Cannot issue new books. You have overdue books or pending fines of ₹{total_fine:.2f}. Please clear them first."
            }
        
        # Create the loan record
        due_date = (date.today() + timedelta(days=14)).isoformat()  # 14-day loan period
        
        loan_data = {
            "id": str(uuid.uuid4()),
            "student_id": student_id,
            "book_id": book['id'],
            "issue_date": datetime.now().isoformat(),
            "due_date": due_date,
            "loan_status": "active",
            "fine_amount": 0.0
        }
        
        loan_response = supabase.table("book_loans").insert(loan_data).execute()
        
        if not loan_response.data:
            return {
                "success": False,
                "message": "Failed to create loan record"
            }
        
        logger.info(f"Book '{book['title']}' issued to student {student_id}")
        
        return {
            "success": True,
            "message": f"Book '{book['title']}' has been successfully issued!",
            "loan_details": {
                "book_title": book['title'],
                "author": book['author'],
                "isbn": book['isbn'],
                "issue_date": loan_data['issue_date'],
                "due_date": due_date,
                "loan_period_days": 14
            }
        }
        
    except Exception as e:
        logger.error(f"Error reserving book: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def return_book(student_id: str, book_id: str) -> Dict[str, Any]:
    """
    Return a borrowed book.
    
    Args:
        student_id: The student's database ID
        book_id: The book's database ID
        
    Returns:
        Dictionary with return confirmation and fine (if any)
    """
    try:
        supabase = get_supabase_admin()
        
        # Find the active loan
        loan_response = supabase.table("book_loans")\
            .select("*")\
            .eq("student_id", student_id)\
            .eq("book_id", book_id)\
            .eq("loan_status", "active")\
            .execute()
        
        if not loan_response.data:
            return {
                "success": False,
                "message": "No active loan found for this book"
            }
        
        loan = loan_response.data[0]
        
        # Calculate fine if overdue
        due_date = datetime.fromisoformat(loan['due_date']).date()
        today = date.today()
        fine = 0.0
        
        if today > due_date:
            days_overdue = (today - due_date).days
            fine = days_overdue * 5.0  # ₹5 per day
        
        # Update loan record
        update_data = {
            "loan_status": "returned",
            "return_date": datetime.now().isoformat(),
            "fine_amount": fine
        }
        
        supabase.table("book_loans")\
            .update(update_data)\
            .eq("id", loan['id'])\
            .execute()
        
        logger.info(f"Book {book_id} returned by student {student_id}")
        
        return {
            "success": True,
            "message": "Book returned successfully!",
            "fine": round(fine, 2),
            "days_overdue": max(0, (today - due_date).days) if today > due_date else 0
        }
        
    except Exception as e:
        logger.error(f"Error returning book: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_popular_books(limit: int = 10) -> Dict[str, Any]:
    """
    Get most popular books based on loan history.
    
    Args:
        limit: Number of books to return
        
    Returns:
        Dictionary with popular books list
    """
    try:
        supabase = get_supabase_admin()
        
        # This is a simplified version - in production, you'd use a proper aggregation query
        loans_response = supabase.table("book_loans")\
            .select("book_id, library_books(title, author, category)")\
            .execute()
        
        # Count loans per book
        book_counts = {}
        for loan in loans_response.data:
            book_id = loan['book_id']
            if book_id not in book_counts:
                book_counts[book_id] = {
                    "count": 0,
                    "book_info": loan['library_books']
                }
            book_counts[book_id]["count"] += 1
        
        # Sort by count
        popular = sorted(
            book_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:limit]
        
        return {
            "popular_books": popular,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting popular books: {str(e)}")
        return {
            "popular_books": [],
            "success": False,
            "error": str(e)
        }

