import axios from 'axios';
import { useEffect, useState } from 'react';
import './App.css';
import CodeEditor from './components/CodeEditor';
import DailyChallenge from './components/DailyChallenge';
import ResultsPanel from './components/ResultsPanel';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [userWeakness, setUserWeakness] = useState('General');
  const [userLevel, setUserLevel] = useState('Intermediate');

  useEffect(() => {
    fetchDailyChallenge();
  }, []);

  const fetchDailyChallenge = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/daily-challenge`, {
        user_weakness: userWeakness,
        current_level: userLevel
      });
      setChallenge(response.data);
      // Use starter_code from MongoDB if available, otherwise use default
      const starterCode = response.data.starter_code?.[language] || getDefaultCode(language);
      setCode(starterCode);
    } catch (error) {
      console.error('Error fetching daily challenge:', error);
      alert('Failed to load daily challenge. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getDefaultCode = (lang) => {
    const templates = {
      python: `def solution():
    # Your code here
    pass

# Test your solution
if __name__ == "__main__":
    result = solution()
    print(result)`,
      java: `public class Solution {
    public static void main(String[] args) {
        // Your code here
    }
}`,
      cpp: `#include <iostream>
using namespace std;

int main() {
    // Your code here
    return 0;
}`
    };
    return templates[lang] || templates.python;
  };

  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    // Use starter_code from challenge if available
    const starterCode = challenge?.starter_code?.[newLanguage] || getDefaultCode(newLanguage);
    setCode(starterCode);
  };

  const handleSubmit = async () => {
    if (!challenge || !code.trim()) {
      alert('Please write some code before submitting.');
      return;
    }

    setSubmitting(true);
    setResult(null);

    try {
      // Pass all test cases or just input/expected if no test cases
      const testCasesToSend = challenge.test_cases && challenge.test_cases.length > 0 
        ? challenge.test_cases 
        : null;

console.log('Challenge:', challenge);
console.log('Test cases to send:', testCasesToSend);
  
const response = await axios.post(`${API_BASE_URL}/submit`, {
  task_id: challenge.task_id,  // Add task_id for MongoDB lookup
  language: language,
  code: code,
  input_data: challenge.test_cases?.[0]?.input || "",
  expected_output: challenge.test_cases?.[0]?.expected || "",
  test_cases: testCasesToSend
});

      setResult(response.data);
    } catch (error) {
      console.error('Error submitting code:', error);
      setResult({
        verdict: 'System Error',
        output: '',
        ai_hint: error.response?.data?.detail || 'Failed to submit code. Please try again.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading your daily challenge...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>💻 CodeChallenge Daily</h1>
        <p>Your personalized coding challenge awaits</p>
      </header>

      <div className="app-container">
        <div className="settings-panel">
          <div className="setting-group">
            <label>Focus Area:</label>
            <select 
              value={userWeakness} 
              onChange={(e) => setUserWeakness(e.target.value)}
            >
              <option value="General">General</option>
              <option value="Arrays">Arrays</option>
              <option value="Strings">Strings</option>
              <option value="Dynamic Programming">Dynamic Programming</option>
              <option value="Sliding Window">Sliding Window</option>
              <option value="Two Pointers">Two Pointers</option>
              <option value="Binary Search">Binary Search</option>
              <option value="Trees">Trees</option>
              <option value="Graphs">Graphs</option>
            </select>
          </div>
          <div className="setting-group">
            <label>Level:</label>
            <select 
              value={userLevel} 
              onChange={(e) => setUserLevel(e.target.value)}
            >
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
          </div>
          <button onClick={fetchDailyChallenge} className="refresh-btn">
            🔄 New Challenge
          </button>
        </div>

        <div className="main-content">
          <div className="left-panel">
            <DailyChallenge challenge={challenge} />
          </div>

          <div className="right-panel">
            <CodeEditor
              code={code}
              language={language}
              onCodeChange={setCode}
              onLanguageChange={handleLanguageChange}
              onSubmit={handleSubmit}
              submitting={submitting}
              testCaseCount={challenge?.test_cases?.length || 0}
            />

            {result && (
              <ResultsPanel result={result} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
