# Zoho Project Assistant — AI Chatbot

An AI-powered chatbot that connects to Zoho Projects via REST API. Built with FastAPI, LangGraph-style multi-agent routing, and a Next.js chat UI.

## Architecture

- **Backend:** FastAPI (Python) with async/await
- **Agents:** Query Agent (read) + Action Agent (write) with a router
- **Memory:** SQLite — short-term (session) + long-term (across sessions)
- **Auth:** Zoho OAuth 2.0 Authorization Code Grant
- **Frontend:** Next.js + Tailwind CSS

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/zoho-chatbot
cd zoho-chatbot
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

### 4. Zoho OAuth Configuration
- Go to https://api-console.zoho.com/
- Create a Server-based Application
- Set redirect URI to `http://localhost:8000/auth/callback`
- Copy Client ID and Client Secret to `.env`

### 5. Run backend
```bash
cd backend
python -m uvicorn main:app --reload
```

### 6. Run frontend
```bash
cd frontend
npm install
npm run dev
```

### 7. Login
- Go to `http://localhost:3000`
- Click "Login with Zoho"
- Start chatting!

## Sample Conversations

| You say | Bot does |
|---|---|
| "What projects do I have?" | Lists your Zoho projects |
| "Show tasks for the first one" | Lists tasks using memory |
| "Create a task called API Integration" | Asks confirmation, then creates |
| "Delete task called API Integration" | Asks confirmation, then deletes |
| "Who has the most tasks?" | Returns workload summary |

## Known Limitations
- Single user session (default_user)
- Task matching by name may fail on partial matches
- Token auto-refresh not fully implemented

## Environment Variables
See `.env.example` for all required variables.