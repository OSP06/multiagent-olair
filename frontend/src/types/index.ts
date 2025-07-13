import { useEffect, useState } from "react"
import api from "../api/axiosconfig"

const MyComponent = () => {
  const [health, setHealth] = useState<{ message: string } | null>(null)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await api.get("/api/routes/chat/health")
        setHealth(res.data)
      } catch (error) {
        console.error("Failed to fetch health", error)
      }
    }

    fetchHealth()
  }, [])

  // return <div>Backend Status: {health?.message || "Loading..."}</div>
}

export default MyComponent
