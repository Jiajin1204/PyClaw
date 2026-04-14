# cli.py
import os
import sys
import shlex
from typing import Optional

from agent import Agent
from session import Session, Message
from datetime import datetime


class CLI:
    """Command Line Interface for PyClaw."""

    COMMANDS = ["/help", "/new", "/switch", "/sessions", "/delete", "/memory", "/clear", "/exit"]

    def __init__(self, config_path: str = "config.json"):
        self.agent = Agent(config_path)
        self.current_session: Optional[Session] = None
        self.running = True

        self.agent.set_console_callback(self._print_tool)

        self._init_session()

    def _init_session(self) -> None:
        sessions = self.agent.session_manager.list_sessions()
        if sessions:
            self.current_session = self.agent.session_manager.load_session(sessions[0]["session_id"])
            if self.current_session:
                return

        self.current_session = self.agent.session_manager.create_session()

    def _print_tool(self, message: str) -> None:
        print(message)

    def _print_banner(self) -> None:
        print("╔═══════════════════════════════════════════╗")
        print("║           PyClaw AI Agent                  ║")
        print("║═══════════════════════════════════════════║")
        print(f"Session: {self.current_session.session_id if self.current_session else 'None':8} | Model: {self.agent.model.get_name()}")
        print("───────────────────────────────────────────")

    def _print_help(self) -> None:
        print("""
PyClaw Commands:
  /new                    - Start a new session
  /switch <session_id>    - Switch to another session
  /sessions               - List all sessions
  /delete <session_id>    - Delete a session
  /memory                 - View/edit memory
  /clear                  - Clear screen
  /exit                   - Exit PyClaw
  /help                   - Show this help

Core Tools:
  read    - Read file contents
  write   - Write content to file
  exec    - Execute Python code or shell commands

Simply type your message to chat with the agent.
""")

    def _cmd_new(self) -> None:
        self.current_session = self.agent.session_manager.create_session()
        print(f"Started new session: {self.current_session.session_id}")

    def _cmd_switch(self, session_id: str) -> None:
        session = self.agent.session_manager.load_session(session_id)
        if session:
            self.current_session = session
            print(f"Switched to session: {session_id}")
        else:
            print(f"Session not found: {session_id}")

    def _cmd_sessions(self) -> None:
        sessions = self.agent.session_manager.list_sessions()
        if not sessions:
            print("No sessions found.")
            return
        print(f"{'Session ID':<12} {'Updated':<26} {'Messages':<10} {'Size':<10}")
        print("-" * 60)
        for s in sessions:
            current_marker = " *" if s["session_id"] == self.current_session.session_id else ""
            print(f"{s['session_id']:<12} {s['updated_at']:<26} {s['message_count']:<10} {s['size_bytes']:<10}{current_marker}")

    def _cmd_delete(self, session_id: str) -> None:
        if session_id == self.current_session.session_id:
            print("Cannot delete current session. Switch to another first.")
            return
        if self.agent.session_manager.delete_session(session_id):
            print(f"Deleted session: {session_id}")
        else:
            print(f"Session not found: {session_id}")

    def _cmd_memory(self, args: str = None) -> None:
        if not args:
            print("Current memory:")
            print(self.agent.memory if self.agent.memory else "(empty)")
            print("\nUsage: /memory <text> - to append to memory")
            return

        if self.agent.memory:
            self.agent.memory += "\n" + args
        else:
            self.agent.memory = args
        self.agent.save_memory()
        print("Memory updated.")

    def _cmd_clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        self._print_banner()

    def _handle_command(self, line: str) -> bool:
        parts = shlex.split(line)
        if not parts:
            return True

        cmd = parts[0]
        args = " ".join(parts[1:]) if len(parts) > 1 else ""

        if cmd == "/help":
            self._print_help()
        elif cmd == "/new":
            self._cmd_new()
        elif cmd == "/switch":
            if args:
                self._cmd_switch(args)
            else:
                print("Usage: /switch <session_id>")
        elif cmd == "/sessions":
            self._cmd_sessions()
        elif cmd == "/delete":
            if args:
                self._cmd_delete(args)
            else:
                print("Usage: /delete <session_id>")
        elif cmd == "/memory":
            self._cmd_memory(args)
        elif cmd == "/clear":
            self._cmd_clear()
        elif cmd == "/exit":
            self.running = False
            print("Goodbye!")
        else:
            return False
        return True

    def run(self) -> None:
        self._print_banner()
        print("Type /help for commands or just start chatting.\n")

        while self.running:
            try:
                user_input = input("> ").strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    if self._handle_command(user_input):
                        continue

                if not self.current_session:
                    self.current_session = self.agent.session_manager.create_session()

                user_message = Message(
                    role="user",
                    content=user_input,
                    timestamp=datetime.now().isoformat()
                )
                self.current_session.add_message(user_message)
                self.agent.session_manager.add_message_to_session(
                    self.current_session.session_id, user_message
                )

                response = self.agent.think(self.current_session, user_input)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\nUse /exit to quit.")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    config_path = "config.json"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    cli = CLI(config_path)
    cli.run()


if __name__ == "__main__":
    main()
