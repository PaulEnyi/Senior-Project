import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiCalendar,
  FiPlus,
  FiEdit3,
  FiTrash2,
  FiSave,
  FiX,
  FiChevronLeft,
  FiChevronRight,
  FiClock,
  FiBookmark,
  FiAlertCircle
} from 'react-icons/fi';
import '../../styles/calendar.css';

const CalendarView = ({ user }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [events, setEvents] = useState({});
  const [showEventModal, setShowEventModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [eventForm, setEventForm] = useState({
    title: '',
    description: '',
    time: '',
    type: 'reminder', // reminder, event, assignment, exam
    priority: 'medium' // low, medium, high
  });

  // Load events from localStorage on component mount
  useEffect(() => {
    const savedEvents = localStorage.getItem('morgan_calendar_events');
    if (savedEvents) {
      try {
        setEvents(JSON.parse(savedEvents));
      } catch (error) {
        console.error('Error loading calendar events:', error);
      }
    }
  }, []);

  // Save events to localStorage whenever events change
  useEffect(() => {
    localStorage.setItem('morgan_calendar_events', JSON.stringify(events));
  }, [events]);

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDateKey = (date) => {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  };

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const handleDateClick = (day) => {
    const clickedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    const dateKey = formatDateKey(clickedDate);
    setSelectedDate(dateKey);
    
    // If there are no events for this date, open the modal to add one
    if (!events[dateKey] || events[dateKey].length === 0) {
      setShowEventModal(true);
      setEventForm({
        title: '',
        description: '',
        time: '',
        type: 'reminder',
        priority: 'medium'
      });
    }
  };

  const handleAddEvent = () => {
    if (!selectedDate) {
      const today = new Date();
      const todayKey = formatDateKey(today);
      setSelectedDate(todayKey);
    }
    
    setEditingEvent(null);
    setEventForm({
      title: '',
      description: '',
      time: '',
      type: 'reminder',
      priority: 'medium'
    });
    setShowEventModal(true);
  };

  const handleEditEvent = (eventId) => {
    const event = events[selectedDate]?.find(e => e.id === eventId);
    if (event) {
      setEditingEvent(eventId);
      setEventForm(event);
      setShowEventModal(true);
    }
  };

  const handleSaveEvent = () => {
    if (!eventForm.title.trim() || !selectedDate) return;

    const newEvent = {
      id: editingEvent || Date.now().toString(),
      ...eventForm,
      createdAt: editingEvent ? events[selectedDate].find(e => e.id === editingEvent).createdAt : new Date().toISOString()
    };

    setEvents(prev => {
      const updated = { ...prev };
      if (!updated[selectedDate]) {
        updated[selectedDate] = [];
      }
      
      if (editingEvent) {
        // Update existing event
        const index = updated[selectedDate].findIndex(e => e.id === editingEvent);
        if (index !== -1) {
          updated[selectedDate][index] = newEvent;
        }
      } else {
        // Add new event
        updated[selectedDate].push(newEvent);
      }
      
      return updated;
    });

    setShowEventModal(false);
    setEditingEvent(null);
  };

  const handleDeleteEvent = (eventId) => {
    if (window.confirm('Are you sure you want to delete this event?')) {
      setEvents(prev => {
        const updated = { ...prev };
        if (updated[selectedDate]) {
          updated[selectedDate] = updated[selectedDate].filter(e => e.id !== eventId);
          if (updated[selectedDate].length === 0) {
            delete updated[selectedDate];
          }
        }
        return updated;
      });
    }
  };

  const renderCalendarGrid = () => {
    const daysInMonth = getDaysInMonth(currentDate);
    const firstDay = getFirstDayOfMonth(currentDate);
    const days = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(
        <div key={`empty-${i}`} className="calendar-day empty"></div>
      );
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dateKey = formatDateKey(date);
      const dayEvents = events[dateKey] || [];
      const isToday = dateKey === formatDateKey(new Date());
      const isSelected = dateKey === selectedDate;

      days.push(
        <motion.div
          key={day}
          className={`calendar-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${dayEvents.length > 0 ? 'has-events' : ''}`}
          onClick={() => handleDateClick(day)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="day-number">{day}</span>
          {dayEvents.length > 0 && (
            <div className="event-indicators">
              {dayEvents.slice(0, 3).map((event, index) => (
                <div
                  key={index}
                  className={`event-dot ${event.type} priority-${event.priority}`}
                  title={event.title}
                />
              ))}
              {dayEvents.length > 3 && (
                <span className="more-events">+{dayEvents.length - 3}</span>
              )}
            </div>
          )}
        </motion.div>
      );
    }

    return days;
  };

  const getEventTypeIcon = (type) => {
    switch (type) {
      case 'assignment': return <FiEdit3 />;
      case 'exam': return <FiAlertCircle />;
      case 'event': return <FiCalendar />;
      default: return <FiBookmark />;
    }
  };

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <div className="calendar-title-section">
          <div className="title-with-icon">
            <FiCalendar className="calendar-icon" />
            <h1 className="calendar-title">Academic Calendar</h1>
          </div>
          <p className="calendar-subtitle">Manage your schedule, assignments, and reminders</p>
        </div>
        
        <button
          className="add-event-btn"
          onClick={handleAddEvent}
        >
          <FiPlus />
          Add Event
        </button>
      </div>

      <div className="calendar-content">
        <div className="calendar-view">
          <div className="calendar-controls">
            <button
              className="nav-btn"
              onClick={() => navigateMonth(-1)}
            >
              <FiChevronLeft />
            </button>
            
            <h2 className="month-year">
              {months[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h2>
            
            <button
              className="nav-btn"
              onClick={() => navigateMonth(1)}
            >
              <FiChevronRight />
            </button>
          </div>

          <div className="calendar-grid">
            <div className="weekdays">
              {weekdays.map(day => (
                <div key={day} className="weekday">
                  {day}
                </div>
              ))}
            </div>
            
            <div className="days-grid">
              {renderCalendarGrid()}
            </div>
          </div>
        </div>

        <div className="calendar-sidebar">
          {selectedDate && (
            <div className="selected-date-panel">
              <h3 className="panel-title">
                {new Date(selectedDate).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </h3>
              
              <div className="events-list">
                {events[selectedDate]?.length > 0 ? (
                  events[selectedDate].map(event => (
                    <motion.div
                      key={event.id}
                      className={`event-card ${event.type} priority-${event.priority}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="event-header">
                        <div className="event-icon">
                          {getEventTypeIcon(event.type)}
                        </div>
                        <div className="event-info">
                          <h4 className="event-title">{event.title}</h4>
                          {event.time && (
                            <div className="event-time">
                              <FiClock />
                              {event.time}
                            </div>
                          )}
                        </div>
                        <div className="event-actions">
                          <button
                            className="edit-btn"
                            onClick={() => handleEditEvent(event.id)}
                            title="Edit event"
                          >
                            <FiEdit3 />
                          </button>
                          <button
                            className="delete-btn"
                            onClick={() => handleDeleteEvent(event.id)}
                            title="Delete event"
                          >
                            <FiTrash2 />
                          </button>
                        </div>
                      </div>
                      
                      {event.description && (
                        <p className="event-description">{event.description}</p>
                      )}
                      
                      <div className="event-meta">
                        <span className={`event-type-badge ${event.type}`}>
                          {event.type.charAt(0).toUpperCase() + event.type.slice(1)}
                        </span>
                        <span className={`priority-badge priority-${event.priority}`}>
                          {event.priority.charAt(0).toUpperCase() + event.priority.slice(1)} Priority
                        </span>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="no-events">
                    <FiCalendar className="no-events-icon" />
                    <p>No events for this date</p>
                    <button
                      className="add-event-link"
                      onClick={handleAddEvent}
                    >
                      Add your first event
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Event Modal */}
      <AnimatePresence>
        {showEventModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowEventModal(false)}
          >
            <motion.div
              className="event-modal"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3 className="modal-title">
                  {editingEvent ? 'Edit Event' : 'Add New Event'}
                </h3>
                <button
                  className="modal-close"
                  onClick={() => setShowEventModal(false)}
                >
                  <FiX />
                </button>
              </div>

              <div className="modal-body">
                <div className="form-group">
                  <label htmlFor="title">Event Title *</label>
                  <input
                    id="title"
                    type="text"
                    value={eventForm.title}
                    onChange={(e) => setEventForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Submit Lab 3, Study session, Meeting..."
                    autoFocus
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="description">Description</label>
                  <textarea
                    id="description"
                    value={eventForm.description}
                    onChange={(e) => setEventForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Additional details about this event..."
                    rows={3}
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="time">Time (Optional)</label>
                    <input
                      id="time"
                      type="time"
                      value={eventForm.time}
                      onChange={(e) => setEventForm(prev => ({ ...prev, time: e.target.value }))}
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="type">Type</label>
                    <select
                      id="type"
                      value={eventForm.type}
                      onChange={(e) => setEventForm(prev => ({ ...prev, type: e.target.value }))}
                    >
                      <option value="reminder">Reminder</option>
                      <option value="assignment">Assignment</option>
                      <option value="exam">Exam</option>
                      <option value="event">Event</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="priority">Priority</label>
                    <select
                      id="priority"
                      value={eventForm.priority}
                      onChange={(e) => setEventForm(prev => ({ ...prev, priority: e.target.value }))}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  className="cancel-btn"
                  onClick={() => setShowEventModal(false)}
                >
                  Cancel
                </button>
                <button
                  className="save-btn"
                  onClick={handleSaveEvent}
                  disabled={!eventForm.title.trim()}
                >
                  <FiSave />
                  {editingEvent ? 'Update Event' : 'Save Event'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CalendarView;