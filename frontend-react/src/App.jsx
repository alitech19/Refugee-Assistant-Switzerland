import { useState, useEffect, useRef } from "react";
import { newConversation, sendMessage, submitFeedback, transcribeAudio, textToSpeech } from "./api";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import PermitBar from "./components/PermitBar";
import MessageList from "./components/MessageList";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatInput from "./components/ChatInput";
import translations from "./i18n";
import "./App.css";

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages]             = useState([]);
  const [permit, setPermit]                 = useState(null);
  const [canton, setCanton]                 = useState(null);
  const [loading, setLoading]               = useState(false);
  const [sidebarOpen, setSidebarOpen]       = useState(window.innerWidth > 768);
  const [uiLang, setUiLang]                 = useState("en");
  const t = translations[uiLang];
  const bottomRef = useRef(null);

  useEffect(() => {
    newConversation().then(setConversationId);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function closeSidebarOnMobile() {
    if (window.innerWidth <= 768) setSidebarOpen(false);
  }

  async function handleSend(text) {
    if (!text.trim() || !conversationId || loading) return;
    closeSidebarOnMobile();
    setMessages(prev => [...prev, { role: "user", content: text, sources: [] }]);
    setLoading(true);
    try {
      const data = await sendMessage({ message: text, conversationId, permit, canton });
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.reply,
        sources: data.sources || [],
        detectedLang: data.detected_language,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "⚠️ Could not reach the server. Make sure the API is running on port 8000.",
        sources: [],
      }]);
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(msgIndex, rating) {
    const assistantMsg = messages[msgIndex];
    const userMsg = [...messages].slice(0, msgIndex).reverse().find(m => m.role === "user");
    if (!userMsg) return;
    await submitFeedback({ conversationId, userMessage: userMsg.content, assistantMessage: assistantMsg.content, rating });
    setMessages(prev => prev.map((m, i) => i === msgIndex ? { ...m, rated: rating } : m));
  }

  async function handleVoice(audioBlob) {
    try {
      const text = await transcribeAudio(audioBlob);
      if (text) handleSend(text);
    } catch { console.error("Transcription failed"); }
  }

  async function handleTTS(text, language) {
    try {
      const b64 = await textToSpeech({ text, language });
      new Audio(`data:audio/mp3;base64,${b64}`).play();
    } catch { console.error("TTS failed"); }
  }

  function handleNewConversation() {
    newConversation().then(id => {
      setConversationId(id);
      setMessages([]);
      setPermit(null);
    });
  }

  return (
    <div className="app-shell" dir={uiLang === "ar" ? "rtl" : "ltr"}>
      {sidebarOpen && (
        <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />
      )}
      <Sidebar
        open={sidebarOpen}
        canton={canton}
        onCantonChange={setCanton}
        onNewConversation={handleNewConversation}
        onClose={() => setSidebarOpen(false)}
        t={t}
      />
      <div className={`main-area ${sidebarOpen ? "sidebar-open" : ""}`}>
        <Header
          onToggleSidebar={() => setSidebarOpen(o => !o)}
          uiLang={uiLang}
          onChangeLang={setUiLang}
          t={t}
        />
        <div className="content">
          <PermitBar selected={permit} onSelect={setPermit} t={t} />
          <div className="chat-area">
            {messages.length === 0
              ? <WelcomeScreen topics={t.topics} commonQ={t.commonQ} onSelect={handleSend} t={t} />
              : <MessageList messages={messages} loading={loading} onFeedback={handleFeedback} onTTS={handleTTS} t={t} />
            }
            <div ref={bottomRef} />
          </div>
          <ChatInput onSend={handleSend} onVoice={handleVoice} disabled={loading || !conversationId} t={t} />
        </div>
      </div>
    </div>
  );
}
