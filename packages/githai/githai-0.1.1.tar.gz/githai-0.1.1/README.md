# GITHAI CLI

A CLI tool that combines GitHub's API with the [LLM API](https://llm.datasette.io/en/stable/python-api.html) to help you understand, analyze, and work with GitHub repositories and issues more effectively.

## Quick Start

```bash
# Install the CLI
pip install githai

# Set up your GitHub token (required for GitHub API access)
ghai keys set GITHUB_TOKEN

# Analyze a GitHub issue with AI
ghai explain-issue --issue-url https://github.com/owner/repo/issues/123

# List available commands
ghai --help
```

## API Keys and Model Configuration

GHAI supports multiple AI models from different providers. You can configure API keys for the following services:

### Supported Models and Keys

- **GitHub Models**

  - `github/gpt-4o-mini`
  - `github/claude-3-haiku`
  - `etc...`
  - Requires: `GITHUB_TOKEN`

- **OpenAI Models**

  - `gpt-4`
  - `gpt-3.5-turbo`
  - `etc...`
  - Requires: `OPENAI_API_KEY`

- **Anthropic Models**
  - `claude-3-sonnet`
  - `claude-3-haiku`
  - `etc...`
  - Requires: `ANTHROPIC_API_KEY`

### Setting API Keys

```bash
# GitHub token (required for all GitHub API access)
ghai keys set GITHUB_TOKEN

# OpenAI API key (for OpenAI models)
ghai keys set OPENAI_API_KEY

# Anthropic API key (for Anthropic models)
ghai keys set ANTHROPIC_API_KEY

# List all stored keys
ghai keys list

# Show the path to your keys file
ghai keys path
```

### Default Model Configuration

Set a default model to use across all commands:

```bash
# Set default model (recommended: use free GitHub models)
ghai keys set-default-model github/gpt-4o-mini

# View current default model
ghai keys get-default-model

# Clear default model setting
ghai keys clear-default-model
```

If no default model is set, commands will use their built-in defaults.

### Key Management

```bash
# Delete a specific key
ghai keys delete OPENAI_API_KEY

# View all available key management commands
ghai keys --help
```

## Example Commands and Usage

### Explain Issue

Analyze GitHub issues with AI to get detailed explanations, context, and insights:

```bash
# Analyze a GitHub issue using the default prompt
ghai explain-issue --issue-url https://github.com/owner/repo/issues/123

# Use a custom prompt file
ghai explain-issue --issue-url https://github.com/owner/repo/issues/123 --prompt custom_prompt.md

# Short form
ghai explain-issue -u https://github.com/owner/repo/issues/123 -p custom_prompt.md
```

### Progress Update

Get progress updates on GitHub issues and their related sub-issues:

```bash
# Get progress update using default prompt
ghai progress-update --issue-url https://github.com/owner/repo/issues/123

# Use a custom prompt file
ghai progress-update --issue-url https://github.com/owner/repo/issues/123 --prompt progress_prompt.md

# Short form
ghai progress-update -u https://github.com/owner/repo/issues/123 -p progress_prompt.md
```

## Custom Prompts

Most commands support custom prompts to tailor the AI analysis to your specific needs.

### Using Custom Prompts

1. **Create your prompt file** in Markdown format
2. **Use the `--prompt` option** with any command:
   ```bash
   ghai explain-issue -u <issue-url> --prompt your-custom-prompt.md
   ```
3. **Path resolution**: Prompts can be specified with:
   - Absolute paths: `/full/path/to/prompt.md`
   - Relative paths: `./prompts/custom.md`

Use [prompt best practices](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api).

## Project Structure

```
ghai/
├── src/
│   └── ghai/
│       ├── __init__.py
│       ├── cli.py              # Main CLI entry point
│       ├── github_api.py       # GitHub GraphQL API client
│       ├── llm_api.py          # AI/LLM integration
│       ├── commands/           # Command modules
│       │   ├── __init__.py
│       │   ├── explain_issue.py    # Issue analysis command
│       │   ├── snippet_update.py   # Code snippet updates
│       │   ├── progress_update.py  # Progress reporting
│       │   └── keys.py             # Key management
│       ├── types/              # Type definitions
│       │   └── github_api_types.py
│       └── util/
│           ├── __init__.py
│           └── key_util.py  # Key utility functions
├── prompts/                    # AI prompt templates
│   ├── explain_issue_prompt.md
│   ├── initiative_prompt.md
│   └── snippet_prompt.md
├── pyproject.toml
└── README.md
```

## License

MIT License
