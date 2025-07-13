"use client"

import { useState, useEffect } from "react"
import api from "../api/axiosconfig"

const UploadPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [sampleData, setSampleData] = useState<Record<string, any[]>>({})
  const [selectedDataType, setSelectedDataType] = useState<"qa" | "property">("qa")
  const [isLoadingSample, setIsLoadingSample] = useState(false)

  useEffect(() => {
    fetchSampleData()
  }, [selectedDataType])

  const fetchSampleData = async () => {
    setIsLoadingSample(true)
    try {
      const response = await api.get(`/api/routes/upload/internal-knowledge?type=${selectedDataType}`)
      setSampleData((prev) => ({
        ...prev,
        [selectedDataType]: response.data.sample || [],
      }))
    } catch (error) {
      console.error("Failed to fetch sample data:", error)
    } finally {
      setIsLoadingSample(false)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    setSelectedFile(file)
    setUploadStatus("")
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("Please select a file first.")
      return
    }

    setIsUploading(true)
    setUploadStatus("")

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      await api.post("/api/routes/upload/docs", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })

      setUploadStatus("File uploaded successfully!")
      setSelectedFile(null)

      const fileInput = document.getElementById("file-input") as HTMLInputElement
      if (fileInput) fileInput.value = ""
    } catch (error) {
      setUploadStatus("Upload failed. Please try again.")
      console.error("Upload error:", error)
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
  }

  const renderSampleData = () => {
    const data = sampleData[selectedDataType]
    if (!data || !data.length) return null

    const headers = Object.keys(data[0])
    const sampleRows = data.slice(0, 5)

    return (
      <div style={{ overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              {headers.map((header) => (
                <th key={header}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sampleRows.map((row, index) => (
              <tr key={index}>
                {headers.map((header) => (
                  <td key={header}>
                    {String(row[header] || "").substring(0, 100)}
                    {String(row[header] || "").length > 100 ? "..." : ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {data.length > 5 && (
          <p style={{ marginTop: "1rem", color: "#64748b", fontSize: "0.875rem" }}>
            Showing 5 of {data.length} records
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="upload-page">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Upload Documents</h1>
          <p className="card-subtitle">Upload CSV files to update the internal knowledge base</p>
        </div>

        <div className="upload-section">
          <div className="form-group">
            <label className="form-label">Select CSV File</label>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="form-input"
              disabled={isUploading}
            />
          </div>

          {selectedFile && (
            <div className="file-info">
              <div className="file-details">
                <div><strong>File:</strong> {selectedFile.name}</div>
                <div><strong>Size:</strong> {formatFileSize(selectedFile.size)}</div>
                <div><strong>Type:</strong> {selectedFile.type || "text/csv"}</div>
              </div>
            </div>
          )}

          <button className="btn btn-primary" onClick={handleUpload} disabled={!selectedFile || isUploading}>
            {isUploading ? (
              <>
                <div className="spinner"></div>
                Uploading...
              </>
            ) : (
              "Upload File"
            )}
          </button>

          {uploadStatus && (
            <div className={`upload-status ${uploadStatus.includes("success") ? "success" : "error"}`}>
              {uploadStatus}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Sample Knowledge Base Data</h2>
          <p className="card-subtitle">Preview existing data in the knowledge base</p>
        </div>

        <div className="data-type-selector">
          <button
            className={`btn ${selectedDataType === "qa" ? "btn-primary" : "btn-secondary"} btn-sm`}
            onClick={() => setSelectedDataType("qa")}
          >
            Q&A Data
          </button>
          <button
            className={`btn ${selectedDataType === "property" ? "btn-primary" : "btn-secondary"} btn-sm`}
            onClick={() => setSelectedDataType("property")}
          >
            Property Data
          </button>
        </div>

        <div className="sample-data-container">
          {isLoadingSample ? (
            <div className="loading">
              <div className="spinner"></div>
              Loading sample data...
            </div>
          ) : sampleData[selectedDataType] && sampleData[selectedDataType].length > 0 ? (
            renderSampleData()
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h3>No data available</h3>
              <p>No {selectedDataType} data found in the knowledge base.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default UploadPage