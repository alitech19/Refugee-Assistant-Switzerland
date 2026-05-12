export default function PermitBar({ selected, onSelect, t }) {
  return (
    <div className="permit-bar">
      <span className="permit-label">{t.myPermit}</span>
      <div className="permit-pills">
        {t.permits.map(({ code, label }) => (
          <button
            key={code}
            title={label}
            className={`permit-pill ${selected === code ? "active" : ""}`}
            onClick={() => onSelect(selected === code ? null : code)}
          >
            {code}
          </button>
        ))}
      </div>
    </div>
  );
}
