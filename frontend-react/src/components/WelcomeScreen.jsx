export default function WelcomeScreen({ topics, commonQ, onSelect, t }) {
  return (
    <div className="welcome">
      <div className="welcome-info">
        <p><strong>{t.welcomeInfo1.split(':')[0]}:</strong>{t.welcomeInfo1.split(':').slice(1).join(':')}</p>
        <p><strong>{t.welcomeInfo2.split(':')[0]}:</strong>{t.welcomeInfo2.split(':').slice(1).join(':')}</p>
        <p>
          <strong>{t.welcomeInfo3label}</strong>{t.welcomeInfo3}{" "}
          <a href="https://www.osar.ch" target="_blank" rel="noreferrer">{t.welcomeInfo3osar}</a>{" "}
          {t.welcomeInfo3mid}{" "}
          <a href="https://www.sem.admin.ch" target="_blank" rel="noreferrer">{t.welcomeInfo3sem}</a>{" "}
          {t.welcomeInfo3end}
        </p>
      </div>

      <h3 className="welcome-heading">{t.welcomeHeading}</h3>
      <p className="welcome-hint">{t.welcomeHint}</p>

      <div className="topic-grid">
        {topics.map(({ emoji, label, question }) => (
          <button key={label} className="topic-btn" onClick={() => onSelect(question)}>
            <span className="topic-emoji">{emoji}</span>
            <span>{label}</span>
          </button>
        ))}
      </div>

      <h4 className="welcome-heading" style={{ marginTop: "1.5rem" }}>{t.commonHeading}</h4>
      <div className="common-grid">
        {commonQ.map((q, i) => (
          <button key={i} className="common-btn" onClick={() => onSelect(q)}>
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
