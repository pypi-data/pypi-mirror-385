from importlib.metadata import version, PackageNotFoundError
from rich.console import Console
from rich.prompt import Prompt

import asyncio
import typer
import uuid
import sys

from configen import system, api, property, runner

app = typer.Typer(invoke_without_command=True)
console = Console()

try:
    __version__ = version("configen-cli")
except PackageNotFoundError:
    __version__ = "unknown"


def server_error(http_code, http_response):
    if http_code != 200:
        console.print(f"❌ [bold red]Server error:[/bold red] [italic]{http_response}[/italic]")
        return True
    return False


async def run_repl():
    while True:
        if not system.has_internet():
            console.print("❌ [bold red]No internet connection![/bold red] [dim]🔌 Please check your network and try again.[/dim]")
            return None

        valid, error = property.validate_config()
        if valid:
            break

        console.print("🛠️ [bold green]Setting .env properties...[/bold green]")
        property.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        property.CONFIGEN_API_URL = "https://api.configen.com"
        property.HOST_ID = str(uuid.uuid4())

        max_attempts = 3
        while max_attempts > 0:
            property.CONFIGEN_API_KEY = Prompt.ask(
                "[bold yellow]Enter your Configen API Key, you can get it from https://configen.com/account[/bold yellow]"
            ).strip()
            if property.CONFIGEN_API_KEY:
                http_code, http_response = await api.validate_api_key(property.CONFIGEN_API_KEY)
                if server_error(http_code, http_response):
                    console.print("[bold red]Configen API Key is invalid![/bold red]")
                else:
                    break
            else:
                console.print("[bold red]Configen API Key is empty![/bold red]")
            max_attempts -= 1
            if max_attempts == 0:
                console.print(f"[bold red]Failed to set up Configen API Key after 3 attempts![/bold red]")
                return None

        with property.ENV_FILE.open("w") as f:
            f.write(f"CONFIGEN_API_KEY={property.CONFIGEN_API_KEY}\n")
            f.write(f"CONFIGEN_API_URL={property.CONFIGEN_API_URL}\n")
            f.write(f"HOST_ID={property.HOST_ID}\n")

        console.print(f"✅ Properties successfully saved to [bold]{property.ENV_FILE}[/bold].")

    http_code, http_response = await api.start_session(__version__)
    if server_error(http_code, http_response):
        return None

    session_id = http_response["session_id"]
    max_prompt_attempts = int(http_response["max_prompt_attempts"])

    console.print("ℹ️ Enter [bold]/help[/bold] to view commands. Use [bold]/new[/bold] to restart. Exit with [bold]/exit[/bold] or [bold]Ctrl+C[/bold].")
    console.print("_" * 50)

    while True:
        try:
            user_ask = Prompt.ask("configen").strip()
            if not user_ask:
                continue
            if user_ask == "/exit":
                console.print("👋 Goodbye boss!")
                break
            elif user_ask == "/help":
                console.print("""
[bold cyan]Available commands:[/bold cyan]

  [bold]/help[/bold]  Show this help message  
  [bold]/new[/bold]   Restart the session  
  [bold]/exit[/bold]  Exit the CLI
""")
            elif user_ask == "/new":
                console.print("🔄 Restarting Configen session...")
                return await run_repl()
            else:
                http_code, http_response = await api.followup_conversation(session_id, user_ask)
                if server_error(http_code, http_response):
                    return None

                pma = max_prompt_attempts
                completed = False

                while not completed and pma > 0:
                    if "commands" in http_response:
                        for command in http_response["commands"]:
                            console.print(f"▶️ [yellow]{command["command"]}[/yellow]")
                            run_code, run_out = runner.run(command["command"])
                            console.print(f"👉 [blue]{run_out}[/blue]")
                            console.print("_" * 50)

                            if run_code == 10:
                                console.print(f"[bold red]{run_out}[/bold red]")
                                return None
                            elif run_code == 1:
                                cli_input = f"When running the command {command["command"]}, the following error occurred: {run_out}"
                                http_code, http_response = await api.followup_conversation(session_id, cli_input)
                                if server_error(http_code, http_response):
                                    return None
                                else:
                                    continue
                            elif command.get("note"):
                                cli_input = None
                                if command.get("note") == "output required":
                                    cli_input = f"You requested the output of {command["command"]} and here it is: {run_out}"
                                if command.get("note") == "continue":
                                    cli_input = f"You requested to continue after {command["command"]}."
                                http_code, http_response = await api.followup_conversation(session_id, cli_input)
                                if server_error(http_code, http_response):
                                    return None
                                else:
                                    continue
                    elif "question" in http_response:
                        console.print(f"❓ [bold]Question:[/bold] {http_response["question"]}")
                        user_answer = Prompt.ask("answer").strip()
                        cli_input = f"You asked: {http_response["question"]}, user has responded with: {user_answer}."
                        http_code, http_response = await api.followup_conversation(session_id, cli_input)
                        if server_error(http_code, http_response):
                            return None
                        else:
                            continue
                    elif "completed" in http_response:
                        if http_response["completed"]:
                            console.print(f"✅ [bold green]{http_response["message"]}[/bold green]")
                        else:
                            console.print(f"❌ [bold red]{http_response["message"]}[/bold red]")
                        completed = True
                        break
                    pma -= 1

                if not completed and pma == 0:
                    console.print(f"🤷‍ [bold yellow]Tried {max_prompt_attempts} times but couldn’t complete the task. Try asking more specifically.[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n👋 Goodbye boss!")
            break


@app.callback()
def cli(ctx: typer.Context, version_flag: bool = typer.Option(None, "--version", "-v", is_eager=True, help="Show the Configen CLI version and exit", ), ):
    if version_flag:
        console.print(f"Version: {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        asyncio.run(run_repl())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        asyncio.run(run_repl())
    else:
        app()
