import { create } from 'zustand';
import { chatService } from '../services/api';
import realtimeAPI from '../services/realtimeAPI';
import toast from 'react-hot-toast';

const useChatStore = create((set, get) => ({
  messages: [],
  threads: [],
  currentThread: null,
  isLoading: false,
  error: null,
  isStreaming: false,

  // Send a message
  sendMessage: async (content, threadId = null) => {
    const { currentThread } = get();
    const activeThreadId = threadId || currentThread?.thread_id;

    // Add user message immediately
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null
    }));

    try {
      const response = await chatService.sendMessage({
        message: content,
        thread_id: activeThreadId
      });

      const assistantMessage = {
        id: response.message_id || `msg-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        sources: response.sources || [],
        timestamp: response.timestamp
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false
      }));

      // Update thread if needed
      if (response.thread_id && !activeThreadId) {
        set({ currentThread: { thread_id: response.thread_id } });
      }

      return assistantMessage;
    } catch (error) {
      // Robust 401 handling
      if (error.message && error.message.toLowerCase().includes('unauthorized')) {
        localStorage.removeItem('token');
        localStorage.removeItem('auth_token');
        toast.error('Session expired or unauthorized. Please log in again.');
        window.location.href = '/login';
        return;
      }
      const errorMessage = error.message || 'Failed to send message';
      set({ error: errorMessage, isLoading: false });
      toast.error(errorMessage);
      // Remove the temporary user message on error
      set((state) => ({
        messages: state.messages.filter(m => m.id !== userMessage.id)
      }));
      throw error;
    }
  },

  // Stream a message response
  streamMessage: async (content, threadId = null) => {
    const { currentThread } = get();
    const activeThreadId = threadId || currentThread?.thread_id;

    // Add user message
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isStreaming: true,
      error: null
    }));

    // Create placeholder for assistant message
    const assistantMessage = {
      id: `streaming-${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    };

    set((state) => ({
      messages: [...state.messages, assistantMessage]
    }));

    try {
      await chatService.streamMessage(
        {
          message: content,
          thread_id: activeThreadId,
          stream: true
        },
        (chunk) => {
          // Update assistant message with streamed content
          set((state) => ({
            messages: state.messages.map((msg) =>
              msg.id === assistantMessage.id
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          }));
        }
      );

      set({ isStreaming: false });
    } catch (error) {
      set({ error: error.message, isStreaming: false });
      toast.error('Streaming failed');
    }
  },

  // Load chat threads
  loadThreads: async () => {
    try {
      const response = await chatService.getThreads();
      set({ threads: response.threads });
      return response.threads;
    } catch (error) {
      toast.error('Failed to load chat history');
      return [];
    }
  },

  // Load messages for a thread
  loadThread: async (threadId, retryCount = 0) => {
    if (!threadId) {
      console.warn('⚠️ loadThread called with no threadId');
      return null;
    }
    
    console.log(`📂 Loading thread ${threadId}... (attempt ${retryCount + 1})`);
    set({ isLoading: true, error: null });
    try {
      const response = await chatService.getThreadMessages(threadId);
      console.log(`📥 Received response for thread ${threadId}:`, {
        thread_id: response.thread_id,
        title: response.title,
        messageCount: response.messages?.length || 0,
        messages: response.messages
      });
      
      const currentThread = {
        thread_id: response.thread_id,
        title: response.title || 'Untitled Chat'
      };
      
      // Silent retry if zero messages (max 3 retries with exponential backoff)
      if ((!response.messages || response.messages.length === 0) && retryCount < 3) {
        const delay = 300 * Math.pow(2, retryCount); // 300ms, 600ms, 1200ms
        console.log(`⚠️ Zero messages in thread ${threadId}, retrying in ${delay}ms... (attempt ${retryCount + 1}/3)`);
        await new Promise(resolve => setTimeout(resolve, delay));
        return get().loadThread(threadId, retryCount + 1);
      }
      
      set({
        messages: response.messages || [],
        currentThread,
        isLoading: false
      });
      
      // Show appropriate feedback
      if (!response.messages || response.messages.length === 0) {
        console.log(`ℹ️ Thread ${currentThread.thread_id} loaded but contains no messages`);
        toast('No messages found in this conversation', { icon: 'ℹ️' });
      } else {
        console.log(`✅ Loaded thread ${currentThread.thread_id} (${currentThread.title}) with ${response.messages.length} messages`);
        toast.success(`Loaded: ${currentThread.title}`);
      }
      
      return response;
    } catch (error) {
      console.error('❌ Failed to load thread:', error);
      set({ error: 'Failed to load thread', isLoading: false });
      toast.error('Failed to load conversation');
      throw error;
    }
  },

  addSystemMessage: (content, role = 'assistant') => {
    const message = {
      id: `sys-${Date.now()}`,
      role,
      content,
      timestamp: new Date().toISOString()
    };
    set((state) => ({ messages: [...state.messages, message] }));
  },

  // Create new thread
  createThread: () => {
    set({
      messages: [],
      currentThread: null,
      error: null
    });
  },

  // Delete thread
  deleteThread: async (threadId) => {
    try {
      await chatService.deleteThread(threadId);
      set((state) => ({
        threads: state.threads.filter(t => t.thread_id !== threadId),
        messages: state.currentThread?.thread_id === threadId ? [] : state.messages,
        currentThread: state.currentThread?.thread_id === threadId ? null : state.currentThread
      }));
      toast.success('Conversation deleted');
    } catch (error) {
      toast.error('Failed to delete conversation');
    }
  },

  // Regenerate response
  regenerateResponse: async (messageIndex, threadId) => {
    const { messages } = get();
    if (messageIndex < 0 || messageIndex >= messages.length) return;

    // Find the last user message before this index
    let lastUserMessage = null;
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        lastUserMessage = messages[i];
        break;
      }
    }

    if (!lastUserMessage) return;

    // Remove messages after the user message
    const newMessages = messages.slice(0, messages.indexOf(lastUserMessage) + 1);
    set({ messages: newMessages });

    // Resend the message
    await get().sendMessage(lastUserMessage.content, threadId);
  },

  // Search chat history
  searchChats: async (query) => {
    try {
      const response = await chatService.searchHistory(query);
      return response.results;
    } catch (error) {
      toast.error('Search failed');
      return [];
    }
  },

  // Submit feedback
  submitFeedback: async (messageId, rating, feedback) => {
    try {
      await chatService.submitFeedback(messageId, rating, feedback);
      
      // Update message with feedback
      set((state) => ({
        messages: state.messages.map((msg) =>
          msg.id === messageId
            ? { ...msg, feedback: { rating, comment: feedback } }
            : msg
        )
      }));
      
      toast.success('Feedback submitted');
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Clear all messages
  clearMessages: () => set({ messages: [], currentThread: null }),

  // Save current chat before logout
  saveBeforeLogout: async () => {
    const { messages, currentThread } = get();
    
    if (messages.length === 0) {
      console.log('ℹ️ No messages to save before logout');
      return { success: true, saved: false };
    }
    
    try {
      console.log('💾 Saving current chat before logout...');
      
      // If there's an active thread, update its title
      if (currentThread?.thread_id) {
        const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
        
        if (token) {
          // Generate title from first user message
          const firstUserMsg = messages.find(m => m.role === 'user');
          const title = firstUserMsg 
            ? firstUserMsg.content.substring(0, 50) + (firstUserMsg.content.length > 50 ? '...' : '')
            : 'Conversation';
          
          await chatService.updateThreadTitle(currentThread.thread_id, title);
          console.log(`✅ Chat saved: "${title}"`);
        }
      }
      
      return { success: true, saved: true };
    } catch (error) {
      console.error('⚠️ Error saving chat before logout:', error);
      // Don't block logout on save error
      return { success: true, saved: false };
    }
  }
  ,
  // Save / update current thread title explicitly
  saveThreadTitle: async () => {
    const { messages, currentThread } = get();
    if (!currentThread?.thread_id || messages.length === 0) return;
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token');
    if (!token) return;
    const firstUserMsg = messages.find(m => m.role === 'user');
    const title = firstUserMsg
      ? firstUserMsg.content.substring(0, 50) + (firstUserMsg.content.length > 50 ? '...' : '')
      : 'Conversation';
    try {
      await chatService.updateThreadTitle(currentThread.thread_id, title);
      set({ currentThread: { ...currentThread, title } });
    } catch (e) {
      console.warn('Failed to save thread title', e);
    }
  }
}));

export const useChat = () => {
  const store = useChatStore();
  return store;
};