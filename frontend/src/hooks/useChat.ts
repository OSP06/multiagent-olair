import { useState } from "react";

const useChat = () => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);

  const addMessage = (message: { role: string; content: string }) => {
    setMessages((prev) => [...prev, message]);
  };

  const resetChat = () => setMessages([]);

  return { messages, addMessage, resetChat };
};

export default useChat;
export {};
