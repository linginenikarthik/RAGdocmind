import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import api from "../api/client";
import { addMessage } from "../features/chat/chatSlice";

function ChatSection() {
  const [question, setQuestion] = useState("");

  const dispatch = useDispatch();

  const documentId = useSelector(
    (state) => state.document.documentId
  );

  const messages = useSelector(
    (state) => state.chat.messages
  );

  const askQuestion = async () => {
    if (!question) return;

    dispatch(
      addMessage({
        role: "user",
        text: question,
      })
    );

    const res = await api.post("/documents/ask", {
      document_id: documentId,
      question: question,
    });

    dispatch(
      addMessage({
        role: "assistant",
        text: res.data.answer,
        pages: res.data.pages,
      })
    );

    setQuestion("");
  };

  return (
    <div className="chat-card">
      <h2>Ask Questions</h2>

      <div className="chat-window">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`bubble ${msg.role}`}
          >
            <p>{msg.text}</p>

            {msg.pages && (
              <small>
                Pages: {msg.pages.join(", ")}
              </small>
            )}
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          value={question}
          placeholder="Ask anything about the PDF..."
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button onClick={askQuestion}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatSection;