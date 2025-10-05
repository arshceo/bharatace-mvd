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
}

export default function UpcomingEventsCard() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await apiClient.events.getUpcoming();
        setEvents(response.data.events || []);
      } catch (error) {
        console.error('Error fetching events:', error);
        setEvents([]);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
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

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Upcoming Events
        </h3>
        {events.length > 3 && (
          <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
            View All ({events.length}) →
          </button>
        )}
      </div>
      
      {events.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {events.slice(0, 3).map((event) => {
            const startDate = new Date(event.start_date);
            
            return (
              <div key={event.id} className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-1 text-xs font-semibold rounded ${getEventTypeColor(event.event_type)}`}>
                    {formatEventType(event.event_type)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </span>
                </div>
                <h4 className="font-semibold text-gray-900 text-sm mb-1">{event.title}</h4>
                <p className="text-xs text-gray-600 mb-2 line-clamp-2">{event.description}</p>
                <div className="text-xs text-gray-500 mb-2">
                  📍 {event.location}
                </div>
                <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">
                  View Details →
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <svg className="h-16 w-16 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-sm">No upcoming events at the moment</p>
          <p className="text-xs text-gray-400 mt-1">Check back later for new events</p>
        </div>
      )}
    </div>
  );
}
