"""
BharatAce - Super Smart AI Campus Assistant Backend

PRODUCTION VERSION with ReAct AI Agent, Multi-Tool Support, and Authentication.

Features:
- Multi-tool AI Agent with 7 specialized tools
- Authenticated student data access
- Personalized responses based on student context
- General knowledge retrieval via RAG
- Action tools (book reservation, event registration)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
import uuid
from datetime import datetime

# Local imports
from models import (
    KnowledgeItemCreate,
    KnowledgeItem,
    Question,
    Answer,
    ErrorResponse,
    LoginRequest,
    TokenResponse
)
from database import get_supabase, KNOWLEDGE_BASE_TABLE
from settings import settings
from auth import get_current_user, AuthUser, OptionalAuth

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Document, Settings as LlamaSettings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.agent import FunctionAgent
from llama_index.core.tools import FunctionTool

# Smart Agent import
from smart_agent import SuperSmartAgent

# Tool imports
from tools.knowledge_tool import search_general_knowledge, search_knowledge_by_category
from tools.attendance_tool import (
    get_student_attendance,
    calculate_attendance_percentage,
    get_attendance_by_date_range,
    check_attendance_shortage
)
from tools.marks_tool import (
    get_student_marks,
    calculate_cgpa,
    calculate_sgpa,
    get_rank_in_class
)
from tools.fees_tool import (
    get_student_fee_status,
    get_fee_history,
    calculate_late_fee,
    check_fee_clearance
)
from tools.timetable_tool import (
    get_full_timetable,
    get_student_timetable,
    get_timetable_for_day,
    get_next_class,
    find_free_slots
)
from tools.library_tool import (
    search_books,
    get_book_details,
    get_student_book_loans,
    reserve_library_book,
    get_popular_books
)
from tools.events_tool import (
    get_upcoming_events,
    get_event_details,
    register_for_event,
    get_student_events,
    search_events
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for LlamaIndex components
agent = None
index = None
llm = None  # Global LLM instance


def initialize_llama_index():
    """
    Initialize LlamaIndex AI Agent with RAG and specialized tools.
    
    Architecture:
    1. Load knowledge base documents for RAG
    2. Create VectorStoreIndex for general knowledge
    3. Wrap all tools with FunctionTool
    4. Create ReActAgent with tools and LLM
    
    The agent can:
    - Search general knowledge (RAG pipeline)
    - Access student-specific data (attendance, marks, fees, etc.)
    - Perform actions (reserve books, register for events)
    - Reason about complex multi-step queries
    """
    global agent, index, llm
    
    try:
        logger.info("=" * 80)
        logger.info("🚀 INITIALIZING AI AGENT SYSTEM")
        logger.info("=" * 80)
        
        # ============================================================
        # STEP 1: Load documents for RAG
        # ============================================================
        logger.info("📚 STEP 1: Loading knowledge base documents...")
        supabase = get_supabase()
        response = supabase.table(KNOWLEDGE_BASE_TABLE).select("*").execute()
        
        documents = []
        if response.data:
            logger.info(f"✅ Found {len(response.data)} documents in knowledge_base")
            
            for idx, item in enumerate(response.data):
                doc = Document(
                    text=item['content'],
                    metadata={
                        'id': str(item['id']),
                        'category': item['category'],
                        'created_at': str(item['created_at'])
                    },
                    doc_id=str(item['id'])
                )
                documents.append(doc)
            
            logger.info(f"✅ Loaded {len(documents)} documents")
        else:
            logger.warning("⚠️  No knowledge base documents found")
        
        # ============================================================
        # STEP 2: Configure LLM & Embeddings
        # ============================================================
        logger.info("🤖 STEP 2: Configuring Gemini LLM...")
        llm = Gemini(
            api_key=settings.GOOGLE_API_KEY,
            model_name="models/gemini-2.0-flash-lite",
            temperature=0.7
        )
        logger.info("✅ Gemini LLM configured successfully")
        
        # ============================================================
        # STEP 3: Configure Embedding Model - Google text-embedding-004
        # ============================================================
        logger.info("🔢 STEP 3: Setting up Gemini Embedding model...")
        embed_model = GeminiEmbedding(
            api_key=settings.GOOGLE_API_KEY,
            model_name="models/text-embedding-004"
        )
        logger.info("✅ Gemini Embedding model configured successfully")
        
        # ============================================================
        # STEP 4: Set global LlamaIndex settings
        # ============================================================
        logger.info("⚙️  STEP 4: Configuring global LlamaIndex settings...")
        LlamaSettings.llm = llm
        LlamaSettings.embed_model = embed_model
        LlamaSettings.chunk_size = 512
        LlamaSettings.chunk_overlap = 50
        logger.info("✅ Global settings configured (chunk_size=512, overlap=50)")
        
        # ============================================================
        # STEP 5: Build VectorStoreIndex from documents
        # ============================================================
        logger.info("🏗️  STEP 5: Building VectorStoreIndex from documents...")
        
        if documents:
            logger.info(f"   📊 Processing {len(documents)} documents...")
            logger.info("   🔄 Generating embeddings and building index...")
            
            index = VectorStoreIndex.from_documents(
                documents,
                show_progress=True
            )
            
            logger.info(f"✅ VectorStoreIndex built with {len(documents)} documents!")
        else:
            logger.warning("⚠️  No documents to index - creating empty index")
            index = VectorStoreIndex.from_documents([])
        
        # ============================================================
        # STEP 6: Wrap all tools with FunctionTool
        # ============================================================
        logger.info("🛠️  STEP 6: Wrapping AI tools...")
        
        # Knowledge tools
        knowledge_search_tool = FunctionTool.from_defaults(
            fn=lambda query: search_general_knowledge(query, index),
            name="search_general_knowledge",
            description="Search the college knowledge base for general information about admissions, courses, facilities, etc. Use this for NON-student-specific questions."
        )
        
        # Attendance tools
        attendance_tool = FunctionTool.from_defaults(
            fn=get_student_attendance,
            name="get_student_attendance",
            description="Get detailed attendance records for a student. Returns total classes, present, absent, late, and percentage. Requires student_id."
        )
        
        attendance_shortage_tool = FunctionTool.from_defaults(
            fn=check_attendance_shortage,
            name="check_attendance_shortage",
            description="Check if student has attendance shortage and calculate classes needed to meet required percentage (default 75%). Requires student_id."
        )
        
        # Marks & CGPA tools
        marks_tool = FunctionTool.from_defaults(
            fn=get_student_marks,
            name="get_student_marks",
            description="Get student's exam marks with subject-wise breakdown. Returns marks for all exams (mid-sem, end-sem, quiz). Requires student_id."
        )
        
        cgpa_tool = FunctionTool.from_defaults(
            fn=calculate_cgpa,
            name="calculate_cgpa",
            description="Calculate student's overall CGPA (10-point scale) and semester-wise GPA. Requires student_id."
        )
        
        rank_tool = FunctionTool.from_defaults(
            fn=get_rank_in_class,
            name="get_rank_in_class",
            description="Get student's rank and percentile in their class/semester. Requires student_id."
        )
        
        # Fees tools
        fees_tool = FunctionTool.from_defaults(
            fn=get_student_fee_status,
            name="get_student_fee_status",
            description="Get student's fee payment status including total, paid, pending, and late fees. Requires student_id."
        )
        
        fee_clearance_tool = FunctionTool.from_defaults(
            fn=check_fee_clearance,
            name="check_fee_clearance",
            description="Check if student is cleared for exams based on fee payment status. Requires student_id."
        )
        
        # Timetable tools
        timetable_tool = FunctionTool.from_defaults(
            fn=get_student_timetable,
            name="get_student_timetable",
            description="Get student's complete weekly timetable with all classes. Requires student_id."
        )
        
        next_class_tool = FunctionTool.from_defaults(
            fn=get_next_class,
            name="get_next_class",
            description="Find student's next upcoming class. Useful for 'What's my next class?' questions. Requires student_id."
        )
        
        # Library tools
        search_books_tool = FunctionTool.from_defaults(
            fn=search_books,
            name="search_books",
            description="Search library books by title, author, or category. Can filter by availability."
        )
        
        student_loans_tool = FunctionTool.from_defaults(
            fn=get_student_book_loans,
            name="get_student_book_loans",
            description="Get student's current and past library book loans with due dates and fines. Requires student_id."
        )
        
        reserve_book_tool = FunctionTool.from_defaults(
            fn=reserve_library_book,
            name="reserve_library_book",
            description="Reserve/issue a book for a student. This is an ACTION tool - it modifies data. Requires student_id and book_title."
        )
        
        # Event tools
        upcoming_events_tool = FunctionTool.from_defaults(
            fn=get_upcoming_events,
            name="get_upcoming_events",
            description="Get upcoming college events (workshops, seminars, competitions, etc.). Can filter by event type."
        )
        
        register_event_tool = FunctionTool.from_defaults(
            fn=register_for_event,
            name="register_for_event",
            description="Register a student for an event. This is an ACTION tool - it modifies data. Requires student_id and event_id."
        )
        
        student_events_tool = FunctionTool.from_defaults(
            fn=get_student_events,
            name="get_student_events",
            description="Get all events a student is registered for. Requires student_id."
        )
        
        logger.info("✅ Wrapped 17 AI tools successfully")
        
        # ============================================================
        # STEP 7: Create ReAct AI Agent
        # ============================================================
        logger.info("🤖 STEP 7: Creating ReAct AI Agent...")
        
        tools = [
            knowledge_search_tool,
            attendance_tool,
            attendance_shortage_tool,
            marks_tool,
            cgpa_tool,
            rank_tool,
            fees_tool,
            fee_clearance_tool,
            timetable_tool,
            next_class_tool,
            search_books_tool,
            student_loans_tool,
            reserve_book_tool,
            upcoming_events_tool,
            register_event_tool,
            student_events_tool
        ]
        
        # Create Super Smart Agent instead of Function Agent
        logger.info("🤖 STEP 7: Creating Super Smart AI Agent...")
        
        # Get query engine for RAG
        query_engine = index.as_query_engine(llm=llm)
        
        # Create the super smart agent
        agent = SuperSmartAgent(
            llm=llm,
            query_engine=query_engine,
            tools=tools
        )
        
        logger.info("✅ Super Smart Agent created with:")
        logger.info(f"   🧠 Advanced reasoning with Gemini LLM")
        logger.info(f"   🛠️  {len(tools)} specialized tools")
        logger.info(f"   📚 RAG knowledge base")
        logger.info(f"   🎯 Intent analysis & tool orchestration")
        
        logger.info("=" * 80)
        logger.info("✅ AI AGENT SYSTEM INITIALIZATION COMPLETE!")
        logger.info(f"📊 Total Documents Indexed: {len(documents)}")
        logger.info(f"🛠️  Total Tools Available: {len(tools)}")
        logger.info(f"🎯 Ready to handle intelligent queries!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR INITIALIZING AI AGENT: {str(e)}")
        logger.error("=" * 80)
        raise


def refresh_index():
    """
    Refresh the vector index with the latest knowledge base data.
    Called after adding new knowledge items.
    """
    global index
    
    try:
        logger.info("🔄 Refreshing knowledge base index...")
        supabase = get_supabase()
        response = supabase.table(KNOWLEDGE_BASE_TABLE).select("*").execute()
        
        documents = []
        if response.data:
            for item in response.data:
                doc = Document(
                    text=item['content'],
                    metadata={
                        'id': str(item['id']),
                        'category': item['category'],
                        'created_at': str(item['created_at'])
                    },
                    doc_id=str(item['id'])
                )
                documents.append(doc)
        
        if documents:
            index = VectorStoreIndex.from_documents(documents, show_progress=True)
            logger.info(f"✅ Index refreshed with {len(documents)} documents")
        else:
            index = VectorStoreIndex.from_documents([])
            logger.warning("⚠️  No documents found")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR REFRESHING INDEX: {str(e)}")
        logger.error("=" * 80)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize LlamaIndex
    logger.info("Starting up BharatAce backend...")
    try:
        initialize_llama_index()
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down BharatAce backend...")


# Initialize FastAPI app
app = FastAPI(
    title="BharatAce - Super Smart AI Campus Assistant",
    description="Production-ready AI campus assistant with multi-tool agent, authentication, and personalized responses",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],  # Allow configured origins + wildcard for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from api.auth_routes import router as auth_router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


# ==================== API ENDPOINTS ====================

@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "message": "BharatAce AI Campus Assistant API",
        "status": "operational",
        "version": "1.0.0"
    }


@app.post(
    "/knowledge",
    response_model=KnowledgeItem,
    status_code=status.HTTP_201_CREATED,
    tags=["Knowledge Base"],
    summary="Add new knowledge base entry"
)
async def create_knowledge_item(item: KnowledgeItemCreate):
    """
    Add a new entry to the knowledge base.
    
    This endpoint:
    1. Stores the content in Supabase
    2. Refreshes the RAG index to include the new content
    
    Args:
        item: Knowledge item to create (content and category)
    
    Returns:
        The created knowledge item with ID and timestamp
    """
    try:
        supabase = get_supabase()
        
        # Create new record in Supabase
        data = {
            "id": str(uuid.uuid4()),
            "content": item.content,
            "category": item.category,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table(KNOWLEDGE_BASE_TABLE).insert(data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create knowledge item"
            )
        
        # Refresh the vector index with new data
        refresh_index()
        
        created_item = response.data[0]
        logger.info(f"Created knowledge item: {created_item['id']}")
        
        return KnowledgeItem(**created_item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating knowledge item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the knowledge item: {str(e)}"
        )


@app.get(
    "/knowledge",
    response_model=List[KnowledgeItem],
    tags=["Knowledge Base"],
    summary="Get all knowledge base entries"
)
async def get_knowledge_items():
    """
    Retrieve all entries from the knowledge base.
    
    Returns:
        List of all knowledge items in the database
    """
    try:
        supabase = get_supabase()
        
        # Fetch all records from knowledge_base table
        response = supabase.table(KNOWLEDGE_BASE_TABLE).select("*").order("created_at", desc=True).execute()
        
        logger.info(f"Retrieved {len(response.data)} knowledge items")
        
        return [KnowledgeItem(**item) for item in response.data]
        
    except Exception as e:
        logger.error(f"Error retrieving knowledge items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving knowledge items: {str(e)}"
        )


@app.post("/ask", response_model=Answer, tags=["Chatbot"])
async def ask_question(
    question: Question,
    user: Optional[AuthUser] = Depends(OptionalAuth())
):
    """
    AI Agent endpoint with personalized responses.
    
    This endpoint:
    1. Accepts authenticated or anonymous users
    2. For authenticated students, injects student context into query
    3. Uses ReAct Agent with 17 specialized tools
    4. Can answer both general questions and student-specific queries
    5. Can perform actions (reserve books, register for events)
    
    Args:
        question: The question object containing the user's query
        user: Optional authenticated user (from JWT token)
    
    Returns:
        Answer object with the AI-generated response
    """
    try:
        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Agent not initialized. Please try again later."
            )
        
        logger.info("=" * 80)
        logger.info(f"❓ QUESTION RECEIVED: {question.query}")
        
        # Build personalized query with student context
        if user and user.student_id:
            logger.info(f"👤 Authenticated Student: {user.full_name} (ID: {user.student_id})")
            
            # Build conversation context if history exists
            conversation_context = ""
            if question.conversation_history:
                logger.info(f"💬 Conversation history: {len(question.conversation_history)} messages")
                conversation_context = "\n\n=== CONVERSATION HISTORY ===\n"
                for msg in question.conversation_history[-6:]:  # Last 6 messages (3 exchanges)
                    role = "Student" if msg.get("role") == "user" else "Assistant"
                    conversation_context += f"{role}: {msg.get('content', '')}\n"
                conversation_context += "=== END OF HISTORY ===\n\n"
            
            # Inject student context into query
            personalized_query = f"""Student Information:
