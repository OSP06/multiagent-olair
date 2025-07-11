import React from "react"

type ConfirmModalProps = {
  message: string
  onConfirm: () => void
  onCancel: () => void
}

const ConfirmModal: React.FC<ConfirmModalProps> = ({ message, onConfirm, onCancel }) => {
  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <p>{message}</p>
        <div style={styles.buttonGroup}>
          <button onClick={onConfirm} style={{ ...styles.button, backgroundColor: "#d9534f", color: "white" }}>
            Confirm
          </button>
          <button onClick={onCancel} style={styles.button}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

const styles: { [key: string]: React.CSSProperties } = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh",
    backgroundColor: "rgba(0,0,0,0.3)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
  },
  modal: {
    background: "#fff",
    padding: "1.5rem",
    borderRadius: "8px",
    minWidth: "300px",
    textAlign: "center",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
  },
  buttonGroup: {
    marginTop: "1rem",
    display: "flex",
    justifyContent: "space-around",
  },
  button: {
    padding: "0.5rem 1rem",
    borderRadius: "4px",
    border: "none",
    cursor: "pointer",
  },
}

export default ConfirmModal