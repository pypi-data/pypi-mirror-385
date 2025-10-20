# Terminal Chat

A modern terminal-based chat application built with Python, featuring real-time messaging, end-to-end encryption, and a beautiful terminal UI.

## Features

- **Real-time Messaging**: WebSocket-based communication for instant message delivery
- **End-to-End Encryption**: Messages are encrypted using Fernet symmetric encryption
- **Terminal UI**: Beautiful, responsive interface built with Textual
- **Message History**: Persistent storage of encrypted messages with SQLite/PostgreSQL
- **User Authentication**: Secure JWT-based authentication
- **Auto-Reconnection**: Smart reconnection with exponential backoff
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Technology Stack

- **Backend**: FastAPI + uvicorn (async WebSocket support)
- **Client UI**: Textual (modern terminal UI framework)
- **Database**: SQLite (development) → PostgreSQL (production)
- **Encryption**: Fernet symmetric encryption
- **Authentication**: JWT tokens with bcrypt password hashing
- **Protocol**: WebSockets for real-time bidirectional communication

## Project Structure

```
terminal-chat/
├── server/                 # FastAPI WebSocket server
│   ├── __init__.py
│   ├── main.py            # Server entry point
│   ├── connection_manager.py
│   ├── database.py
│   └── models.py
├── client/                # Terminal UI client
│   ├── __init__.py
│   ├── main.py           # Client entry point
│   ├── ui.py             # Textual UI components
│   └── connection.py     # WebSocket client
├── shared/               # Shared utilities
│   ├── __init__.py
│   └── crypto.py         # Encryption utilities
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd terminal-chat
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv

   # On Linux/macOS
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and update configuration as needed
   ```

## Usage

### Running the Server

**Development mode:**
```bash
# From project root
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start on `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

### Running the Client

**Basic usage:**
```bash
# From project root
python -m client.main
```

**With custom server:**
```bash
python -m client.main --server http://your-server.com:8000
```

**View configuration:**
```bash
python -m client.main --config
```

**Client Slash Commands:**
- `/help` - Show available commands
- `/quit` or `/exit` - Exit the application
- `/clear` - Clear message history

### Client Configuration

Client settings are stored in `~/.terminal-chat/config.json`:
- `server_url`: Server address (default: http://127.0.0.1:8000)
- `auto_reconnect`: Enable/disable auto-reconnection (default: true)
- `notification_sound`: Enable/disable sound notifications (default: true)
- `message_history_limit`: Number of messages to load on startup (default: 50)

You can also use the `CHAT_SERVER_URL` environment variable to override the server URL.

## API Endpoints

### REST API
- `GET /` - Health check (returns server status)
- `GET /api/health` - API health check for monitoring
- `POST /api/register` - Create a new user account
  - Body: `{"username": "string", "password": "string"}`
  - Returns: JWT token and user info
- `POST /api/login` - Authenticate and receive JWT token
  - Body: `{"username": "string", "password": "string"}`
  - Returns: JWT token and user info
- `GET /api/history?limit=100` - Retrieve message history
  - Query params: `limit` (default: 100), `room_id` (default: "general")
  - Returns: Array of encrypted messages

### WebSocket
- `WS /ws/{user_id}` - WebSocket connection for real-time chat
  - Requires valid JWT token
  - Message types:
    - `message`: Chat message
    - `user_joined`: User joined notification
    - `user_left`: User left notification
    - `active_users`: Active users count update
    - `ping`/`pong`: Heartbeat messages
    - `error`: Error message from server

Visit `http://localhost:8000/docs` for interactive API documentation.

## Development

### Database Initialization

The database will be automatically initialized on first run. To manually initialize:

```python
from server.database import init_db
init_db()
```

### Running Tests

```bash
pytest
pytest -v  # Verbose output
```

## Security Features

1. **Authentication**: JWT tokens with configurable expiration
2. **Password Security**: Bcrypt hashing for all passwords
3. **End-to-End Encryption**: Messages encrypted before transmission
4. **Input Validation**: All user inputs are validated and sanitized
5. **Rate Limiting**: Protection against spam and DoS attacks (to be implemented)

## Deployment

### Docker Deployment

**Using Docker:**
```bash
# Build the Docker image
docker build -t terminal-chat-server:latest .

# Run with SQLite (development)
docker run -d \
  --name terminal-chat \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e JWT_SECRET_KEY=your-secret-key \
  terminal-chat-server:latest
```

**Using Docker Compose (recommended):**

For development (SQLite):
```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

For production (PostgreSQL):
```bash
# Start with PostgreSQL
docker-compose --profile production up -d

# This will start both the server and PostgreSQL database
```

**Environment Variables:**
Create a `.env` file or set the following:
- `DATABASE_URL` - Database connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing (change in production!)
- `JWT_ALGORITHM` - Algorithm for JWT (default: HS256)
- `JWT_EXPIRATION_HOURS` - Token expiration time (default: 24)
- `ENVIRONMENT` - Environment (development/production)

### Cloud Platforms

#### Railway
1. Push your code to GitHub
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add PostgreSQL database from Railway marketplace
5. Set environment variables
6. Deploy!

#### Render
1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database
6. Configure environment variables
7. Deploy!

#### DigitalOcean App Platform
1. Create a new App
2. Connect your repository
3. Select Python as runtime
4. Add PostgreSQL database
5. Configure environment variables
6. Deploy!

**Important for Production:**
- Use PostgreSQL instead of SQLite
- Set a strong `JWT_SECRET_KEY`
- Enable HTTPS/WSS (SSL/TLS)
- Set up proper CORS configuration
- Consider adding rate limiting
- Use environment variables for all secrets

## Roadmap

- [x] Phase 1: Project foundation and structure
- [x] Phase 2: Server core with authentication and WebSockets
- [x] Phase 3: Client foundation with real-time chat UI
- [x] Phase 4: Message persistence with SQLite/PostgreSQL support
- [x] Phase 5: End-to-end encryption with Fernet
- [x] Phase 6: Polish & UX improvements (slash commands, colors, notifications)
- [x] Phase 7: Cloud deployment (Docker, documentation)

## Future Enhancements

- [ ] Multiple chat rooms/channels
- [ ] Private direct messages
- [ ] File sharing capabilities
- [ ] Message editing and deletion
- [ ] User profiles and avatars
- [ ] Message search functionality
- [ ] Rich text formatting (Markdown)
- [ ] Rate limiting and spam protection
- [ ] Read receipts
- [ ] Typing indicators

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details
