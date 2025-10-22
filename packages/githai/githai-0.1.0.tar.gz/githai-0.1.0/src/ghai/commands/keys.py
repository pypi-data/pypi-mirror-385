"""Keys management commands for GHAI CLI."""

import click

from ghai.util import KeyUtil


@click.group()
@click.pass_context
def keys(ctx: click.Context) -> None:
    """Manage API keys and tokens"""


@keys.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """List stored API keys"""
    keys_data = KeyUtil.list_keys()

    if not keys_data:
        click.echo("No API keys stored.")
        click.echo("\nTo add a key, use: ghai keys set <key_name>")
        return

    click.echo("=" * 50)
    click.echo("List of API Keys / Settings!")
    click.echo("=" * 50)

    default_model = keys_data.get("DEFAULT_MODEL")
    if default_model:
        click.echo(f"DEFAULT_MODEL: {default_model}")
        click.echo("-" * 50)

    other_keys = {k: v for k, v in keys_data.items() if k != "DEFAULT_MODEL"}

    if other_keys:
        for key_name in sorted(other_keys.keys()):
            value = other_keys[key_name]
            click.echo(f"{key_name}: {value}")


@keys.command()
@click.argument("name")
@click.option(
    "--value",
    prompt="Enter key",
    hide_input=True,
    help="Value to set (will prompt securely if not provided)",
)
@click.pass_context
def set(ctx: click.Context, name: str, value: str) -> None:
    """Set an API key or token.

    Example usage:

    \b
        $ ghai keys set GITHUB_TOKEN
        Enter key: ...

        $ ghai keys set OPENAI_API_KEY --value your_token_here
    """
    try:
        KeyUtil.set_key(name, value)
        click.echo(f"✓ Key '{name}' has been set successfully.")

        # Special handling for GITHUB_TOKEN
        if name == "GITHUB_TOKEN":
            click.echo("\n💡 Tip: Your GITHUB_TOKEN is now stored securely.")
            click.echo(
                "   The CLI will automatically use this token for GitHub API calls.")

    except ValueError as e:
        raise click.ClickException(str(e))


@keys.command()
@click.pass_context
def path(ctx: click.Context) -> None:
    """Show the path to the keys.json file."""
    keys_path = KeyUtil.get_keys_file_path()

    if keys_path.exists():
        click.echo(f"Keys file path: {keys_path}")
    else:
        click.echo("Keys file does not exist")
        click.echo("It will be created when you set your first key")


@keys.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this key?")
@click.pass_context
def delete(ctx: click.Context, name: str) -> None:
    """Delete a stored API key."""
    if KeyUtil.delete_key(name):
        click.echo(f"✓ Key '{name}' has been deleted.")
    else:
        raise click.ClickException(f"Key '{name}' not found.")


@keys.command("set-default-model")
@click.argument("model_name")
@click.pass_context
def set_default_model(ctx: click.Context, model_name: str) -> None:
    """Set the default AI model to use.

    Example usage:

    \b
        $ ghai keys set-default-model github/gpt-4o-mini
        $ ghai keys set-default-model gpt-4
        $ ghai keys set-default-model claude-3-sonnet
    """
    KeyUtil.set_default_model(model_name)

    click.echo(f"✓ Default model set to: {model_name}")
    click.echo("\n💡 This model will be used by default in all commands.")


@keys.command()
@click.pass_context
def get_default_model(ctx: click.Context) -> None:
    """Show the current default AI model."""
    default_model = KeyUtil.get_default_model()

    if default_model:
        click.echo(f"Current default model: {default_model}")
    else:
        click.echo("No default model set.")
        click.echo(
            "\nTo set a default model, use: ghai keys set-default-model <model_name>")
        click.echo("Available models include:")
        click.echo("  - github/gpt-4o-mini (requires GitHub PAT)")
        click.echo("  - github/claude-3-haiku (requires GitHub PAT)")
        click.echo("  - gpt-4 (requires OpenAI API key)")
        click.echo("  - claude-3-sonnet (requires Anthropic API key)")


@keys.command()
@click.confirmation_option(prompt="Are you sure you want to clear the default model?")
@click.pass_context
def clear_default_model(ctx: click.Context) -> None:
    """Clear the default AI model setting."""
    if KeyUtil.delete_key("DEFAULT_MODEL"):
        click.echo("✓ Default model has been cleared.")
        click.echo("Commands will now use their built-in default models.")
    else:
        click.echo("No default model is currently set.")
        click.echo("No default model is currently set.")
