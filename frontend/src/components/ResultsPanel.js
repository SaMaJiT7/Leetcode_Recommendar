import React from 'react';
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
        {result.output && (
          <div className="result-section">
            <h4>Output:</h4>
            <div className="output-box">
              <pre>{result.output || '(No output)'}</pre>
            </div>
          </div>
        )}

        {result.expected && (
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
            <p>🎉 Congratulations! Your solution is correct!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;
