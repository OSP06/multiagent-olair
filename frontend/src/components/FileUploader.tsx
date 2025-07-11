"use client"

import type React from "react"
import { useState, useRef } from "react"
import styles from "./file-uploader.module.css"

interface FileUploaderProps {
  onUpload: (file: File) => void
}

export default function FileUploader({ onUpload }: FileUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      const allowedTypes = ["application/pdf", "text/plain"]
      if (allowedTypes.includes(file.type)) {
        setSelectedFile(file)
      } else {
        alert("Please select a PDF or TXT file only.")
        // Clear the input
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
      }
    }
  }

  const handleUploadClick = () => {
    if (selectedFile) {
      onUpload(selectedFile)
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const handleClear = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.uploadArea}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,application/pdf,text/plain"
          onChange={handleFileSelect}
          className={styles.hiddenInput}
        />

        <div className={styles.uploadContent}>
          <div className={styles.uploadIcon}>📁</div>
          <p className={styles.uploadText}>{selectedFile ? "File selected" : "Choose a PDF or TXT file"}</p>
          <button type="button" onClick={handleBrowseClick} className={styles.browseButton}>
            Browse Files
          </button>
        </div>
      </div>

      {selectedFile && (
        <div className={styles.fileInfo}>
          <div className={styles.fileName}>
            <span className={styles.fileIcon}>📄</span>
            <span className={styles.fileNameText}>{selectedFile.name}</span>
            <button type="button" onClick={handleClear} className={styles.clearButton} title="Clear selection">
              ✕
            </button>
          </div>
          <div className={styles.fileSize}>{(selectedFile.size / 1024).toFixed(1)} KB</div>
        </div>
      )}

      <div className={styles.actions}>
        <button
          type="button"
          onClick={handleUploadClick}
          disabled={!selectedFile}
          className={`${styles.uploadButton} ${!selectedFile ? styles.disabled : ""}`}
        >
          Upload File
        </button>
      </div>
    </div>
  )
}
