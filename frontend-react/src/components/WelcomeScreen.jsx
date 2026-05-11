const COMMON_Q = [
  "What do I do when I first arrive in Switzerland as a refugee?",
  "What is Permit F and can I work with it?",
  "How do I appeal a rejected asylum decision?",
  "How can I bring my family to Switzerland?",
  "What is Permit S for Ukrainians?",
  "What are the latest asylum updates in Switzerland?",
];

export default function WelcomeScreen({ topics, onSelect }) {
  return (
    <div className="welcome">
      <div className="welcome-info">
        <p><strong>What I can help with:</strong> Swiss asylum procedure · Permits (N, F, B, C, S) · Work rights · Language courses · Healthcare · Family reunification · Appeals · Housing</p>
        <p><strong>Languages:</strong> I reply in your language — Arabic, Tigrinya, Somali, Dari, Ukrainian, Turkish, German, French, Italian, English, and more.</p>
        <p><strong>Important:</strong> I give guidance only — not legal advice. For appeals or urgent matters, contact <a href="https://www.osar.ch" target="_blank" rel="noreferrer">OSAR</a> (free legal aid) or <a href="https://www.sem.admin.ch" target="_blank" rel="noreferrer">SEM</a> directly.</p>
      </div>

      <h3 className="welcome-heading">What would you like to know today?</h3>
      <p className="welcome-hint">Tap a topic or type your question below — I answer in your language.</p>

      <div className="topic-grid">
        {topics.map(({ emoji, label, question }) => (
          <button key={label} className="topic-btn" onClick={() => onSelect(question)}>
            <span className="topic-emoji">{emoji}</span>
            <span>{label}</span>
          </button>
        ))}
      </div>

      <h4 className="welcome-heading" style={{ marginTop: "1.5rem" }}>Common questions:</h4>
      <div className="common-grid">
        {COMMON_Q.map((q, i) => (
          <button key={i} className="common-btn" onClick={() => onSelect(q)}>
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
