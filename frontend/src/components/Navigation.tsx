import React from "react"
import { NavLink } from "react-router-dom"
import "./Navigation.css"

const Navigation: React.FC = () => {
  return (
    <nav className="navigation">
      <ul className="nav-list">
        <li>
          <NavLink to="/chat" className={({ isActive }) => isActive ? "active" : ""}>Chat</NavLink>
        </li>
        <li>
          <NavLink to="/upload" className={({ isActive }) => isActive ? "active" : ""}>Upload</NavLink>
        </li>
        <li>
          <NavLink to="/crm" className={({ isActive }) => isActive ? "active" : ""}>CRM</NavLink>
        </li>
        <li>
          <NavLink to="/lease-preview" className={({ isActive }) => isActive ? "active" : ""}>Lease Preview</NavLink>
        </li>
      </ul>
    </nav>
  )
}

export default Navigation
