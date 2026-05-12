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

export default function Sidebar({ open, canton, onCantonChange, onNewConversation, onClose, t }) {
  const [news, setNews] = useState([]);
  const [totalArticles, setTotalArticles] = useState(null);
  const [newsOpen, setNewsOpen] = useState(false);

  useEffect(() => {
    getNews().then(d => {
      setNews(d.news || []);
      setTotalArticles(d.total_articles ?? null);
    }).catch(() => {});
  }, []);

  if (!open) return null;

  return (
    <aside className="sidebar">
      <div className="sidebar-close-row">
        <span className="sidebar-brand">AmanCH</span>
        <button className="sidebar-close-btn" onClick={onClose} aria-label="Close sidebar">✕</button>
      </div>
      <div className="sidebar-section">
        <h3 className="sidebar-title">{t.yourCanton}</h3>
        <p className="sidebar-hint">{t.cantonHint}</p>
        <select
          className="canton-select"
          value={canton || ""}
          onChange={e => onCantonChange(e.target.value || null)}
        >
          <option value="">{t.cantonPlaceholder}</option>
          {CANTONS.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        {canton && <div className="canton-badge">{t.cantonBadge(canton)}</div>}
      </div>

      <div className="sidebar-section">
        <button className="news-toggle" onClick={() => setNewsOpen(o => !o)}>
          📰 {t.latestNews} {newsOpen ? "▲" : "▼"}
        </button>
        {totalArticles !== null && (
          <p className="news-total">{t.articlesIndexed(totalArticles)}</p>
        )}
        {newsOpen && (
          <div className="news-list">
            {news.length === 0
              ? <p className="sidebar-hint">{t.loadingNews}</p>
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
        <h3 className="sidebar-title">{t.emergencyContacts}</h3>
        <div className="emergency-box">{t.emergencyNumbers}</div>
        <ul className="emergency-links">
          <li><a href="https://www.osar.ch" target="_blank" rel="noreferrer">{t.osar}</a></li>
          <li><a href="https://www.sem.admin.ch" target="_blank" rel="noreferrer">{t.sem}</a></li>
          <li><a href="https://www.redcross.ch" target="_blank" rel="noreferrer">{t.redcross}</a></li>
          <li><a href="https://www.ch.ch/en/" target="_blank" rel="noreferrer">{t.chch}</a></li>
        </ul>
      </div>

      <div className="sidebar-section">
        <button className="new-chat-btn" onClick={onNewConversation}>
          {t.newConversation}
        </button>
        <p className="sidebar-hint">{t.storedLocally}</p>
      </div>
    </aside>
  );
}
