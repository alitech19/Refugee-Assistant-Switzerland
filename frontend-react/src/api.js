import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: BASE });

export async function newConversation() {
  const { data } = await api.post("/conversation");
  return data.conversation_id;
}

export async function sendMessage({ message, conversationId, permit, canton }) {
  const { data } = await api.post("/chat", {
    message,
    conversation_id: conversationId,
    permit: permit || null,
    canton: canton || null,
  });
  return data;
}

export async function getNews() {
  const { data } = await api.get("/news");
  return data;
}

export async function submitFeedback({ conversationId, userMessage, assistantMessage, rating }) {
  await api.post("/feedback", {
    conversation_id: conversationId,
    user_message: userMessage,
    assistant_message: assistantMessage,
    rating,
  });
}

export async function transcribeAudio(audioBlob) {
  const form = new FormData();
  form.append("file", audioBlob, "audio.wav");
  const { data } = await api.post("/transcribe", form);
  return data.text;
}

export async function textToSpeech({ text, language }) {
  const { data } = await api.post("/tts", { text, language });
  return data.audio_base64;
}
