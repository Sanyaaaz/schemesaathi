import React, { useState, useEffect, useRef } from "react";

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ sender: string; text: string; type?: string; options?: string[] }[]>([]);
  const [input, setInput] = useState("");
  const [dropdownOptions, setDropdownOptions] = useState<string[]>([]);
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [messages]);

  const handleSend = async (messageText?: string) => {
    const messageToSend = messageText || input;
    if (!messageToSend.trim()) return;

    if (messageToSend.toLowerCase() !== "start") {
      setMessages((prev) => [...prev, { sender: "user", text: messageToSend }]);
    }
    setDropdownVisible(false);

    try {
      const res = await fetch("http://127.0.0.1:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "user1", message: messageToSend }),
      });
      const data = await res.json();

      setMessages((prev) => [...prev, { sender: "bot", text: data.text, type: data.type, options: data.options }]);

      if (data.type === "dropdown" && Array.isArray(data.options)) {
        setDropdownOptions(data.options);
        setDropdownVisible(true);
      } else {
        setDropdownOptions([]);
        setDropdownVisible(false);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { sender: "bot", text: "⚠️ Could not reach backend" }]);
    }

    setInput("");
  };

  return (
    <div>
      {/* Floating button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 z-[9999]"
      >
        💬
      </button>

      {isOpen && (
        <div className="fixed bottom-20 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col z-[9999]">
          {/* Header */}
          <div className="bg-blue-600 text-white p-3 font-semibold flex justify-between">
            SchemeSathi
            <button onClick={() => setIsOpen(false)}>✖</button>
          </div>

          {/* Messages */}
          <div className="flex-1 p-3 overflow-y-auto space-y-2">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-2 rounded-lg max-w-[75%] ${
                  msg.sender === "user" ? "bg-blue-500 text-white ml-auto" : "bg-gray-200 text-gray-900"
                }`}
              >
                {msg.sender === "bot" && msg.text
                  ? msg.text.split("\n").map((line, i) => {
                      const trimmed = line.trim();
                      if (!trimmed) return null;
                      if (trimmed.startsWith("✅")) {
                        return (
                          <p key={i} className="font-semibold text-blue-700">
                            {trimmed}
                          </p>
                        );
                      } else if (trimmed.startsWith("⚠️")) {
                        return (
                          <p key={i} className="font-semibold text-red-600">
                            {trimmed}
                          </p>
                        );
                      } else if (
                        trimmed.startsWith("Eligibility:") ||
                        trimmed.startsWith("Details:") ||
                        trimmed.startsWith("Apply link:")
                      ) {
                        return (
                          <p key={i} className="ml-4">
                            {trimmed}
                          </p>
                        );
                      } else {
                        return <p key={i}>{trimmed}</p>;
                      }
                    })
                  : <p>{msg.text}</p>}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input / Dropdown */}
          <div className="p-2 border-t flex flex-col gap-2">
            {dropdownVisible ? (
              <select
                onChange={(e) => handleSend(e.target.value)}
                className="border rounded-lg p-2"
                defaultValue=""
              >
                <option value="" disabled>Select an option...</option>
                {dropdownOptions.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : (
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type your query or press Start..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  className="flex-1 border rounded-lg px-2 py-1"
                />
                <button onClick={() => handleSend()} className="bg-blue-600 text-white px-3 rounded-lg">
                  ➤
                </button>
                <button onClick={() => handleSend("Start")} className="bg-green-600 text-white px-3 rounded-lg">
                  Start
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
