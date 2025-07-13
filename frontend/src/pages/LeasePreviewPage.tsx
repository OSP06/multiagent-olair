"use client"

import { useState, useEffect } from "react"
import api from "../api/axiosconfig"

interface LeaseRecord {
  [key: string]: string | number | null
}

const LeasePreviewPage = () => {
  const [leaseData, setLeaseData] = useState<LeaseRecord[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [selectedType, setSelectedType] = useState<"qa" | "property">("qa")
  const [searchTerm, setSearchTerm] = useState<string>("")
  const [currentPage, setCurrentPage] = useState<number>(1)
  const itemsPerPage: number = 10

  useEffect(() => {
    fetchLeaseData()
  }, [selectedType])

  const fetchLeaseData = async () => {
    setIsLoading(true)
    try {
      const response = await api.get<LeaseRecord[]>(`/api/routes/crm/leases?type=${selectedType}`)
      setLeaseData(response.data)
      setCurrentPage(1)
    } catch (error) {
      console.error("Failed to fetch lease data:", error)
      setLeaseData([])
    } finally {
      setIsLoading(false)
    }
  }

  const filteredData = leaseData.filter((item) =>
    !searchTerm ||
    Object.values(item).some((value) =>
      String(value).toLowerCase().includes(searchTerm.toLowerCase())
    )
  )

  const totalPages = Math.ceil(filteredData.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage)

  const renderTable = () => {
    if (!paginatedData.length) return null
    const headers = Object.keys(paginatedData[0])

    return (
      <div className="table-container">
        <div style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                {headers.map((header) => (
                  <th key={header}>{header.replace(/_/g, " ").toUpperCase()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, index) => (
                <tr key={index}>
                  {headers.map((header) => (
                    <td key={header}>
                      <div className="cell-content">
                        {String(row[header] || "").substring(0, 100)}
                        {String(row[header] || "").length > 100 ? "..." : ""}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              Previous
            </button>

            <span className="pagination-info">
              Page {currentPage} of {totalPages} ({filteredData.length} total records)
            </span>

            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="lease-preview-page">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">Lease Data Preview</h1>
          <p className="card-subtitle">View and search through lease analysis data</p>
        </div>

        <div className="controls">
          <div className="data-type-selector">
            <button
              className={`btn ${selectedType === "qa" ? "btn-primary" : "btn-secondary"} btn-sm`}
              onClick={() => setSelectedType("qa")}
            >
              Q&A Data
            </button>
            <button
              className={`btn ${selectedType === "property" ? "btn-primary" : "btn-secondary"} btn-sm`}
              onClick={() => setSelectedType("property")}
            >
              Property Data
            </button>
          </div>

          <div className="search-container">
            <input
              type="text"
              className="form-input search-input"
              placeholder="Search data..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setCurrentPage(1)
              }}
            />
          </div>
        </div>

        <div className="data-container">
          {isLoading ? (
            <div className="loading">
              <div className="spinner"></div>
              Loading {selectedType} data...
            </div>
          ) : leaseData.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h3>No data available</h3>
              <p>No {selectedType} data found. Upload some CSV files to see data here.</p>
            </div>
          ) : filteredData.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">🔍</div>
              <h3>No results found</h3>
              <p>No data matches your search term "{searchTerm}".</p>
            </div>
          ) : (
            renderTable()
          )}
        </div>
      </div>
    </div>
  )
}

export default LeasePreviewPage