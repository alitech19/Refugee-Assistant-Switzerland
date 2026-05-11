import { useState, useEffect, useRef } from "react";
import { newConversation, sendMessage, submitFeedback, transcribeAudio, textToSpeech } from "./api";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import PermitBar from "./components/PermitBar";
import MessageList from "./components/MessageList";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatInput from "./components/ChatInput";
import "./App.css";

const QUICK_TOPICS = [
  { emoji: "🔖", label: "Permits",     question: "What types of permits exist in Switzerland and what does each one allow?" },
  { emoji: "📋", label: "Asylum",      question: "What are the steps of the Swiss asylum procedure?" },
  { emoji: "💼", label: "Work",        question: "Can I work in Switzerland and what do I need to do?" },
  { emoji: "🏥", label: "Healthcare",  question: "How do I access healthcare and get health insurance in Switzerland?" },
  { emoji: "🎓", label: "Integration", question: "What language courses and integration programs are available for refugees?" },
  { emoji: "👨‍👩‍👧", label: "Family",    question: "How can I bring my family to Switzerland?" },
  { emoji: "⚖️", label: "Appeals",     question: "How do I appeal a rejected asylum decision?" },
  { emoji: "🏠", label: "Housing",     question: "What housing do asylum seekers receive in Switzerland?" },
];

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages]             = useState([]);
  const [permit, setPermit]                 = useState(null);
  const [canton, setCanton]                 = useState(null);
  const [loading, setLoading]               = useState(false);
  const [sidebarOpen, setSidebarOpen]       = useState(window.innerWidth > 768);
  const bottomRef = useRef(null);

  useEffect(() => {
    newConversation().then(setConversationId);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text) {
    if (!text.trim() || !conversationId || loading) return;
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
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        canton={canton}
        onCantonChange={setCanton}
        onNewConversation={handleNewConversation}
      />
      <div className={`main-area ${sidebarOpen ? "sidebar-open" : ""}`}>
        <Header onToggleSidebar={() => setSidebarOpen(o => !o)} />
        <div className="content">
          <PermitBar selected={permit} onSelect={setPermit} />
          <div className="chat-area">
            {messages.length === 0
              ? <WelcomeScreen topics={QUICK_TOPICS} onSelect={handleSend} />
              : <MessageList messages={messages} loading={loading} onFeedback={handleFeedback} onTTS={handleTTS} />
            }
            <div ref={bottomRef} />
          </div>
          <ChatInput onSend={handleSend} onVoice={handleVoice} disabled={loading || !conversationId} />
        </div>
      </div>
    </div>
  );
}
