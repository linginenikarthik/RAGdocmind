function MessageBubble({ msg }) {
  return (
    <div className={`bubble ${msg.role}`}>
      <p>{msg.text}</p>

      {msg.pages && (
        <small>📄 Page: {msg.pages.join(", ")}</small>
      )}
    </div>
  );
}

export default MessageBubble;