- Name: {user.full_name}
- Roll Number: {user.roll_number}
- Student ID: {user.student_id}
- Semester: {user.student_data.get('semester', 'Unknown')}
- Department: {user.student_data.get('department', 'Unknown')}
{conversation_context}
CURRENT QUESTION: {question.query}

IMPORTANT INSTRUCTIONS:
1. Read the conversation history carefully to understand the context
2. This is a FOLLOW-UP question if conversation history exists
3. The current question likely refers to the topic discussed above
4. For student-specific queries (attendance, marks, fees, timetable, library), use the student's ID: {user.student_id}
5. For general queries (events, knowledge), DO NOT pass student_id - these tools don't require it
6. Provide contextual responses based on what was discussed previously
7. Be concise and friendly - don't repeat greetings if already in conversation

Example: If the student asked "What's my attendance?" and then asks "how many do I need to get to 90", 
they are asking about attendance (how many more classes to reach 90%), NOT about marks or CGPA."""
        else:
            logger.info("🌍 Anonymous/Admin User - General query")
            
            # Build conversation context for anonymous users too
            conversation_context = ""
            if question.conversation_history:
                logger.info(f"💬 Conversation history: {len(question.conversation_history)} messages")
                conversation_context = "Previous Conversation:\n"
                for msg in question.conversation_history[-6:]:  # Last 6 messages
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    conversation_context += f"{role}: {msg.get('content', '')}\n"
                conversation_context += f"\nCurrent Question: {question.query}"
                personalized_query = conversation_context
            else:
                personalized_query = question.query
        
        logger.info("=" * 80)
        
        # Query the Super Smart AI Agent
        logger.info("🤖 Sending query to Super Smart AI Agent...")
        
        # Prepare student context if user is authenticated
        student_context = None
        if user and user.student_id:
            logger.info(f"📋 Preparing student context for: {user.full_name}")
            logger.info(f"📋 Student ID: {str(user.student_id)} (type: {type(user.student_id).__name__})")
            student_context = {
                'id': str(user.student_id),  # Ensure it's a string
                'full_name': user.full_name,
                'roll_number': user.roll_number,
                **user.student_data
            }
            logger.info(f"📋 Student context prepared: {student_context.get('id', 'NO ID')}")
        else:
            logger.info("📋 No student context - user is None or has no student_id")
        
        # Query the super smart agent
        logger.info(f"🚀 Calling agent.query() with student_context: {student_context is not None}")
        # Use personalized_query (includes conversation history) instead of question.query
        response = await agent.query(personalized_query, student_context)
        answer_text = str(response)
        
        logger.info("=" * 80)
        logger.info(f"✅ AGENT RESPONSE GENERATED")
        logger.info(f"📊 Question: {question.query[:50]}...")
        logger.info(f"📊 Answer Length: {len(answer_text)} chars")
        logger.info(f"📊 User Type: {'Student' if user and user.student_id else 'General'}")
        logger.info("=" * 80)
        
        return Answer(response=answer_text)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR PROCESSING QUESTION: {str(e)}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your question: {str(e)}"
        )


@app.get(
    "/health",
    tags=["Health"],
    summary="Detailed health check"
)
async def health_check():
    """
    Detailed health check endpoint.
    
    Returns:
        System status including database and AI components
    """
    health_status = {
        "status": "healthy",
        "components": {
            "database": "unknown",
            "query_engine": "unknown"
        }
    }
    
    # Check database connection
    try:
        supabase = get_supabase()
        supabase.table(KNOWLEDGE_BASE_TABLE).select("id").limit(1).execute()
        health_status["components"]["database"] = "operational"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI agent
    if agent is not None:
        health_status["components"]["ai_agent"] = "operational"
        health_status["components"]["vector_index"] = "operational" if index is not None else "not initialized"
    else:
        health_status["components"]["ai_agent"] = "not initialized"
        health_status["status"] = "degraded"
    
    return health_status


# ==================== ADMIN ROUTES ====================

# Register admin routes
from api.admin_auth import router as admin_auth_router
from api.admin_dashboard import router as admin_dashboard_router
from api.admin_routes import router as admin_management_router

app.include_router(admin_auth_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_management_router)

# Register student routes
from api.student_routes import router as student_router
app.include_router(student_router)


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
