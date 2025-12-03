import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'prism-react-renderer'
import { FaUser, FaRobot, FaCopy, FaVolumeUp, FaCheck } from 'react-icons/fa'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

import voiceService from '@services/voiceService'
import './ChatMessage.css'

const ChatMessage = ({ message }) => {
  const [copied, setCopied] = useState(false)
  const [speaking, setSpeaking] = useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast.error('Failed to copy')
    }
  }

  const handleSpeak = async () => {
    if (speaking) {
      voiceService.stopSpeaking()
      setSpeaking(false)
    } else {
      setSpeaking(true)
      await voiceService.textToSpeech(message.content)
      setSpeaking(false)
    }
  }

  const renderContent = () => {
    if (message.role === 'user') {
      return <div className="message-text">{message.content}</div>
    }

    return (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        className="message-markdown"
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            return !inline && match ? (
              <div className="code-block">
                <div className="code-header">
                  <span>{match[1]}</span>
                  <button onClick={copyToClipboard} className="copy-code-btn">
                    {copied ? <FaCheck /> : <FaCopy />}
                  </button>
                </div>
                <SyntaxHighlighter
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            )
          }
        }}
      >
        {message.content}
      </ReactMarkdown>
    )
  }

  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-avatar">
        {message.role === 'user' ? (
          <FaUser />
        ) : message.role === 'assistant' ? (
          <FaRobot />
        ) : (
          <span>!</span>
        )}
      </div>
      
      <div className="message-content">
        <div className="message-header">
          <span className="message-role">
            {message.role === 'user' ? 'You' : 
             message.role === 'assistant' ? 'Morgan AI' : 
             'System'}
          </span>
          <span className="message-time">
            {format(new Date(message.timestamp), 'h:mm a')}
          </span>
        </div>
        
        {renderContent()}
        
        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <span className="sources-label">Sources:</span>
            {message.sources.map((source, index) => (
              <span key={index} className="source-item">
                {source}
              </span>
            ))}
          </div>
        )}
        
        <div className="message-actions">
          {message.role === 'assistant' && (
            <>
              <button
                onClick={handleSpeak}
                className="action-btn"
                title={speaking ? 'Stop speaking' : 'Read aloud'}
              >
                <FaVolumeUp className={speaking ? 'speaking' : ''} />
              </button>
              <button
                onClick={copyToClipboard}
                className="action-btn"
                title="Copy message"
              >
                {copied ? <FaCheck /> : <FaCopy />}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage