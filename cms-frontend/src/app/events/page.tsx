"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SidebarLayout from '@/components/SidebarLayout';
import { events as eventsApi } from '@/lib/api';
import { Plus, Search, Edit2, Trash2, Calendar, MapPin, X, Users, Info, Mail, BookOpen } from 'lucide-react';

interface Event {
  id: string;
  title: string;
  description: string;
  start_date: string;
  end_date?: string;
  event_date?: string;
  location: string;
  organizer: string;
  event_type?: string;
  max_participants?: number;
  registered_count?: number;
  event_status?: 'scheduled' | 'ongoing' | 'completed' | 'cancelled';
  status?: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  created_at: string;
}

interface Participant {
  id: string;
  event_id: string;
  student_id: string;
  registration_date: string;
  attendance_status?: string;
  student_name: string;
  roll_number: string;
  email: string;
  semester?: number;
  course?: string;
}

export default function EventsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [loadingParticipants, setLoadingParticipants] = useState(false);
  const [events, setEvents] = useState<Event[]>([]);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    event_date: '',
    location: '',
    organizer: '',
    event_type: '',
    max_participants: 0,
    event_status: 'scheduled' as 'scheduled' | 'ongoing' | 'completed' | 'cancelled',
  });

  useEffect(() => {
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
      router.push('/');
      return;
    }
    fetchEvents();
  }, [router]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await eventsApi.getAll();
      // Backend returns {events: [...]}
      const eventsData = response.data.events || response.data || [];
      setEvents(Array.isArray(eventsData) ? eventsData : []);
    } catch (error) {
      console.error('Error fetching events:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchParticipants = async (eventId: string) => {
    try {
      setLoadingParticipants(true);
      const response = await eventsApi.getParticipants(eventId);
      const participantsData = response.data.participants || [];
      setParticipants(participantsData);
    } catch (error) {
      console.error('Error fetching participants:', error);
      setParticipants([]);
    } finally {
      setLoadingParticipants(false);
    }
  };

  const openEventDetails = async (event: Event) => {
    setSelectedEvent(event);
    setShowDetailModal(true);
    await fetchParticipants(event.id);
  };

  const openEditModal = (event: Event) => {
    setSelectedEvent(event);
    const status = event.event_status || event.status || 'scheduled';
    const validStatus: 'scheduled' | 'ongoing' | 'completed' | 'cancelled' = 
      status === 'upcoming' ? 'scheduled' : status as 'scheduled' | 'ongoing' | 'completed' | 'cancelled';
    
    setFormData({
      title: event.title,
      description: event.description,
      event_date: event.event_date || event.start_date,
      location: event.location,
      organizer: event.organizer,
      event_type: event.event_type || '',
      max_participants: event.max_participants || 0,
      event_status: validStatus,
    });
    setShowEditModal(true);
  };

  const handleEditEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEvent) return;
    try {
      await eventsApi.update(selectedEvent.id, formData);
      setShowEditModal(false);
      fetchEvents();
      setSelectedEvent(null);
    } catch (error) {
      console.error('Error updating event:', error);
      alert('Failed to update event');
    }
  };

  const handleDeleteEvent = async (id: string) => {
    if (!confirm('Are you sure you want to delete this event?')) return;
    try {
      await eventsApi.delete(id);
      fetchEvents();
    } catch (error) {
      console.error('Error deleting event:', error);
      alert('Failed to delete event');
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      scheduled: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-800 dark:text-blue-200' },
      ongoing: { bg: 'bg-green-100 dark:bg-green-900', text: 'text-green-800 dark:text-green-200' },
      completed: { bg: 'bg-gray-100 dark:bg-gray-900', text: 'text-gray-800 dark:text-gray-200' },
      cancelled: { bg: 'bg-red-100 dark:bg-red-900', text: 'text-red-800 dark:text-red-200' },
      upcoming: { bg: 'bg-blue-100 dark:bg-blue-900', text: 'text-blue-800 dark:text-blue-200' },
    };
    const badge = badges[status as keyof typeof badges] || badges.scheduled;
    return (
      <span className={`px-2 py-1 text-xs rounded-full ${badge.bg} ${badge.text}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const filteredEvents = Array.isArray(events) ? events.filter((event) => {
    const matchesSearch = 
      event?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event?.location?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event?.organizer?.toLowerCase().includes(searchQuery.toLowerCase());
    const eventStatus = event?.event_status || event?.status || 'scheduled';
    const matchesStatus = filterStatus === 'all' || eventStatus === filterStatus;
    return matchesSearch && matchesStatus;
  }) : [];

  if (loading) {
    return (
      <SidebarLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
      </SidebarLayout>
    );
  }

  return (
    <SidebarLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Events Management</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Total Events: {events.length}
            </p>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search events by title, location, or organizer..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="upcoming">Upcoming</option>
              <option value="ongoing">Ongoing</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvents.map((event) => {
            const eventDate = event.event_date || event.start_date;
            const status = event.event_status || event.status || 'scheduled';
            const participantCount = event.registered_count || 0;
            const maxParticipants = event.max_participants || 0;
            const participantPercentage = maxParticipants > 0 ? (participantCount / maxParticipants) * 100 : 0;

            return (
              <div
                key={event.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 
                      className="text-lg font-semibold text-gray-900 dark:text-white flex-1 cursor-pointer hover:text-indigo-600"
                      onClick={() => openEventDetails(event)}
                    >
                      {event.title}
                    </h3>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(status)}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          openEditModal(event);
                        }}
                        className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteEvent(event.id);
                        }}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <p 
                    className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2 cursor-pointer"
                    onClick={() => openEventDetails(event)}
                  >
                    {event.description}
                  </p>

                  <div 
                    className="space-y-2 text-sm cursor-pointer"
                    onClick={() => openEventDetails(event)}
                  >
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Calendar className="w-4 h-4 mr-2" />
                      {eventDate ? new Date(eventDate).toLocaleDateString() : 'Date TBD'}
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <MapPin className="w-4 h-4 mr-2" />
                      {event.location || 'Location TBD'}
                    </div>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <Users className="w-4 h-4 mr-2" />
                      {participantCount} / {maxParticipants > 0 ? maxParticipants : '∞'} participants
                    </div>
                  </div>

                  {maxParticipants > 0 && (
                    <div className="mt-4" onClick={() => openEventDetails(event)}>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 cursor-pointer">
                        <div
                          className="bg-indigo-600 h-2 rounded-full transition-all"
                          style={{ width: `${Math.min(participantPercentage, 100)}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {participantPercentage.toFixed(0)}% capacity
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {filteredEvents.length === 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <Calendar className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No events found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {searchQuery || filterStatus !== 'all' ? 'Try adjusting your filters' : 'No events available'}
            </p>
          </div>
        )}

        {showDetailModal && selectedEvent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {selectedEvent.title}
                    </h2>
                    {getStatusBadge(selectedEvent.event_status || selectedEvent.status || 'scheduled')}
                  </div>
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setSelectedEvent(null);
                    }}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Description</h3>
                    <p className="text-gray-900 dark:text-white">{selectedEvent.description}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1 flex items-center">
                        <Calendar className="w-4 h-4 mr-1" /> Date
                      </h3>
                      <p className="text-gray-900 dark:text-white">
                        {selectedEvent.event_date || selectedEvent.start_date
                          ? new Date(selectedEvent.event_date || selectedEvent.start_date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                            })
                          : 'Date TBD'}
                      </p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1 flex items-center">
                        <MapPin className="w-4 h-4 mr-1" /> Location
                      </h3>
                      <p className="text-gray-900 dark:text-white">{selectedEvent.location || 'Location TBD'}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1 flex items-center">
                        <Info className="w-4 h-4 mr-1" /> Organizer
                      </h3>
                      <p className="text-gray-900 dark:text-white">{selectedEvent.organizer || 'N/A'}</p>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1 flex items-center">
                        <Users className="w-4 h-4 mr-1" /> Participants
                      </h3>
                      <p className="text-gray-900 dark:text-white">
                        {selectedEvent.registered_count || 0} / {selectedEvent.max_participants || '∞'}
                      </p>
                    </div>
                  </div>

                  {selectedEvent.event_type && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Event Type</h3>
                      <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 rounded-full text-sm">
                        {selectedEvent.event_type}
                      </span>
                    </div>
                  )}

                  {selectedEvent.max_participants && selectedEvent.max_participants > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Registration Progress</h3>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                        <div
                          className="bg-indigo-600 h-3 rounded-full transition-all"
                          style={{
                            width: `${Math.min(((selectedEvent.registered_count || 0) / selectedEvent.max_participants) * 100, 100)}%`,
                          }}
                        ></div>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {((((selectedEvent.registered_count || 0) / selectedEvent.max_participants) * 100) || 0).toFixed(1)}% capacity filled
                      </p>
                    </div>
                  )}

                  {/* Participants List */}
                  <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                      <Users className="w-5 h-5 mr-2" />
                      Registered Participants ({participants.length})
                    </h3>
                    
                    {loadingParticipants ? (
                      <div className="flex justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                      </div>
                    ) : participants.length > 0 ? (
                      <div className="space-y-3 max-h-64 overflow-y-auto">
                        {participants.map((participant, index) => (
                          <div
                            key={participant.id}
                            className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                                <span className="text-indigo-600 dark:text-indigo-400 font-semibold">
                                  {index + 1}
                                </span>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 dark:text-white">
                                  {participant.student_name}
                                </p>
                                <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                                  <span className="flex items-center">
                                    <BookOpen className="w-3 h-3 mr-1" />
                                    {participant.roll_number}
                                  </span>
                                  {participant.email && (
                                    <span className="flex items-center">
                                      <Mail className="w-3 h-3 mr-1" />
                                      {participant.email}
                                    </span>
                                  )}
                                  {participant.course && (
                                    <span>
                                      {participant.course} - Sem {participant.semester}
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                            {participant.attendance_status && (
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                participant.attendance_status === 'present' 
                                  ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                                  : 'bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200'
                              }`}>
                                {participant.attendance_status}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                        <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No participants registered yet</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setSelectedEvent(null);
                      setParticipants([]);
                    }}
                    className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Edit Event Modal */}
        {showEditModal && selectedEvent && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Edit Event
                  </h2>
                  <button
                    onClick={() => {
                      setShowEditModal(false);
                      setSelectedEvent(null);
                    }}
                    className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <form onSubmit={handleEditEvent} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Event Title *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Description *
                    </label>
                    <textarea
                      required
                      rows={3}
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Event Date *
                      </label>
                      <input
                        type="date"
                        required
                        value={formData.event_date?.split('T')[0]}
                        onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Location *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Organizer *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.organizer}
                        onChange={(e) => setFormData({ ...formData, organizer: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Event Type
                      </label>
                      <input
                        type="text"
                        value={formData.event_type}
                        onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Max Participants
                      </label>
                      <input
                        type="number"
                        min="0"
                        value={formData.max_participants}
                        onChange={(e) => setFormData({ ...formData, max_participants: parseInt(e.target.value) || 0 })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Status *
                      </label>
                      <select
                        required
                        value={formData.event_status}
                        onChange={(e) => setFormData({ ...formData, event_status: e.target.value as any })}
                        className="w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="scheduled">Scheduled</option>
                        <option value="ongoing">Ongoing</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3 mt-6">
                    <button
                      type="button"
                      onClick={() => {
                        setShowEditModal(false);
                        setSelectedEvent(null);
                      }}
                      className="px-4 py-2 border rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                    >
                      Update Event
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </SidebarLayout>
  );
}
