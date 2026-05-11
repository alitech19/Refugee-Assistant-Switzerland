import { useEffect, useState } from "react";
import { getNews } from "../api";

const CANTONS = [
  "Aargau (AG)", "Appenzell Ausserrhoden (AR)", "Appenzell Innerrhoden (AI)",
  "Basel-Landschaft (BL)", "Basel-Stadt (BS)", "Bern (BE)",
  "Fribourg (FR)", "Geneva (GE)", "Glarus (GL)", "Graubünden (GR)",
  "Jura (JU)", "Lucerne (LU)", "Neuchâtel (NE)", "Nidwalden (NW)",
  "Obwalden (OW)", "Schaffhausen (SH)", "Schwyz (SZ)", "Solothurn (SO)",
  "St. Gallen (SG)", "Thurgau (TG)", "Ticino (TI)", "Uri (UR)",
  "Valais (VS)", "Vaud (VD)", "Zug (ZG)", "Zurich (ZH)",
];

export default function Sidebar({ open, canton, onCantonChange, onNewConversation }) {
  const [news, setNews] = useState([]);
  const [newsOpen, setNewsOpen] = useState(false);

  useEffect(() => {
    getNews(3).then(d => setNews(d.news || [])).catch(() => {});
  }, []);

  if (!open) return null;

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h3 className="sidebar-title">Your Canton</h3>
        <p className="sidebar-hint">Select your canton for local answers:</p>
        <select
          className="canton-select"
          value={canton || ""}
          onChange={e => onCantonChange(e.target.value || null)}
        >
          <option value="">— Select your canton —</option>
          {CANTONS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        {canton && <div className="canton-badge">📍 {canton}</div>}
      </div>

      <div className="sidebar-section">
        <button className="news-toggle" onClick={() => setNewsOpen(o => !o)}>
          📰 Latest News {newsOpen ? "▲" : "▼"}
        </button>
        {newsOpen && (
          <div className="news-list">
            {news.length === 0
              ? <p className="sidebar-hint">Loading news…</p>
              : news.map((item, i) => (
                <div key={i} className="news-item">
                  <a href={item.url} target="_blank" rel="noreferrer">
                    {item.title.length > 70 ? item.title.slice(0, 70) + "…" : item.title}
                  </a>
                  <span className="news-meta">{item.source_name} · {item.published_at}</span>
                </div>
              ))
            }
          </div>
        )}
      </div>

      <div className="sidebar-section">
        <h3 className="sidebar-title">Emergency Contacts</h3>
        <div className="emergency-box">
          🚨 Police: <strong>117</strong> · Ambulance: <strong>144</strong> · Emergency: <strong>112</strong>
        </div>
        <ul className="emergency-links">
          <li><a href="https://www.osar.ch" target="_blank" rel="noreferrer">OSAR — Free legal aid</a></li>
          <li><a href="https://www.sem.admin.ch" target="_blank" rel="noreferrer">SEM — Migration authority</a></li>
          <li><a href="https://www.redcross.ch" target="_blank" rel="noreferrer">Swiss Red Cross</a></li>
          <li><a href="https://www.ch.ch/en/" target="_blank" rel="noreferrer">ch.ch — Swiss portal</a></li>
        </ul>
      </div>

      <div className="sidebar-section">
        <button className="new-chat-btn" onClick={onNewConversation}>
          + Start new conversation
        </button>
        <p className="sidebar-hint">🔒 Conversations stored locally via Groq AI.</p>
      </div>
    </aside>
  );
}
