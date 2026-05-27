"use client";
import { useState, useEffect } from "react";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("auth") === "success") setAuthed(true);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("const res = await fetch("https://zoho-chatbot-1.onrender.com/chat", {", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, user_id: "default_user" })
      });
      const contentType = res.headers.get("content-type") || "";
      const payload = contentType.includes("application/json")
        ? await res.json()
        : { detail: await res.text() };

      if (!res.ok) {
        throw new Error(payload.detail || `Request failed with status ${res.status}`);
      }

      setMessages(prev => [...prev, { role: "bot", content: payload.response || "No response returned." }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "bot", content: error?.message || "Error connecting to backend." }]);
    }
    setLoading(false);
  };

  if (!authed) return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-4">Zoho Project Assistant</h1>
      <a href="http://localhost:8000/auth/login"
        className="bg-blue-600 px-6 py-3 rounded-lg hover:bg-blue-700">
        Login with Zoho
      </a>
    </div>
  );

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <div className="p-4 bg-gray-800 text-xl font-bold">Zoho Project Assistant</div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`px-4 py-2 rounded-lg max-w-lg ${m.role === "user" ? "bg-blue-600" : "bg-gray-700"}`}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-400">Thinking...</div>}
      </div>
      <div className="p-4 bg-gray-800 flex gap-2">
        <input
          className="flex-1 bg-gray-700 rounded-lg px-4 py-2 outline-none"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && sendMessage()}
          placeholder="Ask something..."
        />
        <button onClick={sendMessage}
          className="bg-blue-600 px-6 py-2 rounded-lg hover:bg-blue-700">
          Send
        </button>
      </div>
    </div>
  );
}