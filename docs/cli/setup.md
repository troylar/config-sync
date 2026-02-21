# devsync setup

Configure your LLM provider for AI-powered extraction and installation. This is a one-time setup.

## Usage

```
$ devsync setup
```

No options. The command runs an interactive wizard.

## What It Does

1. **Provider selection** -- choose Anthropic, OpenAI, or OpenRouter
2. **API key detection** -- checks for environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`)
3. **Model override** -- optionally specify a non-default model
4. **Save configuration** -- writes to `~/.devsync/config.yaml`

## Example

```
$ devsync setup

? Select LLM provider:
  1. Anthropic (Claude)
  2. OpenAI
  3. OpenRouter
> 1

? API key found in ANTHROPIC_API_KEY. Use it? [Y/n]: y

? Override default model? (claude-sonnet-4-20250514) [y/N]: n

Configuration saved to ~/.devsync/config.yaml
```

## Supported Providers

| Provider | Env Variable | Default Model |
|----------|-------------|--------------|
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4o` |
| OpenRouter | `OPENROUTER_API_KEY` | `anthropic/claude-sonnet-4-20250514` |

## Configuration File

The configuration is stored at `~/.devsync/config.yaml`:

```yaml
llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
```

!!! warning "Security"
    API keys are **never** written to disk. Only the provider name and model are saved. Keys are read from environment variables at runtime.

## When Is Setup Required?

Setup is required before using AI-powered extraction or installation. If you skip setup:

- Commands with `--no-ai` still work (file-copy mode)
- `devsync tools` works without setup
- `devsync list` and `devsync uninstall` work without setup

## Re-running Setup

Run `devsync setup` again to change your provider or model. The new configuration overwrites the previous one.
