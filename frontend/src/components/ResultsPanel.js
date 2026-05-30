import './ResultsPanel.css';

const ResultsPanel = ({ result }) => {
  if (!result) return null;

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'Accepted':
        return '#4caf50';
      case 'Wrong Answer':
        return '#ff9800';
      case 'Runtime Error':
        return '#f44336';
      case 'System Error':
        return '#9e9e9e';
      default:
        return '#666';
    }
  };

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'Accepted':
        return '✅';
      case 'Wrong Answer':
        return '❌';
      case 'Runtime Error':
        return '⚠️';
      case 'System Error':
        return '🔧';
      default:
        return '📋';
    }
  };

  const verdictColor = getVerdictColor(result.verdict);
  const verdictIcon = getVerdictIcon(result.verdict);

  return (
    <div className="results-panel">
      <div className="results-header">
        <h3>📊 Results</h3>
        <div 
          className="verdict-badge"
          style={{ backgroundColor: verdictColor }}
        >
          {verdictIcon} {result.verdict}
        </div>
      </div>

      <div className="results-content">
        {/* Show test case progress */}
        {result.total_cases && (
          <div className="test-progress">
            <div className="progress-header">
              <span className="progress-text">
                {result.passed_cases || 0} / {result.total_cases} Test Cases Passed
              </span>
              <span className="progress-percentage">
                {Math.round(((result.passed_cases || 0) / result.total_cases) * 100)}%
              </span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ 
                  width: `${((result.passed_cases || 0) / result.total_cases) * 100}%`,
                  backgroundColor: result.verdict === 'Accepted' ? '#4caf50' : '#ff9800'
                }}
              ></div>
            </div>
          </div>
        )}

        {/* Show failed test case details */}
        {result.failed_on_case && (
          <div className="result-section failed-case">
            <h4>❌ Failed on Test Case {result.failed_on_case}</h4>
            <div className="test-case-details">
              <div className="detail-row">
                <span className="detail-label">Input:</span>
                <pre className="detail-value">{result.input || '(empty)'}</pre>
              </div>
              <div className="detail-row">
                <span className="detail-label">Expected Output:</span>
                <pre className="detail-value expected-output">{result.expected || '(empty)'}</pre>
              </div>
              <div className="detail-row">
                <span className="detail-label">Your Output:</span>
                <pre className="detail-value your-output">{result.your_output || '(empty)'}</pre>
              </div>
            </div>
          </div>
        )}

        {/* Show output for simple runs (no test cases) */}
        {!result.failed_on_case && result.output && (
          <div className="result-section">
            <h4>Output:</h4>
            <div className="output-box">
              <pre>{result.output || '(No output)'}</pre>
            </div>
          </div>
        )}

        {!result.failed_on_case && result.expected && (
          <div className="result-section">
            <h4>Expected:</h4>
            <div className="output-box expected">
              <pre>{result.expected}</pre>
            </div>
          </div>
        )}

        {result.ai_hint && (
          <div className="result-section ai-hint-section">
            <h4>🤖 AI Mentor Hint:</h4>
            <div className="hint-box">
              <p>{result.ai_hint}</p>
            </div>
          </div>
        )}

        {result.verdict === 'Accepted' && (
          <div className="success-message">
            <p>🎉 Congratulations! Your solution passed all test cases!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;
