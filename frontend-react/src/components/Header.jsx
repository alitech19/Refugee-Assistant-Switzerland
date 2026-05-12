import { LANGUAGES } from "../i18n";

export default function Header({ onToggleSidebar, uiLang, onChangeLang, t }) {
  return (
    <header className="header">
      <button className="sidebar-toggle" onClick={onToggleSidebar} aria-label="Toggle sidebar">
        ☰
      </button>
      <div className="header-logo">
        <div className="header-cross">
          <svg width="20" height="20" viewBox="0 0 22 22">
            <rect x="9" y="1" width="4" height="20" fill="#D52B1E"/>
            <rect x="1" y="9" width="20" height="4" fill="#D52B1E"/>
          </svg>
        </div>
        <div>
          <div className="header-name">AmanCH</div>
          <div className="header-sub">{t.subtitle}</div>
        </div>
      </div>
      <select
        className="lang-select"
        value={uiLang}
        onChange={e => onChangeLang(e.target.value)}
        aria-label="Interface language"
      >
        {LANGUAGES.map(({ code, label }) => (
          <option key={code} value={code}>{label}</option>
        ))}
      </select>
    </header>
  );
}
