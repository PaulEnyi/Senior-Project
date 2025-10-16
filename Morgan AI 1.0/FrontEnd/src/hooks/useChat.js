import { useState, useCallback, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { apiService } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentThread, setCurrentThread] = useState(null);
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    const savedThread = localStorage.getItem('currentThread');
    if (savedThread) {
      setCurrentThread(savedThread);
    }
  }, []);

  const createNewThread = useCallback(() => {
    const newThreadId = uuidv4();
    setCurrentThread(newThreadId);
    setMessages([]);
    setError(null);
    
    localStorage.setItem('currentThread', newThreadId);
    
    return newThreadId;
  }, []);

  const sendMessage = useCallback(async (messageText, options = {}) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: messageText.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    abortControllerRef.current = new AbortController();

    try {
      let threadId = currentThread;
      if (!threadId) {
        threadId = createNewThread();
      }

      const response = await apiService.sendMessage({
        message: messageText,
        thread_id: threadId,
        category_filter: options.categoryFilter,
        include_related_questions: options.includeRelatedQuestions ?? true
      }, {
        signal: abortControllerRef.current.signal
      });

      const aiMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        sources_used: response.sources_used || [],
        related_questions: response.related_questions || []
      };

      setMessages(prev => [...prev, aiMessage]);

      if (response.thread_id && response.thread_id !== threadId) {
        setCurrentThread(response.thread_id);
        localStorage.setItem('currentThread', response.thread_id);
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('Request was aborted');
        return;
      }

      console.error('Error sending message:', err);
      setError(err.message || 'Failed to send message');

      const errorMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
        error: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [currentThread, isLoading, createNewThread]);

  const loadThreadHistory = useCallback(async (threadId) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.getThreadMessages(threadId);
      
      if (response.messages && Array.isArray(response.messages)) {
        setMessages(response.messages);
        setCurrentThread(threadId);
        localStorage.setItem('currentThread', threadId);
      }
    } catch (err) {
      console.error('Error loading thread history:', err);
      setError('Failed to load conversation history');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearCurrentThread = useCallback(async () => {
    if (currentThread) {
      try {
        await apiService.clearThread(currentThread);
      } catch (err) {
        console.error('Error clearing thread:', err);
      }
    }

    setMessages([]);
    setCurrentThread(null);
    setError(null);
    localStorage.removeItem('currentThread');
  }, [currentThread]);

  const deleteThread = useCallback(async (threadId) => {
    try {
      await apiService.deleteThread(threadId);
      
      if (threadId === currentThread) {
        setMessages([]);
        setCurrentThread(null);
        localStorage.removeItem('currentThread');
      }
    } catch (err) {
      console.error('Error deleting thread:', err);
      throw new Error('Failed to delete conversation');
    }
  }, [currentThread]);

  const getThreadList = useCallback(async (limit = 20, offset = 0) => {
    try {
      const response = await apiService.getThreadList({ limit, offset });
      return response.threads || [];
    } catch (err) {
      console.error('Error getting thread list:', err);
      throw new Error('Failed to load conversations');
    }
  }, []);

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  }, []);

  const retryLastMessage = useCallback(() => {
    const lastUserMessage = [...messages]
      .reverse()
      .find(msg => msg.role === 'user');

    if (lastUserMessage) {
      setMessages(prev => {
        const filtered = prev.filter(msg => 
          !(msg.role === 'assistant' && msg.error)
        );
        return filtered;
      });

      sendMessage(lastUserMessage.content);
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    currentThreadId: currentThread,
    error,
    sendMessage,
    createNewThread,
    loadThreadHistory,
    clearCurrentThread,
    clearChat: clearCurrentThread, // Add this alias
    deleteThread,
    getThreadList,
    cancelRequest,
    retryLastMessage,
    hasMessages: messages.length > 0,
    lastMessage: messages[messages.length - 1] || null,
    messageCount: messages.length
  };
};