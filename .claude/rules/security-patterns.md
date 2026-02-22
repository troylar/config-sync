# Security Patterns

> Vision principle: **"Credential safety."** Credentials never in repos, always prompted or from environment variables. DevSync touches file systems, Git repos, and MCP server configs — security here means safe file operations and credential handling.

These patterns are enforced on ALL code in this repository. Violations must be fixed before committing.

## Forbidden — Never Generate These

- `eval()`, `exec()`, `compile()` with any user-controlled input
- `subprocess` calls with `shell=True` and user input
- Hardcoded secrets, API keys, passwords, or tokens
- `pickle.loads()` on untrusted data
- Logging of passwords, API keys, or credentials
- Path traversal via unsanitized `..` in file operations
- Writing credentials to manifest files, installation records, or package trackers
- `verify=False` or `rejectUnauthorized: false` in HTTP/TLS clients

## Required Patterns

### File Operations
- Validate all file paths before read/write operations
- Prevent path traversal: reject paths containing `..` that escape intended directories
- Validate file extensions match expected types
- Check file sizes before reading (prevent memory exhaustion)
- Use `pathlib.Path` over string manipulation for path construction

### Git Operations
- Never embed credentials in Git URLs
- Sanitize repository URLs before passing to Git commands
- Validate Git output before parsing (don't assume format)
- Use `subprocess` with `shell=False` for all Git operations

### Credential Handling
- MCP server credentials: prompt at install time or read from environment
- Never store credential values in `.devsync/packages.json` or `.devsync/installations.json`
- Never log credential values, even at debug level
- Credential environment variable names (not values) may be stored in manifests

### Input Validation
- Validate all input at system boundaries (CLI args, manifest files, Git output)
- Allowlists over denylists for validation
- YAML parsing: use `yaml.safe_load()`, never `yaml.load()` without SafeLoader
- Validate manifest structure before accessing nested fields

### Package Security
- Verify file checksums when specified in manifests
- Validate package manifests before installation
- Reject packages with paths that escape the package directory
- Warn on packages that modify security-sensitive paths

## When Adding New Features

1. Validate all input parameters at the entry point
2. Use `pathlib.Path.resolve()` to canonicalize paths
3. Never interpolate user input into shell commands
4. Log security-relevant events (installation, credential prompts, conflicts)
5. Test with adversarial inputs (paths with `..`, oversized files, malformed YAML)
