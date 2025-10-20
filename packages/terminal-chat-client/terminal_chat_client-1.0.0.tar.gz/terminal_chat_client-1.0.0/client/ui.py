"""
Textual UI components for the terminal chat client
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static, Button, Label, RichLog
from textual.binding import Binding
from textual.screen import Screen
from datetime import datetime
from typing import Optional, Callable
from rich.text import Text
import hashlib


class LoginScreen(Screen):
    """Login and registration screen"""

    CSS = """
    LoginScreen {
        align: center middle;
        background: $surface;
    }

    #login-container {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }

    #login-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $accent;
        padding: 1;
    }

    .login-label {
        width: 100%;
        padding: 1 0;
    }

    .login-input {
        width: 100%;
        margin-bottom: 1;
    }

    #button-container {
        width: 100%;
        height: auto;
        layout: horizontal;
        padding: 1 0;
    }

    Button {
        width: 1fr;
        margin: 0 1;
    }

    #status-label {
        width: 100%;
        text-align: center;
        color: $warning;
        padding: 1 0;
        height: 3;
    }
    """

    def __init__(self, on_login: Callable):
        super().__init__()
        self.on_login = on_login

    def compose(self) -> ComposeResult:
        """Compose the login screen"""
        with Container(id="login-container"):
            yield Label("Terminal Chat", id="login-title")
            yield Label("Username:", classes="login-label")
            yield Input(
                placeholder="Enter username (min 3 chars)",
                id="username-input",
                classes="login-input"
            )
            yield Label("Password:", classes="login-label")
            yield Input(
                placeholder="Enter password (min 6 chars)",
                password=True,
                id="password-input",
                classes="login-input"
            )
            with Horizontal(id="button-container"):
                yield Button("Login", variant="primary", id="login-btn")
                yield Button("Register", variant="success", id="register-btn")
            yield Label("", id="status-label")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        username_input = self.query_one("#username-input", Input)
        password_input = self.query_one("#password-input", Input)
        status_label = self.query_one("#status-label", Label)

        username = username_input.value.strip()
        password = password_input.value.strip()

        # Validation
        if len(username) < 3:
            status_label.update("Username must be at least 3 characters")
            return

        if len(username) > 30:
            status_label.update("Username must be less than 30 characters")
            return

        # Check for valid characters
        if not username.replace('_', '').replace('-', '').isalnum():
            status_label.update("Username: letters, numbers, _, - only")
            return

        if len(password) < 6:
            status_label.update("Password must be at least 6 characters")
            return

        # Determine action
        if event.button.id == "login-btn":
            action = "login"
        elif event.button.id == "register-btn":
            action = "register"
        else:
            return

        status_label.update(f"{action.capitalize()}ing...")

        # Call the login callback
        self.on_login(username, password, action)

    def show_error(self, message: str):
        """Show error message"""
        status_label = self.query_one("#status-label", Label)
        status_label.update(f"Error: {message}")


class ChatScreen(Screen):
    """Main chat interface"""

    CSS = """
    ChatScreen {
        background: $surface;
    }

    #chat-header {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        padding: 1 2;
    }

    #header-content {
        layout: horizontal;
        width: 100%;
        height: 100%;
    }

    #app-title {
        width: auto;
        text-style: bold;
    }

    #online-users {
        width: auto;
        dock: right;
        text-align: right;
        margin-right: 2;
    }

    #encryption-indicator {
        width: auto;
        dock: right;
        text-align: right;
        color: $success;
        text-style: bold;
    }

    #status-bar {
        dock: top;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 2;
    }

    #message-display {
        height: 1fr;
        border: solid $primary;
        background: $surface;
        margin: 1;
        padding: 1;
    }

    #input-container {
        dock: bottom;
        height: 3;
        background: $panel;
        padding: 0 2;
    }

    Input {
        width: 100%;
    }

    .message-line {
        padding: 0 0 0 1;
    }

    .message-timestamp {
        color: $text-muted;
    }

    .message-username {
        color: $accent;
        text-style: bold;
    }

    .message-content {
        color: $text;
    }

    .system-message {
        color: $warning;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, username: str, on_send_message: Callable):
        super().__init__()
        self.username = username
        self.on_send_message = on_send_message
        self.online_users_count = 0
        # User colors for consistent color assignment
        self.user_colors = {}
        self.available_colors = [
            "cyan", "magenta", "yellow", "blue",
            "green", "bright_cyan", "bright_magenta", "bright_yellow"
        ]

    def get_user_color(self, username: str) -> str:
        """Get a consistent color for a username"""
        if username not in self.user_colors:
            # Use hash to get consistent color for username
            hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
            color_index = hash_value % len(self.available_colors)
            self.user_colors[username] = self.available_colors[color_index]
        return self.user_colors[username]

    def compose(self) -> ComposeResult:
        """Compose the chat screen"""
        # Header
        with Container(id="chat-header"):
            with Horizontal(id="header-content"):
                yield Label(f"Terminal Chat - {self.username}", id="app-title")
                yield Label("🔒 E2EE", id="encryption-indicator")
                yield Label("Online: 0", id="online-users")

        # Status bar
        yield Label("Connecting...", id="status-bar")

        # Message display area
        yield RichLog(id="message-display", highlight=True, markup=True, wrap=True)

        # Input area
        with Container(id="input-container"):
            yield Input(placeholder="Type a message and press Enter...", id="message-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission"""
        message = event.value.strip()
        if message:
            # Check for commands
            if message.startswith('/'):
                self.handle_command(message)
                event.input.value = ""
            else:
                # Send message via callback
                self.on_send_message(message)
                event.input.value = ""

    def add_message(self, username: str, content: str, timestamp: str = None, play_sound: bool = True):
        """Add a chat message to the display"""
        message_display = self.query_one("#message-display", RichLog)

        # Format timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M:%S")
            except Exception:
                time_str = timestamp[:8] if len(timestamp) >= 8 else ""
        else:
            time_str = datetime.now().strftime("%H:%M:%S")

        # Get user color
        user_color = self.get_user_color(username)

        # Use different color for own messages
        if username == self.username:
            new_message = f"[dim]{time_str}[/dim] [bold white]{username}:[/bold white] {content}"
        else:
            new_message = f"[dim]{time_str}[/dim] [bold {user_color}]{username}:[/bold {user_color}] {content}"

        # Write the message to RichLog
        message_display.write(new_message)

        # Play notification sound for messages from other users
        if play_sound and username != self.username:
            self.app.bell()

    def add_system_message(self, message: str):
        """Add a system message (user joined, left, etc.)"""
        message_display = self.query_one("#message-display", RichLog)

        time_str = datetime.now().strftime("%H:%M:%S")
        # Use Rich markup for system messages
        new_message = f"[dim]{time_str}[/dim] [italic yellow]* {message}[/italic yellow]"

        # Write the system message to RichLog
        message_display.write(new_message)

    def update_status(self, status: str):
        """Update the status bar"""
        status_bar = self.query_one("#status-bar", Label)
        status_bar.update(status)

    def update_online_users(self, count: int):
        """Update online users count"""
        self.online_users_count = count
        online_label = self.query_one("#online-users", Label)
        online_label.update(f"Online: {count}")

    def handle_command(self, command: str):
        """Handle slash commands"""
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "/help":
            self.show_help()
        elif cmd == "/quit" or cmd == "/exit":
            self.app.exit()
        elif cmd == "/clear":
            self.clear_messages()
        else:
            self.add_system_message(f"Unknown command: {cmd}. Type /help for available commands.")

    def show_help(self):
        """Show help message with available commands"""
        help_text = [
            "Available Commands:",
            "  /help       - Show this help message",
            "  /quit       - Exit the application",
            "  /clear      - Clear message history",
            "",
            "Keyboard Shortcuts:",
            "  Ctrl+C/Q    - Quit application"
        ]
        for line in help_text:
            self.add_system_message(line)

    def clear_messages(self):
        """Clear the message display"""
        message_display = self.query_one("#message-display", RichLog)
        message_display.clear()
        self.add_system_message("Message history cleared")

    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()


class ChatApp(App):
    """Main chat application"""

    def __init__(self):
        super().__init__()
        self.username: Optional[str] = None
        self.user_id: Optional[int] = None
        self.token: Optional[str] = None
        self.send_message_callback: Optional[Callable] = None
        self.login_callback: Optional[Callable] = None

    def on_mount(self) -> None:
        """Show login screen on startup"""
        self.push_screen(LoginScreen(self.handle_login))

    def handle_login(self, username: str, password: str, action: str):
        """Handle login/register action"""
        if self.login_callback:
            self.login_callback(username, password, action)

    def show_chat(self, username: str, user_id: int, token: str):
        """Switch to chat screen after successful login"""
        self.username = username
        self.user_id = user_id
        self.token = token

        # Remove login screen and show chat
        self.pop_screen()
        self.push_screen(ChatScreen(username, self.handle_send_message))

    def handle_send_message(self, message: str):
        """Handle message sending"""
        if self.send_message_callback:
            self.send_message_callback(message)

    def set_login_callback(self, callback: Callable):
        """Set callback for login/register"""
        self.login_callback = callback

    def set_send_message_callback(self, callback: Callable):
        """Set callback for sending messages"""
        self.send_message_callback = callback

    def get_chat_screen(self) -> Optional[ChatScreen]:
        """Get the chat screen if it exists"""
        for screen in self.screen_stack:
            if isinstance(screen, ChatScreen):
                return screen
        return None

    def show_login_error(self, message: str):
        """Show error on login screen"""
        for screen in self.screen_stack:
            if isinstance(screen, LoginScreen):
                screen.show_error(message)
                break
