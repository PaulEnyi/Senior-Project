import { useState, useEffect, useCallback, useRef } from 'react'
import { io } from 'socket.io-client'
import { WS_BASE_URL } from '../utils/constants'
import toast from 'react-hot-toast'

export const useWebSocket = (options = {}) => {
  const {
    url = WS_BASE_URL,
    autoConnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 1000,
    debug = false
  } = options

  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)
  const [messageHistory, setMessageHistory] = useState([])
  const [error, setError] = useState(null)
  const [reconnectCount, setReconnectCount] = useState(0)

  const socketRef = useRef(null)
  const eventHandlers = useRef({})
  const reconnectTimeoutRef = useRef(null)

  // Debug logging
  const log = useCallback((...args) => {
    if (debug) {
      console.log('[WebSocket]', ...args)
    }
  }, [debug])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      log('Already connected')
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      const token = localStorage.getItem('auth_token')
      
      const newSocket = io(url, {
        auth: {
          token
        },
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: reconnectAttempts,
        reconnectionDelay: reconnectDelay,
        reconnectionDelayMax: 5000,
        timeout: 20000
      })

      // Connection events
      newSocket.on('connect', () => {
        log('Connected to WebSocket')
        setIsConnected(true)
        setIsConnecting(false)
        setReconnectCount(0)
        setError(null)
      })

      newSocket.on('disconnect', (reason) => {
        log('Disconnected:', reason)
        setIsConnected(false)
        
        if (reason === 'io server disconnect') {
          // Server initiated disconnect, don't auto-reconnect
          setError('Server disconnected')
        }
      })

      newSocket.on('connect_error', (error) => {
        log('Connection error:', error.message)
        setIsConnecting(false)
        setError(error.message)
        
        // Handle reconnection
        if (reconnectCount < reconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectCount(prev => prev + 1)
            connect()
          }, reconnectDelay * Math.pow(2, reconnectCount))
        } else {
          toast.error('Failed to connect to real-time service')
        }
      })

      // Message events
      newSocket.on('message', (data) => {
        log('Message received:', data)
        const message = {
          ...data,
          timestamp: new Date().toISOString()
        }
        setLastMessage(message)
        setMessageHistory(prev => [...prev, message])
      })

      // Chat events
      newSocket.on('chat:message', (data) => {
        log('Chat message:', data)
        handleEvent('chat:message', data)
      })

      newSocket.on('chat:typing', (data) => {
        log('User typing:', data)
        handleEvent('chat:typing', data)
      })

      newSocket.on('chat:stream', (data) => {
        log('Stream chunk:', data)
        handleEvent('chat:stream', data)
      })

      // Voice events
      newSocket.on('voice:connected', (data) => {
        log('Voice connected:', data)
        handleEvent('voice:connected', data)
      })

      newSocket.on('voice:audio', (data) => {
        log('Voice audio received')
        handleEvent('voice:audio', data)
      })

      newSocket.on('voice:transcript', (data) => {
        log('Voice transcript:', data)
        handleEvent('voice:transcript', data)
      })

      // Admin events
      newSocket.on('admin:notification', (data) => {
        log('Admin notification:', data)
        handleEvent('admin:notification', data)
        toast.info(data.message)
      })

      newSocket.on('admin:stats', (data) => {
        log('Admin stats update:', data)
        handleEvent('admin:stats', data)
      })

      // Error events
      newSocket.on('error', (error) => {
        log('Socket error:', error)
        setError(error.message || 'WebSocket error occurred')
        handleEvent('error', error)
      })

      socketRef.current = newSocket
      setSocket(newSocket)
      
    } catch (error) {
      log('Failed to create socket:', error)
      setIsConnecting(false)
      setError(error.message)
    }
  }, [url, reconnectAttempts, reconnectDelay, reconnectCount, log])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      log('Disconnecting...')
      socketRef.current.disconnect()
      socketRef.current = null
      setSocket(null)
      setIsConnected(false)
      setIsConnecting(false)
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [log])

  // Send message
  const sendMessage = useCallback((event, data) => {
    if (!socketRef.current?.connected) {
      log('Cannot send message: not connected')
      setError('Not connected to server')
      return false
    }

    try {
      log('Sending message:', event, data)
      socketRef.current.emit(event, data)
      return true
    } catch (error) {
      log('Failed to send message:', error)
      setError(error.message)
      return false
    }
  }, [log])

  // Subscribe to events
  const on = useCallback((event, handler) => {
    if (!eventHandlers.current[event]) {
      eventHandlers.current[event] = []
    }
    eventHandlers.current[event].push(handler)
    
    // Also register with socket if connected
    if (socketRef.current) {
      socketRef.current.on(event, handler)
    }
    
    log('Subscribed to event:', event)
  }, [log])

  // Unsubscribe from events
  const off = useCallback((event, handler) => {
    if (eventHandlers.current[event]) {
      eventHandlers.current[event] = eventHandlers.current[event].filter(
        h => h !== handler
      )
    }
    
    // Also unregister from socket if connected
    if (socketRef.current) {
      socketRef.current.off(event, handler)
    }
    
    log('Unsubscribed from event:', event)
  }, [log])

  // Handle custom events
  const handleEvent = useCallback((event, data) => {
    const handlers = eventHandlers.current[event] || []
    handlers.forEach(handler => {
      try {
        handler(data)
      } catch (error) {
        console.error(`Error in event handler for ${event}:`, error)
      }
    })
  }, [])

  // Chat-specific methods
  const sendChatMessage = useCallback((message, threadId) => {
    return sendMessage('chat:message', {
      message,
      thread_id: threadId,
      timestamp: new Date().toISOString()
    })
  }, [sendMessage])

  const sendTypingIndicator = useCallback((threadId, isTyping = true) => {
    return sendMessage('chat:typing', {
      thread_id: threadId,
      is_typing: isTyping
    })
  }, [sendMessage])

  const joinChatRoom = useCallback((threadId) => {
    return sendMessage('chat:join', { thread_id: threadId })
  }, [sendMessage])

  const leaveChatRoom = useCallback((threadId) => {
    return sendMessage('chat:leave', { thread_id: threadId })
  }, [sendMessage])

  // Voice-specific methods
  const startVoiceSession = useCallback(() => {
    return sendMessage('voice:start', {
      timestamp: new Date().toISOString()
    })
  }, [sendMessage])

  const endVoiceSession = useCallback(() => {
    return sendMessage('voice:end', {
      timestamp: new Date().toISOString()
    })
  }, [sendMessage])

  const sendAudioChunk = useCallback((audioData) => {
    return sendMessage('voice:audio', {
      audio: audioData,
      timestamp: new Date().toISOString()
    })
  }, [sendMessage])

  // Admin-specific methods
  const subscribeToAdminEvents = useCallback(() => {
    return sendMessage('admin:subscribe', {
      events: ['stats', 'notifications', 'logs']
    })
  }, [sendMessage])

  const unsubscribeFromAdminEvents = useCallback(() => {
    return sendMessage('admin:unsubscribe', {})
  }, [sendMessage])

  // Clear message history
  const clearMessageHistory = useCallback(() => {
    setMessageHistory([])
    setLastMessage(null)
  }, [])

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, []) // Only run on mount/unmount

  // Re-register event handlers when socket reconnects
  useEffect(() => {
    if (socket && isConnected) {
      Object.entries(eventHandlers.current).forEach(([event, handlers]) => {
        handlers.forEach(handler => {
          socket.on(event, handler)
        })
      })
    }
  }, [socket, isConnected])

  return {
    // Connection state
    socket,
    isConnected,
    isConnecting,
    error,
    reconnectCount,
    
    // Messages
    lastMessage,
    messageHistory,
    
    // Core methods
    connect,
    disconnect,
    sendMessage,
    on,
    off,
    
    // Chat methods
    sendChatMessage,
    sendTypingIndicator,
    joinChatRoom,
    leaveChatRoom,
    
    // Voice methods
    startVoiceSession,
    endVoiceSession,
    sendAudioChunk,
    
    // Admin methods
    subscribeToAdminEvents,
    unsubscribeFromAdminEvents,
    
    // Utility methods
    clearMessageHistory
  }
}