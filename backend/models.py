"""
Pydantic models for API request and response validation.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


# ==================== ENUMS ====================

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class FeeStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"


class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"
    CHEQUE = "cheque"


class EventType(str, Enum):
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    COMPETITION = "competition"
    CULTURAL = "cultural"
    SPORTS = "sports"
    ACADEMIC = "academic"
    OTHER = "other"


class BookStatus(str, Enum):
    AVAILABLE = "available"
    ISSUED = "issued"
    RESERVED = "reserved"
    LOST = "lost"
    DAMAGED = "damaged"


# ==================== AUTH & USER MODELS ====================

class LoginRequest(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class SignupRequest(BaseModel):
    """Student signup request"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    roll_number: str
    semester: int = Field(..., ge=1, le=8)
    department: str
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# ==================== STUDENT MODELS ====================

class StudentBase(BaseModel):
    """Base student model"""
    roll_number: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    semester: int = Field(..., ge=1, le=8)
    department: str
    admission_year: int


class StudentCreate(StudentBase):
    """Create student"""
    password: str = Field(..., min_length=6)


class Student(StudentBase):
    """Complete student model"""
    id: uuid.UUID
    institution_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    cgpa: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ATTENDANCE MODELS ====================

class AttendanceRecord(BaseModel):
    """Single attendance record"""
    id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    date: date
    status: AttendanceStatus
    marked_by: uuid.UUID
    
    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    """Attendance summary for a student"""
    total_classes: int
    attended: int
    present: int
    late: int
    absent: int
    excused: int
    percentage: float
    subject_wise: Optional[List[Dict[str, Any]]] = None


# ==================== MARKS MODELS ====================

class MarksRecord(BaseModel):
    """Marks for an exam"""
    id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    semester: int
    exam_type: str  # mid_sem, end_sem, quiz, assignment
    marks_obtained: float
    max_marks: float
    exam_date: date
    
    class Config:
        from_attributes = True


class GPAResult(BaseModel):
    """GPA calculation result"""
    cgpa: Optional[float] = None
    sgpa: Optional[float] = None
    semester: Optional[int] = None
    total_credits: int
    semester_wise: Optional[List[Dict[str, Any]]] = None
    grade_distribution: Optional[Dict[str, int]] = None


# ==================== FEES MODELS ====================

class FeeRecord(BaseModel):
    """Fee record for a semester"""
    id: uuid.UUID
    student_id: uuid.UUID
    semester: int
    total_amount: float
    paid_amount: float
    due_date: date
    status: FeeStatus
    late_fee: float = 0.0
    
    class Config:
        from_attributes = True


class FeeTransactionCreate(BaseModel):
    """Create fee payment transaction"""
    fee_id: uuid.UUID
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    transaction_reference: Optional[str] = None


class FeeTransaction(FeeTransactionCreate):
    """Complete fee transaction"""
    id: uuid.UUID
    payment_date: datetime
    processed_by: uuid.UUID
    
    class Config:
        from_attributes = True


# ==================== EVENT MODELS ====================

class EventBase(BaseModel):
    """Base event model"""
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    event_type: EventType
    start_date: datetime
    end_date: Optional[datetime] = None
    location: str
    organizer: str
    max_participants: Optional[int] = None
    registration_deadline: Optional[datetime] = None


class EventCreate(EventBase):
    """Create event"""
    pass


class Event(EventBase):
    """Complete event model"""
    id: uuid.UUID
    institution_id: uuid.UUID
    event_status: str = "upcoming"
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventRegistration(BaseModel):
    """Event registration"""
    event_id: uuid.UUID


# ==================== LIBRARY MODELS ====================

class BookBase(BaseModel):
    """Base book model"""
    title: str = Field(..., min_length=1)
    author: str
    isbn: str
    category: str
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    total_copies: int = Field(..., ge=1)


class BookCreate(BookBase):
    """Create book"""
    pass


class Book(BookBase):
    """Complete book model"""
    id: uuid.UUID
    institution_id: uuid.UUID
    available_copies: int
    status: BookStatus
    
    class Config:
        from_attributes = True


class BookLoan(BaseModel):
    """Book loan record"""
    id: uuid.UUID
    book_id: uuid.UUID
    student_id: uuid.UUID
    issue_date: date
    due_date: date
    return_date: Optional[date] = None
    fine_amount: float = 0.0
    fine_paid: bool = False
    
    class Config:
        from_attributes = True


class BookReservation(BaseModel):
    """Reserve a book"""
    book_title: str = Field(..., min_length=1, description="Exact or partial book title")


# ==================== TIMETABLE MODELS ====================

class TimetableEntry(BaseModel):
    """Single timetable entry"""
    id: uuid.UUID
    semester: int
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Sunday
    start_time: str  # HH:MM format
    end_time: str
    subject_id: uuid.UUID
    room_number: str
    faculty_name: str
    
    class Config:
        from_attributes = True


# ==================== KNOWLEDGE BASE MODELS ====================

class KnowledgeItemCreate(BaseModel):
    """
    Model for creating a new knowledge base entry.
    """
    content: str = Field(..., description="The content to be added to the knowledge base", min_length=1)
    category: str = Field(..., description="Category of the content (e.g., 'admission', 'courses', 'facilities')", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "The university offers undergraduate programs in Computer Science, Electronics, and Mechanical Engineering.",
                "category": "courses"
            }
        }


class KnowledgeItem(BaseModel):
    """
    Model representing a complete knowledge base item with metadata.
    """
    id: uuid.UUID = Field(..., description="Unique identifier for the knowledge item")
    content: str = Field(..., description="The content of the knowledge item")
    category: str = Field(..., description="Category of the content")
    created_at: datetime = Field(..., description="Timestamp when the item was created")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "content": "The university offers undergraduate programs in Computer Science.",
                "category": "courses",
                "created_at": "2025-10-05T10:30:00Z"
            }
        }


class Question(BaseModel):
    """
    Model for chatbot questions with optional conversation history.
    """
    query: str = Field(..., description="The question to ask the AI assistant", min_length=1)
    conversation_history: Optional[List[dict]] = Field(None, description="Previous conversation messages for context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What undergraduate programs does the university offer?",
                "conversation_history": [
                    {"role": "user", "content": "Tell me about your university"},
                    {"role": "assistant", "content": "BharatAce is a leading institution..."}
                ]
            }
        }


class Answer(BaseModel):
    """
    Model for chatbot responses.
    """
    response: str = Field(..., description="The AI-generated answer to the question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "The university offers undergraduate programs in Computer Science, Electronics, and Mechanical Engineering."
            }
        }


class ErrorResponse(BaseModel):
    """
    Model for error responses.
    """
    detail: str = Field(..., description="Error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "An error occurred while processing your request"
            }
        }
