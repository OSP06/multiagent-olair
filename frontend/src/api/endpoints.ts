// API endpoint paths

const API_ENDPOINTS = {
  CHAT: "/chat",
  UPLOAD_DOCS: "/upload_docs",
  CREATE_USER: "/crm/create_user",
  UPDATE_USER: "/crm/update_user",
  GET_CONVERSATIONS: (userId: string) => `/crm/conversations/${userId}`,
  RESET: "/reset",
};

export default API_ENDPOINTS;
export {};
