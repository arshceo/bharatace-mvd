"""
AI Agent Tools Package
Contains all tools that the AI agent can use to answer questions and perform actions.
"""

from .knowledge_tool import search_general_knowledge
from .attendance_tool import get_student_attendance, calculate_attendance_percentage
from .marks_tool import get_student_marks, calculate_cgpa, calculate_sgpa
from .fees_tool import get_student_fee_status, get_fee_history
from .timetable_tool import get_full_timetable, get_student_timetable
from .library_tool import search_books, get_student_book_loans, reserve_library_book
from .events_tool import get_upcoming_events, register_for_event

__all__ = [
    'search_general_knowledge',
    'get_student_attendance',
    'calculate_attendance_percentage',
    'get_student_marks',
    'calculate_cgpa',
    'calculate_sgpa',
    'get_student_fee_status',
    'get_fee_history',
    'get_full_timetable',
    'get_student_timetable',
    'search_books',
    'get_student_book_loans',
    'reserve_library_book',
    'get_upcoming_events',
    'register_for_event',
]
