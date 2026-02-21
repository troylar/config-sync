"""Setup command for configuring LLM provider."""

from rich.console import Console
from rich.prompt import Confirm, Prompt

from devsync.llm.config import LLMConfig, load_config, save_config
from devsync.llm.provider import resolve_provider

console = Console()

_PROVIDER_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

_PROVIDER_DEFAULTS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "openrouter": "anthropic/claude-sonnet-4-20250514",
}


def setup_command() -> int:
    """Interactive setup for LLM provider configuration."""
    console.print("\n[bold]DevSync Setup[/bold]")
    console.print("Configure your LLM provider for AI-powered features.\n")

    existing = load_config()
    if existing.provider:
        console.print(f"Current provider: [cyan]{existing.provider}[/cyan]")
        if not Confirm.ask("Reconfigure?", default=False):
            return 0

    provider_name = Prompt.ask(
        "Select provider",
        choices=["anthropic", "openai", "openrouter"],
        default="anthropic",
    )

    env_var = _PROVIDER_ENV_VARS[provider_name]
    default_model = _PROVIDER_DEFAULTS[provider_name]

    console.print("\nSet your API key as an environment variable:")
    console.print(f"  [cyan]export {env_var}=your-key-here[/cyan]")
    console.print("\nAdd this to your shell profile (~/.zshrc, ~/.bashrc) for persistence.\n")

    model = Prompt.ask("Model", default=default_model)

    provider = resolve_provider(preferred_provider=provider_name, preferred_model=model)
    if provider:
        console.print("Validating API key...", end=" ")
        if provider.validate_api_key():
            console.print("[green]valid[/green]")
        else:
            console.print("[red]invalid[/red]")
            console.print(f"[yellow]Check that {env_var} is set correctly.[/yellow]")
            if not Confirm.ask("Save config anyway?", default=False):
                return 1
    else:
        console.print(f"[yellow]{env_var} not set in current environment.[/yellow]")
        console.print("Config will be saved — set the env var before using AI features.\n")

    config = LLMConfig(provider=provider_name, model=model, env_var=env_var)
    save_config(config)

    console.print(f"\n[green]Config saved.[/green] Provider: {provider_name}, Model: {model}")
    console.print(f"API key env var: {env_var}")
    return 0
