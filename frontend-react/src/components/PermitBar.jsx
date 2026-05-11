const PERMITS = [
  { code: "N", label: "Asylum seeker — procedure pending" },
  { code: "F", label: "Provisionally admitted" },
  { code: "B", label: "Recognised refugee" },
  { code: "C", label: "Settlement permit" },
  { code: "S", label: "Protection status (e.g. Ukraine)" },
  { code: "?", label: "I don't know my permit type" },
];

export default function PermitBar({ selected, onSelect }) {
  return (
    <div className="permit-bar">
      <span className="permit-label">My permit:</span>
      <div className="permit-pills">
        {PERMITS.map(({ code, label }) => (
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
