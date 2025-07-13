import axios from "axios"

const api = axios.create({
  baseURL: "http://localhost:8000", // ✅ correct FastAPI backend
  withCredentials: false,
})

export default api
