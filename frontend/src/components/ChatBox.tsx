"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"

// Define the message interface
export interface Message {
  id: string
  content: string
  sender: "user" | "bot"
  timestamp?: Date
}

// Define the component props
interface ChatBoxProps {
  messages: Message[]
  onSend: (message: string) => void
  placeholder?: string
  disabled?: boolean
  height?: string
}

// ChatBox Component
const ChatBox: React.FC<ChatBoxProps> = ({
  messages,
  onSend,
  placeholder = "Type your message...",
  disabled = false,
  height = "400px",
}) => {
  const [inputValue, setInputValue] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = () => {
    if (inputValue.trim() && !disabled) {
      onSend(inputValue.trim())
      setInputValue("")
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSend()
    }
  }

  const chatContainerStyle: React.CSSProperties = {
    display: "flex",
    flexDirection: "column",
    height,
    border: "1px solid #e0e0e0",
    borderRadius: "8px",
    backgroundColor: "#ffffff",
    fontFamily: "Arial, sans-serif",
    overflow: "hidden",
  }

  const messagesContainerStyle: React.CSSProperties = {
    flex: 1,
    overflowY: "auto",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    backgroundColor: "#f9f9f9",
  }

  const messageStyle = (sender: "user" | "bot"): React.CSSProperties => ({
    display: "flex",
    justifyContent: sender === "user" ? "flex-end" : "flex-start",
    marginBottom: "8px",
  })

  const bubbleStyle = (sender: "user" | "bot"): React.CSSProperties => ({
    maxWidth: "70%",
    padding: "12px 16px",
    borderRadius: "18px",
    backgroundColor: sender === "user" ? "#007bff" : "#e9ecef",
    color: sender === "user" ? "#ffffff" : "#333333",
    fontSize: "14px",
    lineHeight: "1.4",
    wordWrap: "break-word",
    boxShadow: "0 1px 2px rgba(0, 0, 0, 0.1)",
  })

  const inputContainerStyle: React.CSSProperties = {
    display: "flex",
    padding: "16px",
    borderTop: "1px solid #e0e0e0",
    backgroundColor: "#ffffff",
    gap: "8px",
  }

  const inputStyle: React.CSSProperties = {
    flex: 1,
    padding: "12px 16px",
    border: "1px solid #ddd",
    borderRadius: "24px",
    fontSize: "14px",
    outline: "none",
    backgroundColor: disabled ? "#f5f5f5" : "#ffffff",
    color: disabled ? "#999" : "#333",
  }

  const buttonStyle: React.CSSProperties = {
    padding: "12px 20px",
    backgroundColor: disabled || !inputValue.trim() ? "#ccc" : "#007bff",
    color: "#ffffff",
    border: "none",
    borderRadius: "24px",
    fontSize: "14px",
    fontWeight: "600",
    cursor: disabled || !inputValue.trim() ? "not-allowed" : "pointer",
    transition: "background-color 0.2s ease",
    minWidth: "60px",
  }

  return (
    <div style={chatContainerStyle}>
      {/* Messages Container */}
      <div style={messagesContainerStyle}>
        {messages.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              color: "#999",
              fontSize: "14px",
              marginTop: "20px",
            }}
          >
            No messages yet. Start a conversation!
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} style={messageStyle(message.sender)}>
              <div style={bubbleStyle(message.sender)}>{message.content}</div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Container */}
      <div style={inputContainerStyle}>
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          style={inputStyle}
        />
        <button onClick={handleSend} disabled={disabled || !inputValue.trim()} style={buttonStyle}>
          Send
        </button>
      </div>
    </div>
  )
}

// Demo Component
export default function ChatBoxDemo() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ])

  const handleSend = (message: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])

    // Simulate bot response after a delay
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `You said: "${message}". This is a demo response!`,
        sender: "bot",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
    }, 1000)
  }

  const containerStyle: React.CSSProperties = {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    minHeight: "100vh",
    backgroundColor: "#f0f2f5",
    padding: "20px",
  }

  const wrapperStyle: React.CSSProperties = {
    width: "100%",
    maxWidth: "600px",
    backgroundColor: "#ffffff",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
    overflow: "hidden",
  }

  const headerStyle: React.CSSProperties = {
    padding: "20px",
    backgroundColor: "#007bff",
    color: "#ffffff",
    textAlign: "center",
    fontSize: "18px",
    fontWeight: "600",
  }

  return (
    <div style={containerStyle}>
      <div style={wrapperStyle}>
        <div style={headerStyle}>ChatBox Demo</div>
        <div style={{ padding: "20px" }}>
          <ChatBox messages={messages} onSend={handleSend} placeholder="Type your message here..." height="500px" />
        </div>
      </div>
    </div>
  )
}

// Export the ChatBox component for reuse
export { ChatBox }
