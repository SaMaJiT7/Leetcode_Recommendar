import React from 'react';
import Editor from '@monaco-editor/react';
import './CodeEditor.css';

const CodeEditor = ({ code, language, onCodeChange, onLanguageChange, onSubmit, submitting }) => {
  const languages = [
    { value: 'python', label: 'Python' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' }
  ];

  const handleEditorChange = (value) => {
    onCodeChange(value || '');
  };

  return (
    <div className="code-editor-container">
      <div className="editor-header">
        <div className="editor-title">
          <h3>💻 Code Editor</h3>
        </div>
        <div className="editor-controls">
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="language-selector"
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
          <button
            onClick={onSubmit}
            disabled={submitting || !code.trim()}
            className="submit-button"
          >
            {submitting ? (
              <>
                <span className="spinner-small"></span>
                Running...
              </>
            ) : (
              <>
                ▶️ Run Code
              </>
            )}
          </button>
        </div>
      </div>

      <div className="editor-wrapper">
        <Editor
          height="500px"
          language={language}
          value={code}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            formatOnPaste: true,
            formatOnType: true
          }}
        />
      </div>
    </div>
  );
};

export default CodeEditor;
