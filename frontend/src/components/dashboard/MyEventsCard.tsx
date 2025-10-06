"use client";

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface Event {
  id: string;
  title: string;
  description: string;
  event_type: string;
  start_date: string;
  end_date: string;
  location: string;
  organizer: string;
  registration_date?: string;
  registration_id?: string;
}

interface MyEventsData {
  all_events: Event[];
  upcoming_events: Event[];
  past_events: Event[];
  total_registered: number;
  upcoming_count: number;
  past_count: number;
}

export default function MyEventsCard() {
  const [eventsData, setEventsData] = useState<MyEventsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPastEvents, setShowPastEvents] = useState(false);

  useEffect(() => {
    const fetchMyEvents = async () => {
      try {
        const response = await apiClient.events.getMyEvents();
        setEventsData(response.data);
      } catch (error) {
        console.error('Error fetching my events:', error);
        setEventsData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMyEvents();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="space-y-3">
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const getEventTypeColor = (type: string) => {
    const types: Record<string, string> = {
      workshop: 'bg-purple-100 text-purple-700',
      seminar: 'bg-blue-100 text-blue-700',
      competition: 'bg-green-100 text-green-700',
      cultural: 'bg-pink-100 text-pink-700',
      sports: 'bg-orange-100 text-orange-700',
      academic: 'bg-indigo-100 text-indigo-700',
    };
    return types[type.toLowerCase()] || 'bg-gray-100 text-gray-700';
  };

  const formatEventType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  const displayEvents = showPastEvents 
    ? eventsData?.past_events || []
    : eventsData?.upcoming_events || [];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          My Registered Events
        </h3>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
            {eventsData?.total_registered || 0} Registered
          </span>
          {(eventsData?.past_count || 0) > 0 && (
            <button
              onClick={() => setShowPastEvents(!showPastEvents)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {showPastEvents ? 'Show Upcoming' : 'Show Past'}
            </button>
          )}
        </div>
      </div>

      {!eventsData || eventsData.total_registered === 0 ? (
        <div className="text-center py-8">
          <svg className="h-16 w-16 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-500 mb-2">You haven't registered for any events yet</p>
          <p className="text-sm text-gray-400">Ask the AI chat to register you for upcoming events!</p>
        </div>
      ) : displayEvents.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">
            {showPastEvents ? 'No past events' : 'No upcoming events'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {displayEvents.map((event) => {
            const startDate = new Date(event.start_date);
            const isToday = startDate.toDateString() === new Date().toDateString();
            
            return (
              <div 
                key={event.id} 
                className={`p-4 border-l-4 rounded-lg ${
                  isToday 
                    ? 'bg-green-50 border-green-500' 
                    : 'bg-gray-50 border-gray-300'
                } hover:shadow-md transition-all`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getEventTypeColor(event.event_type)}`}>
                      {formatEventType(event.event_type)}
                    </span>
                    {isToday && (
                      <span className="px-2 py-1 text-xs font-semibold rounded bg-green-500 text-white">
                        TODAY
                      </span>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      {formatDate(event.start_date)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTime(event.start_date)}
                    </div>
                  </div>
                </div>
                
                <h4 className="font-semibold text-gray-900 mb-1">{event.title}</h4>
                <p className="text-sm text-gray-600 mb-2 line-clamp-2">{event.description}</p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center">
                      <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {event.location}
                    </span>
                    <span className="flex items-center">
                      <svg className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      {event.organizer}
                    </span>
                  </div>
                  {event.registration_date && (
                    <span className="text-gray-400">
                      Registered: {formatDate(event.registration_date)}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {eventsData && eventsData.total_registered > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              {showPastEvents 
                ? `${eventsData.past_count} Past Events`
                : `${eventsData.upcoming_count} Upcoming Events`
              }
            </span>
            <span className="text-xs text-gray-400">
              Total: {eventsData.total_registered} events
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
