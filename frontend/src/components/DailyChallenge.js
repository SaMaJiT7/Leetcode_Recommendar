import './DailyChallenge.css';

const DailyChallenge = ({ challenge }) => {
  if (!challenge) {
    return (
      <div className="daily-challenge">
        <div className="challenge-placeholder">
          <p>No challenge available</p>
        </div>
      </div>
    );
  }

  const difficultyColors = {
    'Easy': '#4caf50',
    'Medium': '#ff9800',
    'Hard': '#f44336',
    'Beginner': '#4caf50',
    'Intermediate': '#ff9800',
    'Advanced': '#f44336'
  };

  const difficultyColor = difficultyColors[challenge.difficulty] || '#666';

  return (
    <div className="daily-challenge">
      <div className="challenge-header">
        <div className="challenge-title-section">
          <h2>{challenge.title}</h2>
          <span 
            className="difficulty-badge"
            style={{ backgroundColor: difficultyColor }}
          >
            {challenge.difficulty}
          </span>
        </div>
        <div className="challenge-meta">
          <span className="challenge-date">📅 {challenge.date}</span>
          <span className="challenge-topic">🏷️ {challenge.topic}</span>
        </div>
      </div>

      <div className="challenge-content">
        <div className="challenge-description">
          {challenge.content ? (
            <div className="content-text">
              {challenge.content.split('\n').map((line, idx) => (
                <p key={idx}>{line}</p>
              ))}
            </div>
          ) : (
            <p>Problem description will be displayed here.</p>
          )}
        </div>

        {challenge.url && challenge.url !== '#' && (
          <div className="challenge-link">
            <a 
              href={challenge.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="external-link"
            >
              🔗 View on LeetCode
            </a>
          </div>
        )}
      </div>

      {challenge.test_cases && challenge.test_cases.length > 0 && (
        <div className="test-cases-section">
          <h3>📝 Test Cases ({challenge.test_cases.length})</h3>
          <div className="test-cases-list">
            {challenge.test_cases.map((testCase, idx) => (
              <div key={idx} className="test-case-item">
                <div className="test-case-header">
                  <span className="test-case-number">Case {idx + 1}</span>
                </div>
                <div className="test-case-content">
                  <div className="test-case-field">
                    <span className="field-label">Input:</span>
                    <pre className="field-value">{testCase.input || '(empty)'}</pre>
                  </div>
                  <div className="test-case-field">
                    <span className="field-label">Expected:</span>
                    <pre className="field-value">{testCase.expected || '(empty)'}</pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="challenge-footer">
        <div className="challenge-stats">
          <div className="stat-item">
            <span className="stat-label">Topic:</span>
            <span className="stat-value">{challenge.topic}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Level:</span>
            <span className="stat-value">{challenge.difficulty}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailyChallenge;
