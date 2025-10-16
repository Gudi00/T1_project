import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [displayedAnswer, setDisplayedAnswer] = useState("");
  const typingInterval = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);
    setDisplayedAnswer("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", { query: input });
const answer = `
Ответ: ${response.data.answer || "нет данных"}

Категория: ${response.data.category || "не указана"}

Подкатегория: ${response.data.subcategory || "не указана"}

`.trim();
      let i = 0;
      typingInterval.current = setInterval(() => {
        setDisplayedAnswer(answer.slice(0, i + 1));
        i++;
        if (i >= answer.length) {
          clearInterval(typingInterval.current);
          setIsTyping(false);
          setMessages((prev) => [...prev, { sender: "bot", text:answer}]);
        }
      }, 25);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Ошибка подключения к серверу." },
      ]);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    return () => clearInterval(typingInterval.current);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0f0a] to-[#0f2413] flex flex-col items-center justify-between p-6 text-[#d4ffd4] font-mono">
      <div className="w-full max-w-3xl flex flex-col flex-1 overflow-y-auto space-y-4 mb-6 p-4 rounded-2xl bg-[#101a10] shadow-lg">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-3 rounded-xl max-w-[75%] ${
              msg.sender === "user"
                ? "self-end bg-[#1e3d1e] text-green-100"
                : "self-start bg-[#183318] text-green-200"
            }`}
          >
            {msg.text}
          </div>
        ))}

        {isTyping && (
          <div className="self-start p-3 rounded-xl bg-[#183318] text-green-200 animate-pulse">
            {displayedAnswer || "▌"}
          </div>
        )}
      </div>

      <div className="w-full max-w-3xl flex items-center space-x-2">
        <textarea
          className="flex-1 p-3 rounded-xl bg-[#0f1b0f] text-green-100 placeholder-green-700 resize-none focus:outline-none focus:ring-2 focus:ring-green-600"
          rows="2"
          placeholder="Введите сообщение..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <button
          onClick={sendMessage}
          className="px-6 py-3 rounded-xl bg-green-700 hover:bg-green-600 text-black font-bold transition"
        >
          ➤
        </button>
      </div>
    </div>
  );
}
