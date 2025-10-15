import { useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessage = { role: "user", text: input };
    setMessages([...messages, newMessage]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/ask", {
        query: input,
      });
      const botMessage = { role: "assistant", text: response.data.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
    }
    setInput("");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-6">
      <motion.div
        className="w-full max-w-2xl bg-primary/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-primary/40"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-secondary mb-4 text-center drop-shadow-lg">
          Smart Support 🤖
        </h1>

        <div className="flex flex-col space-y-4 max-h-[70vh] overflow-y-auto mb-6 scrollbar-thin scrollbar-thumb-secondary/40 scrollbar-track-primary/10">
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              className={`p-3 rounded-xl max-w-[80%] ${
                msg.role === "user"
                  ? "bg-secondary/40 text-white self-end"
                  : "bg-primary/40 text-accent self-start"
              }`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {msg.text}
            </motion.div>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Введите вопрос..."
            className="flex-1 bg-primary/40 text-accent rounded-xl p-3 border border-secondary focus:ring-2 focus:ring-secondary focus:outline-none"
          />
          <button
            onClick={sendMessage}
            className="bg-secondary text-white px-4 py-2 rounded-xl hover:bg-blue-500 transition font-semibold"
          >
            Отправить
          </button>
        </div>
      </motion.div>
    </div>
  );
}
