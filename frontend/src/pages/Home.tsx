"use client"

import type React from "react"
import { useState } from "react"

type AnalysisTool = "clause-analysis" | "semantic-search" | "summarize-lease" | "lease-chatbot"

interface AnalysisResult {
  tool: AnalysisTool
  content: string
  timestamp: Date
}

const LeaseAnalyzerDashboard: React.FC = () => {
  const [selectedTool, setSelectedTool] = useState<AnalysisTool>("clause-analysis")
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [chatInput, setChatInput] = useState("")

  const tools = [
    { id: "clause-analysis" as AnalysisTool, name: "Clause Analysis", icon: "📋" },
    { id: "semantic-search" as AnalysisTool, name: "Semantic Search", icon: "🔍" },
    { id: "summarize-lease" as AnalysisTool, name: "Summarize Lease", icon: "📄" },
    { id: "lease-chatbot" as AnalysisTool, name: "Lease Chatbot", icon: "💬" },
  ]

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && (file.type === "application/pdf" || file.type === "text/plain")) {
      setUploadedFile(file)
      setAnalysisResult(null)
    } else {
      alert("Please upload a PDF or TXT file")
    }
  }

  const handleAnalysis = async () => {
    if (!uploadedFile) {
      alert("Please upload a file first")
      return
    }

    setIsAnalyzing(true)

    // Simulate API call
    setTimeout(() => {
      const mockResults: Record<AnalysisTool, string> = {
        "clause-analysis": `Key clauses identified in ${uploadedFile.name}:
        
• Rent Payment: Monthly rent of $2,500 due on the 1st of each month
• Security Deposit: $5,000 refundable deposit required
• Lease Term: 12-month lease starting January 1, 2024
• Pet Policy: No pets allowed without written consent
• Maintenance: Tenant responsible for minor repairs under $100
• Termination: 30-day notice required for lease termination`,

        "semantic-search": `Semantic analysis results for ${uploadedFile.name}:
        
• Document contains 15 standard residential lease clauses
• Risk level: Medium (2 potentially problematic clauses identified)
• Compliance score: 85% with local housing regulations
• Similar lease patterns found in database
• Recommended review areas: subletting terms, early termination fees`,

        "summarize-lease": `Lease Summary for ${uploadedFile.name}:
        
Property: 123 Main Street, Apartment 4B
Tenant: [Name to be filled]
Landlord: ABC Property Management
Lease Period: 12 months (Jan 1, 2024 - Dec 31, 2024)
Monthly Rent: $2,500
Security Deposit: $5,000
Key Terms: Standard residential lease with no pet policy, tenant maintenance responsibilities, and 30-day termination notice requirement.`,

        "lease-chatbot": `I'm ready to answer questions about your lease document "${uploadedFile.name}". 

Some things I can help with:
• Explain specific clauses in plain language
• Compare terms with standard practices
• Identify potential issues or concerns
• Suggest questions to ask your landlord

What would you like to know about your lease?`,
      }

      setAnalysisResult({
        tool: selectedTool,
        content: mockResults[selectedTool],
        timestamp: new Date(),
      })
      setIsAnalyzing(false)
    }, 2000)
  }

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatInput.trim()) return

    const chatResponse = `Q: ${chatInput}

A: Based on your lease document, here's what I found: This is a simulated response to "${chatInput}". In a real implementation, this would analyze your specific lease document and provide detailed answers about the terms, conditions, and implications of your question.`

    setAnalysisResult({
      tool: "lease-chatbot",
      content: chatResponse,
      timestamp: new Date(),
    })
    setChatInput("")
  }

  const styles = {
    container: {
      display: "flex",
      height: "100vh",
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: "#f8f9fa",
    },
    sidebar: {
      width: "280px",
      backgroundColor: "#ffffff",
      borderRight: "1px solid #e9ecef",
      padding: "24px",
      display: "flex",
      flexDirection: "column" as const,
    },
    logo: {
      fontSize: "24px",
      fontWeight: "bold",
      color: "#2c3e50",
      marginBottom: "32px",
      display: "flex",
      alignItems: "center",
      gap: "8px",
    },
    toolsList: {
      listStyle: "none",
      padding: 0,
      margin: 0,
    },
    toolItem: {
      marginBottom: "8px",
    },
    toolButton: (isActive: boolean) => ({
      width: "100%",
      padding: "12px 16px",
      border: "none",
      borderRadius: "8px",
      backgroundColor: isActive ? "#e3f2fd" : "transparent",
      color: isActive ? "#1976d2" : "#495057",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: isActive ? "600" : "400",
      display: "flex",
      alignItems: "center",
      gap: "12px",
      transition: "all 0.2s ease",
      textAlign: "left" as const,
    }),
    mainContent: {
      flex: 1,
      display: "flex",
      flexDirection: "column" as const,
      overflow: "hidden",
    },
    header: {
      backgroundColor: "#ffffff",
      borderBottom: "1px solid #e9ecef",
      padding: "24px 32px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    },
    headerTitle: {
      fontSize: "20px",
      fontWeight: "600",
      color: "#2c3e50",
      margin: 0,
    },
    content: {
      flex: 1,
      padding: "32px",
      overflow: "auto",
    },
    uploadSection: {
      backgroundColor: "#ffffff",
      border: "2px dashed #dee2e6",
      borderRadius: "12px",
      padding: "32px",
      textAlign: "center" as const,
      marginBottom: "24px",
    },
    uploadInput: {
      display: "none",
    },
    uploadButton: {
      backgroundColor: "#007bff",
      color: "white",
      border: "none",
      padding: "12px 24px",
      borderRadius: "6px",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: "500",
    },
    fileInfo: {
      backgroundColor: "#d4edda",
      border: "1px solid #c3e6cb",
      borderRadius: "6px",
      padding: "12px",
      marginTop: "16px",
      color: "#155724",
    },
    analyzeButton: {
      backgroundColor: "#28a745",
      color: "white",
      border: "none",
      padding: "12px 32px",
      borderRadius: "6px",
      cursor: "pointer",
      fontSize: "16px",
      fontWeight: "500",
      marginTop: "16px",
      disabled: isAnalyzing,
    },
    chatForm: {
      display: "flex",
      gap: "12px",
      marginBottom: "24px",
    },
    chatInput: {
      flex: 1,
      padding: "12px",
      border: "1px solid #ced4da",
      borderRadius: "6px",
      fontSize: "14px",
    },
    chatButton: {
      backgroundColor: "#007bff",
      color: "white",
      border: "none",
      padding: "12px 24px",
      borderRadius: "6px",
      cursor: "pointer",
      fontSize: "14px",
    },
    resultPanel: {
      backgroundColor: "#ffffff",
      border: "1px solid #e9ecef",
      borderRadius: "12px",
      padding: "24px",
      minHeight: "300px",
    },
    resultHeader: {
      fontSize: "18px",
      fontWeight: "600",
      color: "#2c3e50",
      marginBottom: "16px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    },
    resultContent: {
      fontSize: "14px",
      lineHeight: "1.6",
      color: "#495057",
      whiteSpace: "pre-line" as const,
    },
    timestamp: {
      fontSize: "12px",
      color: "#6c757d",
    },
    loading: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      height: "200px",
      color: "#6c757d",
    },
  }

  return (
    <div style={styles.container}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.logo}>📊 Lease Analyzer</div>

        <ul style={styles.toolsList}>
          {tools.map((tool) => (
            <li key={tool.id} style={styles.toolItem}>
              <button
                style={styles.toolButton(selectedTool === tool.id)}
                onClick={() => setSelectedTool(tool.id)}
                onMouseEnter={(e) => {
                  if (selectedTool !== tool.id) {
                    e.currentTarget.style.backgroundColor = "#f8f9fa"
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedTool !== tool.id) {
                    e.currentTarget.style.backgroundColor = "transparent"
                  }
                }}
              >
                <span>{tool.icon}</span>
                {tool.name}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Main Content */}
      <div style={styles.mainContent}>
        <header style={styles.header}>
          <h1 style={styles.headerTitle}>{tools.find((t) => t.id === selectedTool)?.name}</h1>
        </header>

        <div style={styles.content}>
          {/* File Upload Section */}
          <div style={styles.uploadSection}>
            <h3>Upload Lease Document</h3>
            <p>Upload a PDF or TXT file to analyze</p>

            <input
              type="file"
              id="file-upload"
              accept=".pdf,.txt"
              onChange={handleFileUpload}
              style={styles.uploadInput}
            />

            <label htmlFor="file-upload">
              <button style={styles.uploadButton} onClick={() => document.getElementById("file-upload")?.click()}>
                Choose File
              </button>
            </label>

            {uploadedFile && (
              <div style={styles.fileInfo}>
                ✅ File uploaded: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
              </div>
            )}

            {uploadedFile && (
              <button
                style={{
                  ...styles.analyzeButton,
                  opacity: isAnalyzing ? 0.6 : 1,
                  cursor: isAnalyzing ? "not-allowed" : "pointer",
                }}
                onClick={handleAnalysis}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? "Analyzing..." : `Run ${tools.find((t) => t.id === selectedTool)?.name}`}
              </button>
            )}
          </div>

          {/* Chat Input for Chatbot Tool */}
          {selectedTool === "lease-chatbot" && uploadedFile && (
            <form onSubmit={handleChatSubmit} style={styles.chatForm}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask a question about your lease..."
                style={styles.chatInput}
              />
              <button type="submit" style={styles.chatButton}>
                Ask
              </button>
            </form>
          )}

          {/* Results Panel */}
          <div style={styles.resultPanel}>
            <div style={styles.resultHeader}>
              <span>Analysis Results</span>
              {analysisResult && <span style={styles.timestamp}>{analysisResult.timestamp.toLocaleTimeString()}</span>}
            </div>

            {isAnalyzing ? (
              <div style={styles.loading}>
                <div>🔄 Analyzing your lease document...</div>
              </div>
            ) : analysisResult ? (
              <div style={styles.resultContent}>{analysisResult.content}</div>
            ) : (
              <div style={styles.resultContent}>
                Upload a lease document and click "Run {tools.find((t) => t.id === selectedTool)?.name}" to see results
                here.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Page() {
  return <LeaseAnalyzerDashboard />
}
