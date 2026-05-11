import { useState, useRef } from "react";

export default function ChatInput({ onSend, onVoice, disabled }) {
  const [text, setText]         = useState("");
  const [recording, setRecording] = useState(false);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);

  function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  async function toggleRecording() {
    if (recording) {
      mediaRef.current?.stop();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = e => chunksRef.current.push(e.data);
      recorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        onVoice(blob);
        setRecording(false);
      };
      recorder.start();
      mediaRef.current = recorder;
      setRecording(true);
    } catch {
      alert("Microphone access denied. Please allow microphone access to use voice input.");
    }
  }

  return (
    <form className="chat-input-bar" onSubmit={handleSubmit}>
      <button
        type="button"
        className={`voice-btn ${recording ? "recording" : ""}`}
        onClick={toggleRecording}
        title={recording ? "Stop recording" : "Speak your question"}
      >
        {recording ? "⏹" : "🎤"}
      </button>
      <textarea
        className="chat-textarea"
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKey}
        placeholder="Ask anything — asylum, permits, work, healthcare… (any language)"
        rows={1}
        disabled={disabled}
      />
      <button type="submit" className="send-btn" disabled={disabled || !text.trim()}>
        ↑
      </button>
    </form>
  );
}
