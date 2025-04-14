# Calendar-assistant
📅 Google Calendar Assistant (LangGraph + Groq)
A smart AI assistant that interacts with your Google Calendar to schedule, edit, and retrieve events using natural language. Built using LangGraph, Groq, and Google Calendar API.

🚀 Features
🧠 Powered by Groq’s blazing-fast LLaMA 3

📆 Connects to your personal Google Calendar

✍️ Natural language input like:

"Create a meeting with John at 4pm tomorrow"

🛠️ Built with:

LangGraph for flexible agent-tool flow

Groq LLMs with tool calling support

Secure Google API authentication

⚙️ Setup
1. Get yourself a Groq api key and use it in model.py and tools.py
2. feel free to reach out to me (vishweshjagadeesh@gmail.com) to get the credentials.json file from my google Console Project
Save it somewhere locally (not in the repo!)

Set the path in your .env as GOOGLE_CREDENTIALS_PATH=path/to/that/file.json

✅ Running the Bot
Once set up, run the bot with:

python ui.py
The bot will listen for input and respond using your calendar and tools.

🛡️ Security
Never commit your .env or credentials.json file to GitHub.

This repo includes .gitignore rules to keep sensitive files safe.

📂 Example .env.example

GROQ_API_KEY=your-groq-api-key
GOOGLE_CREDENTIALS_PATH=credentials.json

🧠 How it Works
Uses LangGraph to build a dynamic agent flow

Your LLM (via Groq) analyzes the user's message

If it detects a tool call, it outputs the tool name + arguments

The appropriate tool is called (create_event, get_events, etc.)

Responses are streamed back into the graph

💡 Future Ideas
✅ Add web search integration

🔁 Add Long term memory or vector retriever

📲 Turn into a fully fledged desktop or mobile app

🧑‍💻 Author
Built by Your vishwesh for learning and fun.

