import React, { useState, useRef, useEffect } from 'react'

const QUICK_ACTIONS = [
  'Evaluate this job description',
  'Generate a cover letter',
  'Prep me for an interview',
  'Optimize my resume',
]

export default function AiChatPanel({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      model: 'Kimi K2.5',
      text: "Hi Vinay! I'm your Career-Ops AI assistant powered by Kimi. I can help you evaluate jobs, generate cover letters, prep for interviews, and optimize your resume. What would you like to do?",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [isOpen])

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return

    const userMsg = { role: 'user', text: text.trim() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim() }),
      })

      if (res.ok) {
        const data = await res.json()
        setMessages((prev) => [
          ...prev,
          { role: 'ai', model: data.model || 'Kimi', text: data.response },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          { role: 'ai', model: 'System', text: 'Sorry, I could not process that request. Make sure the FastAPI backend and LiteLLM proxy are running.' },
        ])
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', model: 'System', text: 'Connection error — backend offline. Start it with: python career_ops_api.py' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <>
      {isOpen && <div className="chat-overlay" onClick={onClose} />}
      <div className={`chat-drawer ${isOpen ? 'open' : ''}`} id="ai-chat-drawer">
        {/* Header */}
        <div className="chat-drawer-header">
          <h3>
            <span className="material-symbols-outlined">smart_toy</span>
            Kimi AI Assistant
          </h3>
          <button className="chat-drawer-close" onClick={onClose} aria-label="Close chat">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Quick Actions */}
        <div className="chat-quick-actions">
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action}
              className="chat-quick-btn"
              onClick={() => sendMessage(action)}
              disabled={loading}
            >
              {action}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-msg ${msg.role}`}>
              {msg.role === 'ai' && <div className="msg-model">{msg.model}</div>}
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="chat-typing">
              <span /><span /><span />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form className="chat-input-area" onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask Kimi anything about your job search..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="chat-send-btn" disabled={!input.trim() || loading}>
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>send</span>
          </button>
        </form>
      </div>
    </>
  )
}
