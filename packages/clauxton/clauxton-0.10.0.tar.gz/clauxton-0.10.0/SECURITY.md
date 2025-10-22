# Security Policy

## Supported Versions

We provide security updates for the following versions of Clauxton:

| Version | Supported          |
| ------- | ------------------ |
| 0.10.x  | :white_check_mark: |
| 0.9.x   | :white_check_mark: |
| < 0.9   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Clauxton, please report it responsibly:

### Where to Report

- **Email**: [nakishiyaman@gmail.com](mailto:nakishiyaman@gmail.com)
- **Subject Line**: `[SECURITY] Clauxton Vulnerability Report`
- **GitHub Security Advisories**: [Report via GitHub](https://github.com/nakishiyaman/clauxton/security/advisories/new)

### What to Include

Please include the following information in your report:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential impact if exploited
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Affected Versions**: Which versions are affected
5. **Suggested Fix**: (Optional) Your suggestion for fixing the issue

### Response Timeline

- **Acknowledgment**: Within 48 hours of report
- **Initial Assessment**: Within 7 days
- **Fix Target**: Within 30 days for critical vulnerabilities, 90 days for others
- **Public Disclosure**: After fix is released (coordinated disclosure)

### Bug Bounty

We currently do not offer a bug bounty program, but we deeply appreciate responsible disclosure and will publicly acknowledge security researchers who help improve Clauxton's security (with permission).

---

## Security Considerations

### Threat Model

Clauxton operates on the following security assumptions:

1. **Local Environment**: Clauxton is designed for local development use
2. **Trusted User**: The user running Clauxton is trusted
3. **File System Access**: Clauxton requires read/write access to `.clauxton/` directory
4. **No Network Access**: Clauxton does not make network requests (except for MCP server)

### Attack Surfaces

#### 1. YAML Parsing

**Risk**: YAML deserialization attacks (code execution via dangerous tags)

**Mitigation**:
- Uses `yaml.safe_load()` (not `yaml.load()`)
- Blocks dangerous YAML tags (`!!python`, `!!exec`, etc.)
- Validates YAML structure before processing

**Example Blocked Attack**:
```yaml
# This will be rejected:
!!python/object/apply:os.system
args: ['rm -rf /']
```

#### 2. File System Operations

**Risk**: Path traversal attacks, arbitrary file read/write

**Mitigation**:
- All operations confined to `.clauxton/` directory
- Path validation and normalization
- Restrictive file permissions (600 for files, 700 for directories)
- No symbolic link following outside `.clauxton/`

**Example**:
```python
# Path traversal is prevented:
# Even if user provides "../../../etc/passwd",
# Clauxton only operates within .clauxton/
```

#### 3. User Input

**Risk**: Command injection, XSS (if displayed in web UI)

**Mitigation**:
- Input validation via Pydantic models
- No shell command execution with user input
- Enum-based category validation
- String length limits enforced

**Safe Input Handling**:
```python
# User input is never executed as shell commands
task_name = "task; rm -rf /"  # Stored as literal string
```

#### 4. Log Files

**Risk**: Log injection, sensitive data exposure

**Mitigation**:
- JSON-formatted logs (structured, not concatenated strings)
- Automatic log rotation (30-day retention)
- Restrictive permissions (600)
- Located in `.clauxton/logs/` (user-owned directory)

---

## Safe Usage Guidelines

### For Users

1. **File Permissions**:
   - Ensure `.clauxton/` directory is only accessible by your user
   - Default permissions (700) should not be changed

2. **Input Validation**:
   - Avoid storing sensitive secrets in Knowledge Base entries
   - Review task file paths before execution

3. **Backup Security**:
   - Backups in `.clauxton/backups/` contain full data
   - Secure backups if they contain sensitive information
   - Use `.gitignore` to exclude `.clauxton/` from version control (unless intended)

4. **MCP Server**:
   - MCP server listens on stdio (not network port) - safe
   - Only Claude Code (authorized client) can access MCP tools
   - No authentication required (local communication only)

### For Developers

1. **YAML Safety**:
   - Always use `yaml.safe_load()`, never `yaml.load()`
   - Validate YAML structure after loading
   - Use Pydantic models for validation

2. **File Operations**:
   - Always validate paths stay within `.clauxton/`
   - Use atomic writes (temp file + rename)
   - Create backups before destructive operations
   - Set restrictive permissions (600/700)

3. **Input Validation**:
   - Use Pydantic models for all user input
   - Validate enum values (categories, priorities, statuses)
   - Sanitize strings (no code execution)

4. **Testing**:
   - Run security tests: `pytest tests/security/`
   - Check file permissions in tests
   - Test dangerous YAML payloads

---

## Security Features

### 1. Secure File Storage

- **Permissions**: 600 for files, 700 for directories
- **Atomic Writes**: Temp file + rename (prevents corruption)
- **Automatic Backups**: Timestamped backups with generation limit
- **Encryption**: Not implemented (user responsibility if needed)

### 2. Input Validation

- **Pydantic Models**: Strict type checking and validation
- **Enum Constraints**: Categories, statuses, priorities
- **String Length Limits**: Prevent DoS via large inputs
- **Required Fields**: Enforced by Pydantic

### 3. YAML Safety

- **safe_load Only**: No code execution via YAML tags
- **Structure Validation**: Check for required fields
- **Error Handling**: Graceful degradation on parse errors
- **YAML Bomb Protection**: PyYAML handles alias expansion safely

### 4. Audit Trail

- **Operation Logging**: All operations logged to `.clauxton/logs/`
- **Structured Logs**: JSON Lines format (easy to parse)
- **Automatic Rotation**: 30-day retention
- **Undo Capability**: Recent operations can be reversed

---

## Known Limitations

1. **No Encryption**:
   - Data stored in plaintext YAML
   - Users should encrypt `.clauxton/` if storing sensitive data

2. **No Authentication**:
   - Assumes single-user local environment
   - Not suitable for multi-user systems without additional access controls

3. **No Network Security**:
   - MCP server uses stdio (local only)
   - Not designed for remote access

4. **Limited DoS Protection**:
   - Large YAML files can slow down operations
   - No rate limiting (local tool)

---

## Security Best Practices

### Recommended Setup

```bash
# 1. Initialize Clauxton in project directory
clauxton init

# 2. Verify secure permissions
ls -la .clauxton/
# Should show: drwx------ (700)

# 3. Add to .gitignore (if storing sensitive data)
echo ".clauxton/" >> .gitignore

# 4. (Optional) Encrypt .clauxton directory
# Example with eCryptfs:
# sudo mount -t ecryptfs .clauxton .clauxton
```

### Security Checklist

- [ ] `.clauxton/` has 700 permissions
- [ ] Data files have 600 permissions
- [ ] `.clauxton/` excluded from git (if containing secrets)
- [ ] Regular backups of `.clauxton/` directory
- [ ] No sensitive secrets stored in KB entries
- [ ] Operating system up to date
- [ ] Python dependencies up to date

---

## Security Updates

### How to Update

```bash
# Update to latest version
pip install --upgrade clauxton

# Verify version
clauxton --version

# Check for security advisories
# https://github.com/nakishiyaman/clauxton/security/advisories
```

### Changelog

Security-related changes are marked with 🔒 in [CHANGELOG.md](CHANGELOG.md).

---

## Contact

For security-related questions or concerns:

- **Email**: nakishiyaman@gmail.com
- **GitHub Issues**: [Report Issue](https://github.com/nakishiyaman/clauxton/issues) (for non-sensitive issues)
- **GitHub Security**: [Security Advisories](https://github.com/nakishiyaman/clauxton/security/advisories)

---

**Last Updated**: 2025-10-21
**Version**: 0.10.0
