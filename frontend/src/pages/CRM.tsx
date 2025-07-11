"use client"

import type React from "react"
import { useState } from "react"

interface User {
  id: number
  name: string
  email: string
  tags: string
}

interface FormData {
  name: string
  email: string
  tags: string
}

export default function CRMUserView() {
  const [users, setUsers] = useState<User[]>([
    { id: 1, name: "John Doe", email: "john@example.com", tags: "VIP, Premium" },
    { id: 2, name: "Jane Smith", email: "jane@example.com", tags: "New Customer" },
    { id: 3, name: "Bob Johnson", email: "bob@example.com", tags: "Enterprise, Priority" },
  ])

  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    tags: "",
  })

  const [editingId, setEditingId] = useState<number | null>(null)
  const [nextId, setNextId] = useState(4)
  const [showConfirm, setShowConfirm] = useState(false)
  const [confirmId, setConfirmId] = useState<number | null>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.name.trim() || !formData.email.trim()) {
      alert("Name and email are required")
      return
    }

    if (editingId) {
      setUsers((prev) => prev.map((user) => (user.id === editingId ? { ...user, ...formData } : user)))
      setEditingId(null)
    } else {
      const newUser: User = {
        id: nextId,
        ...formData,
      }
      setUsers((prev) => [...prev, newUser])
      setNextId((prev) => prev + 1)
    }

    setFormData({ name: "", email: "", tags: "" })
  }

  const handleEdit = (user: User) => {
    setFormData({
      name: user.name,
      email: user.email,
      tags: user.tags,
    })
    setEditingId(user.id)
  }

  const handleDelete = (id: number) => {
    setShowConfirm(true)
    setConfirmId(id)
  }

  const confirmDelete = () => {
    if (confirmId !== null) {
      setUsers((prev) => prev.filter((user) => user.id !== confirmId))
      if (editingId === confirmId) {
        setFormData({ name: "", email: "", tags: "" })
        setEditingId(null)
      }
    }
    setShowConfirm(false)
    setConfirmId(null)
  }

  const handleCancel = () => {
    setFormData({ name: "", email: "", tags: "" })
    setEditingId(null)
  }

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>CRM User Management</h1>

      {/* User Form */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "20px",
          marginBottom: "30px",
          backgroundColor: "#f9f9f9",
        }}
      >
        <h2>{editingId ? "Edit User" : "Add New User"}</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "15px" }}>
            <label htmlFor="name" style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Name *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              style={{
                width: "300px",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
              required
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label htmlFor="email" style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Email *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              style={{
                width: "300px",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
              required
            />
          </div>

          <div style={{ marginBottom: "15px" }}>
            <label htmlFor="tags" style={{ display: "block", marginBottom: "5px", fontWeight: "bold" }}>
              Tags
            </label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleInputChange}
              placeholder="e.g., VIP, Premium, New Customer"
              style={{
                width: "300px",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "4px",
              }}
            />
          </div>

          <div>
            <button
              type="submit"
              style={{
                padding: "10px 20px",
                backgroundColor: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                marginRight: "10px",
              }}
            >
              {editingId ? "Update User" : "Add User"}
            </button>

            {editingId && (
              <button
                type="button"
                onClick={handleCancel}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Users Table */}
      <div>
        <h2>Users ({users.length})</h2>
        {users.length === 0 ? (
          <p>No users found.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", border: "1px solid #ccc" }}>
            <thead>
              <tr style={{ backgroundColor: "#f0f0f0" }}>
                <th style={{ padding: "12px", border: "1px solid #ccc" }}>Name</th>
                <th style={{ padding: "12px", border: "1px solid #ccc" }}>Email</th>
                <th style={{ padding: "12px", border: "1px solid #ccc" }}>Tags</th>
                <th style={{ padding: "12px", border: "1px solid #ccc", textAlign: "center" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} style={{ backgroundColor: editingId === user.id ? "#fff3cd" : "white" }}>
                  <td style={{ padding: "12px", border: "1px solid #ccc" }}>{user.name}</td>
                  <td style={{ padding: "12px", border: "1px solid #ccc" }}>{user.email}</td>
                  <td style={{ padding: "12px", border: "1px solid #ccc" }}>{user.tags || "-"}</td>
                  <td style={{ padding: "12px", border: "1px solid #ccc", textAlign: "center" }}>
                    <button
                      onClick={() => handleEdit(user)}
                      style={{
                        padding: "6px 12px",
                        backgroundColor: "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        marginRight: "8px",
                        fontSize: "12px",
                      }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(user.id)}
                      style={{
                        padding: "6px 12px",
                        backgroundColor: "#dc3545",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "12px",
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Confirm Deletion Modal */}
      {showConfirm && (
        <div style={{
          position: "fixed",
          top: 0, left: 0, width: "100%", height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.4)",
          display: "flex", alignItems: "center", justifyContent: "center",
          zIndex: 1000,
        }}>
          <div style={{
            background: "white",
            padding: "30px",
            borderRadius: "8px",
            boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
            minWidth: "300px"
          }}>
            <h3 style={{ marginBottom: "20px" }}>Are you sure you want to delete this user?</h3>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button
                onClick={() => setShowConfirm(false)}
                style={{
                  marginRight: "10px",
                  padding: "8px 16px",
                  backgroundColor: "#6c757d",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer"
                }}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#dc3545",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer"
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
