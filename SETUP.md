# Setup Guide - CodeChallenge Daily

This guide will help you set up and run both the backend and frontend of the CodeChallenge Daily application.

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- FastAPI backend dependencies
- React frontend dependencies

## Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the root directory with:
```
index_name=your_pinecone_index_name
# Add other required environment variables for Pinecone, Groq, etc.
```

3. **Start the FastAPI backend:**
```bash
cd app
uvicorn backend:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`

## Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure API URL (optional):**
Create a `.env` file in the `frontend` directory:
```
REACT_APP_API_URL=http://localhost:8000
```

4. **Start the React development server:**
```bash
npm start
```

The frontend will open at `http://localhost:3000`

## Features

- ✅ Daily personalized coding challenges based on user preferences
- ✅ Monaco code editor with syntax highlighting
- ✅ Support for Python, Java, and C++
- ✅ Code execution via Piston API
- ✅ AI-powered hints and feedback
- ✅ Real-time results display

## Notes

### Test Cases
Currently, test cases need to be extracted from the problem content or provided separately. The backend endpoint `/daily-challenge` returns problem content, but test cases should be parsed from the content or added to the challenge object.

To add test case extraction:
1. Parse test cases from the problem content in the backend
2. Include test cases in the challenge response
3. The frontend will automatically use them for submissions

### API Endpoints

- `GET /test` - Health check endpoint
- `POST /daily-challenge` - Get daily challenge problem
  - Body: `{ "user_weakness": "string", "current_level": "string" }`
- `POST /submit` - Submit code for evaluation
  - Body: `{ "language": "string", "code": "string", "input_data": "string", "expected_output": "string" }`

## Troubleshooting

- **CORS errors**: Make sure the backend CORS middleware is configured correctly
- **API connection issues**: Verify the `REACT_APP_API_URL` matches your backend URL
- **Piston API errors**: Check your internet connection and Piston API availability
