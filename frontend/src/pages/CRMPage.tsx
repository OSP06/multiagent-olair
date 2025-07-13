import { useState, useEffect } from "react"
import api from "../api/axiosconfig"
import "./CRMPage.css"

interface User {
  id: number
  name: string
  email: string
  role: string
}

interface Conversation {
  id: number
  user_id: number
  user_name?: string
  created_at: string
  preview?: string
}

const CRMPage = () => {
  const [users, setUsers] = useState<User[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [userConversations, setUserConversations] = useState<Conversation[]>([])
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<"users" | "conversations">("users")
  const [isLoading, setIsLoading] = useState(false)
  const [showUserForm, setShowUserForm] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "",
  })

  useEffect(() => {
    activeTab === "users" ? fetchUsers() : fetchConversations()
  }, [activeTab])

  const fetchUsers = async () => {
    setIsLoading(true)
    try {
      const res = await api.get<User[]>("/api/routes/crm/users")
      setUsers(res.data)
    } catch (e) {
      console.error("Failed to fetch users", e)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchConversations = async () => {
    setIsLoading(true)
    try {
      const res = await api.get<Conversation[]>("/api/routes/crm/conversations")
      setConversations(res.data)
    } catch (e) {
      console.error("Failed to fetch conversations", e)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchUserConversations = async (userId: number) => {
    try {
      const res = await api.get<Conversation[]>(`/api/routes/crm/users/${userId}/conversations`)
      setUserConversations(res.data)
      setSelectedUserId(userId)
    } catch (e) {
      console.error("Failed to fetch user conversations", e)
    }
  }

  const handleSubmitUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      editingUser
        ? await api.put(`/api/routes/crm/users/${editingUser.id}`, formData)
        : await api.post("/api/routes/crm/users", formData)

      setFormData({ name: "", email: "", role: "" })
      setEditingUser(null)
      setShowUserForm(false)
      fetchUsers()
    } catch (e) {
      console.error("Failed to save user", e)
    }
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setFormData({ name: user.name, email: user.email, role: user.role })
    setShowUserForm(true)
  }

  const handleDeleteUser = async (userId: number) => {
    if (window.confirm("Delete this user?")) {
      await api.delete(`/api/routes/crm/users/${userId}`)
      fetchUsers()
    }
  }

  const handleDeleteConversation = async (conversationId: number) => {
    await api.delete(`/api/routes/crm/conversations/${conversationId}`)
    activeTab === "users" && selectedUserId
      ? fetchUserConversations(selectedUserId)
      : fetchConversations()
  }

  return (
    <div className="crm-page">
      <div className="tab-navigation">
        <button onClick={() => setActiveTab("users")} className={activeTab === "users" ? "active" : ""}>Users</button>
        <button onClick={() => setActiveTab("conversations")} className={activeTab === "conversations" ? "active" : ""}>Conversations</button>
      </div>

      {activeTab === "users" && (
        <div className="users-section">
          <button className="add-user-btn" onClick={() => setShowUserForm(true)}>➕ Add User</button>
          {users.map((user) => (
            <div key={user.id} className="user-card">
              <strong>{user.name}</strong> ({user.email})
              <div className="user-actions">
                <button onClick={() => fetchUserConversations(user.id)}>📄 View</button>
                <button onClick={() => handleEditUser(user)}>✏️ Edit</button>
                <button onClick={() => handleDeleteUser(user.id)}>🗑️ Delete</button>
              </div>
            </div>
          ))}

          {userConversations.map((convo) => (
            <div key={convo.id} className="conversation-card">
              <strong>Conversation #{convo.id}</strong> – {convo.preview || "No preview"}
              <button onClick={() => handleDeleteConversation(convo.id)}>🗑️ Delete</button>
            </div>
          ))}
        </div>
      )}

      {activeTab === "conversations" && (
        <div className="conversations-section">
          {conversations.map((convo) => (
            <div key={convo.id} className="conversation-card">
              <strong>#{convo.id}</strong> – {convo.preview || "No preview"}
              <button onClick={() => handleDeleteConversation(convo.id)}>🗑️ Delete</button>
            </div>
          ))}
        </div>
      )}

      {showUserForm && (
        <form onSubmit={handleSubmitUser} className="user-form">
          <input
            placeholder="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <input
            placeholder="Role"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
          />
          <div className="form-actions">
            <button type="submit">{editingUser ? "Update" : "Add"} User</button>
            <button type="button" onClick={() => setShowUserForm(false)}>Cancel</button>
          </div>
        </form>
      )}
    </div>
  )
}

export default CRMPage