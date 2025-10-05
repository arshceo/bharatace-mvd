"""
Events Tool  
Manages college events, registrations, and participation.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from database import get_supabase_admin
import uuid

logger = logging.getLogger(__name__)


def get_upcoming_events(days_ahead: int = 30, event_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get upcoming events in the next N days.
    
    Args:
        days_ahead: Number of days to look ahead (default 30)
        event_type: Optional filter by event type
        
    Returns:
        Dictionary containing upcoming events
    """
    try:
        supabase = get_supabase_admin()
        
        # Calculate date range
        today = datetime.now().isoformat()
        future_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
        
        # Build query
        query = supabase.table("events")\
            .select("*")\
            .gte("start_date", today)\
            .lte("start_date", future_date)\
            .order("start_date")
        
        if event_type:
            query = query.eq("event_type", event_type)
        
        response = query.execute()
        
        events = response.data
        
        # Categorize events
        categorized = {
            "today": [],
            "this_week": [],
            "this_month": [],
            "later": []
        }
        
        now = datetime.now()
        week_end = now + timedelta(days=7)
        month_end = now + timedelta(days=30)
        
        for event in events:
            event_date = datetime.fromisoformat(event['start_date'])
            
            if event_date.date() == now.date():
                categorized["today"].append(event)
            elif event_date <= week_end:
                categorized["this_week"].append(event)
            elif event_date <= month_end:
                categorized["this_month"].append(event)
            else:
                categorized["later"].append(event)
        
        logger.info(f"Retrieved {len(events)} upcoming events")
        
        return {
            "events": events,
            "categorized": categorized,
            "total_events": len(events),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting upcoming events: {str(e)}")
        return {
            "events": [],
            "success": False,
            "error": str(e)
        }


def get_event_details(event_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific event.
    
    Args:
        event_id: The event's database ID
        
    Returns:
        Dictionary with event details and registration info
    """
    try:
        supabase = get_supabase_admin()
        
        # Get event details
        event_response = supabase.table("events")\
            .select("*")\
            .eq("id", event_id)\
            .execute()
        
        if not event_response.data:
            return {
                "event": None,
                "success": False,
                "message": "Event not found"
            }
        
        event = event_response.data[0]
        
        # Get participant count
        participants_response = supabase.table("event_participation")\
            .select("*")\
            .eq("event_id", event_id)\
            .execute()
        
        registered_count = len(participants_response.data)
        max_participants = event.get('max_participants')
        
        # Check registration status
        registration_open = True
        registration_message = "Registration is open"
        
        if event.get('registration_deadline'):
            deadline = datetime.fromisoformat(event['registration_deadline'])
            if datetime.now() > deadline:
                registration_open = False
                registration_message = "Registration deadline has passed"
        
        if max_participants and registered_count >= max_participants:
            registration_open = False
            registration_message = "Event is full"
        
        if event.get('event_status') in ['completed', 'cancelled']:
            registration_open = False
            registration_message = f"Event is {event['event_status']}"
        
        return {
            "event": event,
            "registered_count": registered_count,
            "max_participants": max_participants,
            "spots_remaining": (max_participants - registered_count) if max_participants else None,
            "registration_open": registration_open,
            "registration_message": registration_message,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error getting event details: {str(e)}")
        return {
            "event": None,
            "success": False,
            "error": str(e)
        }


def register_for_event(student_id: str, event_id: str) -> Dict[str, Any]:
    """
    Register a student for an event.
    
    This is an ACTION tool - it writes data.
    
    Args:
        student_id: The student's database ID
        event_id: The event's database ID
        
    Returns:
        Dictionary with registration confirmation
    """
    try:
        supabase = get_supabase_admin()
        
        # Get event details first
        event_details = get_event_details(event_id)
        
        if not event_details['success']:
            return event_details
        
        if not event_details['registration_open']:
            return {
                "success": False,
                "message": event_details['registration_message']
            }
        
        event = event_details['event']
        
        # Check if already registered
        existing_registration = supabase.table("event_participation")\
            .select("*")\
            .eq("student_id", student_id)\
            .eq("event_id", event_id)\
            .execute()
        
        if existing_registration.data:
            registration = existing_registration.data[0]
            if registration['attendance_status'] == 'cancelled':
                # Re-activate cancelled registration
                supabase.table("event_participation")\
                    .update({"attendance_status": "registered"})\
                    .eq("id", registration['id'])\
                    .execute()
                
                return {
                    "success": True,
                    "message": f"Re-registered for '{event['title']}'!",
                    "event_title": event['title'],
                    "event_date": event['start_date']
                }
            else:
                return {
                    "success": False,
                    "message": f"You are already registered for '{event['title']}'"
                }
        
        # Create registration
        registration_data = {
            "id": str(uuid.uuid4()),
            "event_id": event_id,
            "student_id": student_id,
            "registration_date": datetime.now().isoformat(),
            "attendance_status": "registered"
        }
        
        registration_response = supabase.table("event_participation")\
            .insert(registration_data)\
            .execute()
        
        if not registration_response.data:
            return {
                "success": False,
                "message": "Failed to register for event"
            }
        
        logger.info(f"Student {student_id} registered for event {event_id}")
        
        return {
            "success": True,
            "message": f"Successfully registered for '{event['title']}'!",
            "event_details": {
                "title": event['title'],
                "event_type": event['event_type'],
                "start_date": event['start_date'],
                "location": event['location'],
                "organizer": event['organizer']
            },
            "registration_id": registration_data['id']
        }
        
    except Exception as e:
        logger.error(f"Error registering for event: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def get_student_events(student_id: str, include_past: bool = False) -> Dict[str, Any]:
    """
    Get all events a student is registered for.
    
    Args:
        student_id: The student's database ID
        include_past: If True, include past events
        
    Returns:
        Dictionary containing student's registered events
    """
    try:
        supabase = get_supabase_admin()
        
        # Get student's event participations
        query = supabase.table("event_participation")\
            .select("*, events(*)")\
            .eq("student_id", student_id)\
            .order("registration_date", desc=True)
        
        response = query.execute()
        
        registrations = response.data
        
        # Filter and categorize
        upcoming = []
        past = []
        cancelled = []
        
        now = datetime.now()
        
        for registration in registrations:
            event = registration['events']
            event_date = datetime.fromisoformat(event['start_date'])
            
            if registration['attendance_status'] == 'cancelled':
                cancelled.append(registration)
            elif event_date >= now:
                upcoming.append(registration)
            else:
                past.append(registration)
        
        result = {
            "upcoming_events": upcoming,
            "total_upcoming": len(upcoming),
            "cancelled_events": cancelled,
            "success": True
        }
        
        if include_past:
            result["past_events"] = past
            result["total_past"] = len(past)
        
        logger.info(f"Retrieved events for student {student_id}: {len(upcoming)} upcoming")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting student events: {str(e)}")
        return {
            "upcoming_events": [],
            "success": False,
            "error": str(e)
        }


def cancel_event_registration(student_id: str, event_id: str) -> Dict[str, Any]:
    """
    Cancel a student's registration for an event.
    
    Args:
        student_id: The student's database ID
        event_id: The event's database ID
        
    Returns:
        Dictionary with cancellation confirmation
    """
    try:
        supabase = get_supabase_admin()
        
        # Find the registration
        registration_response = supabase.table("event_participation")\
            .select("*, events(title, start_date)")\
            .eq("student_id", student_id)\
            .eq("event_id", event_id)\
            .eq("attendance_status", "registered")\
            .execute()
        
        if not registration_response.data:
            return {
                "success": False,
                "message": "No active registration found for this event"
            }
        
        registration = registration_response.data[0]
        event = registration['events']
        
        # Check if event has already started
        event_date = datetime.fromisoformat(event['start_date'])
        if datetime.now() >= event_date:
            return {
                "success": False,
                "message": "Cannot cancel registration. Event has already started or ended."
            }
        
        # Update registration status
        supabase.table("event_participation")\
            .update({"attendance_status": "cancelled"})\
            .eq("id", registration['id'])\
            .execute()
        
        logger.info(f"Student {student_id} cancelled registration for event {event_id}")
        
        return {
            "success": True,
            "message": f"Registration cancelled for '{event['title']}'",
            "event_title": event['title']
        }
        
    except Exception as e:
        logger.error(f"Error cancelling registration: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def search_events(
    query: str,
    event_type: Optional[str] = None,
    upcoming_only: bool = True
) -> Dict[str, Any]:
    """
    Search for events by title, description, or organizer.
    
    Args:
        query: Search query
        event_type: Optional event type filter
        upcoming_only: If True, only show future events
        
    Returns:
        Dictionary with search results
    """
    try:
        supabase = get_supabase_admin()
        
        # Build search query
        search_query = supabase.table("events")\
            .select("*")\
            .or_(f"title.ilike.%{query}%,description.ilike.%{query}%,organizer.ilike.%{query}%")
        
        if event_type:
            search_query = search_query.eq("event_type", event_type)
        
        if upcoming_only:
            search_query = search_query.gte("start_date", datetime.now().isoformat())
        
        response = search_query.limit(20).execute()
        
        return {
            "events": response.data,
            "total_results": len(response.data),
            "query": query,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error searching events: {str(e)}")
        return {
            "events": [],
            "success": False,
            "error": str(e)
        }

