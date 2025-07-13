import { useState, useEffect, useRef } from "react"
import { useParams } from "react-router-dom"
import api from "../api/axiosconfig"
import "./ChatPage.css"

interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: Date
  isError?: boolean
}

interface SystemHealth {
  status: string
}

const ChatPage = () => {
  const { userId } = useParams<{ userId: string }>()
  const numericUserId = Number(userId || 0)

  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [chatMode, setChatMode] = useState<"general" | "internal">("general")
  const [internalKBType, setInternalKBType] = useState<"qa" | "property" | "master_clauses">("qa")

  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchSystemHealth()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const fetchSystemHealth = async () => {
    try {
      const res = await api.get("/api/routes/chat/health")
      setSystemHealth(res.data)
    } catch (e) {
      console.error("Health fetch failed", e)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMsg: Message = { role: "user", content: inputMessage, timestamp: new Date() }
    setMessages((prev) => [...prev, userMsg])
    setInputMessage("")
    setIsLoading(true)

    try {
      const endpoint = chatMode === "internal" ? "/api/routes/chat/internal" : "/api/routes/chat"

      const payload =
        chatMode === "internal"
          ? {
              question: inputMessage,
              kb_type: internalKBType,
              top_k: 3,
              use_llm: true,
            }
          : {
              question: inputMessage,
              user_id: numericUserId,
              source: "auto", // could also be "internal" or "lease"
              top_k: 3,
            }

      const res = await api.post(endpoint, payload)
      const aiMsg: Message = {
        role: "assistant",
        content: res.data.answer || res.data.message,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch {
      const errorMsg: Message = {
        role: "assistant",
        content: "❌ Error processing your message.",
        timestamp: new Date(),
        isError: true,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1>AI Chat Assistant</h1>
        <div>Status: {systemHealth?.status || "Checking..."}</div>

        <div className="chat-mode-toggle">
          <button
            onClick={() => setChatMode("general")}
            className={chatMode === "general" ? "active" : ""}
          >
            General Chat
          </button>
          <button
            onClick={() => setChatMode("internal")}
            className={chatMode === "internal" ? "active" : ""}
          >
            Internal KB
          </button>
        </div>

        {chatMode === "internal" && (
          <div className="kb-type-toggle">
            <span>KB Type: </span>
            {["qa", "property", "master_clauses"].map((type) => (
              <button
                key={type}
                onClick={() => setInternalKBType(type as "qa" | "property" | "master_clauses")}
                className={internalKBType === type ? "active" : ""}
              >
                {type}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="chat-body">
        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.role} ${m.isError ? "error" : ""}`}>
            <div>{m.content}</div>
            <span>{m.timestamp.toLocaleTimeString()}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          rows={2}
          disabled={isLoading}
        />
        <button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatPage
