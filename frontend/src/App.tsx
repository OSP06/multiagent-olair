import React, { useState } from "react";
import Home from "./pages/Home";
import CRM from "./pages/CRM";

type Page = "Home" | "CRM";

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>("Home");

  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "Arial, sans-serif" }}>
      {/* Sidebar Navigation */}
      <aside
        style={{
          width: "220px",
          backgroundColor: "#f0f0f0",
          padding: "1rem",
          borderRight: "1px solid #ccc",
        }}
      >
        <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>🔧 Tools</h2>
        <nav>
          <div
            style={{
              padding: "0.5rem",
              cursor: "pointer",
              backgroundColor: currentPage === "Home" ? "#e0f3ff" : "transparent",
              borderRadius: "4px",
              marginBottom: "0.5rem",
            }}
            onClick={() => setCurrentPage("Home")}
          >
            🏠 Home
          </div>
          <div
            style={{
              padding: "0.5rem",
              cursor: "pointer",
              backgroundColor: currentPage === "CRM" ? "#e0f3ff" : "transparent",
              borderRadius: "4px",
            }}
            onClick={() => setCurrentPage("CRM")}
          >
            👤 CRM
          </div>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: "2rem" }}>
        {currentPage === "Home" && <Home />}
        {currentPage === "CRM" && <CRM />}
      </main>
    </div>
  );
};

export default App;
