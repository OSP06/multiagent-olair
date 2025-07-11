// client.ts
import axios from "axios";

const client = axios.create({
  baseURL: "http://localhost:8000", // Replace with your FastAPI backend URL
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
export {};
