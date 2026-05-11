import ReactMarkdown from "react-markdown";
import { useState } from "react";

function Message({ msg, index, onFeedback, onTTS }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isBot = msg.role === "assistant";

  return (
    <div className={`message ${isBot ? "bot" : "user"}`}>
      <div className="message-bubble">
        {isBot
          ? <ReactMarkdown>{msg.content}</ReactMarkdown>
          : <p>{msg.content}</p>
        }
      </div>

      {isBot && (
        <div className="message-actions">
          <button className="action-btn" onClick={() => onTTS(msg.content, msg.detectedLang || "English")} title="Listen">
            🔊
          </button>

          {msg.sources?.length > 0 && (
            <button className="action-btn" onClick={() => setSourcesOpen(o => !o)}>
              📎 Sources {sourcesOpen ? "▲" : "▼"}
            </button>
          )}

          {msg.rated ? (
            <span className="feedback-recorded">
              {msg.rated === 1 ? "👍" : "👎"} Feedback recorded
            </span>
          ) : (
            <>
              <button className="action-btn" onClick={() => onFeedback(index, 1)} title="Helpful">👍</button>
              <button className="action-btn" onClick={() => onFeedback(index, -1)} title="Not helpful">👎</button>
            </>
          )}
        </div>
      )}

      {sourcesOpen && msg.sources?.length > 0 && (
        <div className="sources">
          {msg.sources.map((s, i) => (
            <div key={i} className="source-item">
              <a href={s.url} target="_blank" rel="noreferrer"><strong>{s.title}</strong></a>
              {s.published_at && <span className="source-date"> · {s.published_at}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function MessageList({ messages, loading, onFeedback, onTTS }) {
  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <Message key={i} msg={msg} index={i} onFeedback={onFeedback} onTTS={onTTS} />
      ))}
      {loading && (
        <div className="message bot">
          <div className="message-bubble typing">
            <span /><span /><span />
          </div>
        </div>
      )}
    </div>
  );
}
