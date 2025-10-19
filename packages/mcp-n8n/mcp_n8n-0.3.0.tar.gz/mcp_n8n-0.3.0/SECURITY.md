# Security Policy

## Supported Versions

We provide security updates for the following versions of mcp-n8n:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note:** Only the latest minor version receives security updates. We recommend always using the latest release.

---

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in mcp-n8n, please help us by reporting it responsibly.

### How to Report

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, report security issues via one of these methods:

1. **GitHub Security Advisory (Preferred)**
   - Go to: https://github.com/yourusername/mcp-n8n/security/advisories/new
   - This creates a private disclosure that we can discuss before public release

2. **Email**
   - Send to: security@example.com
   - Include "[SECURITY]" in the subject line
   - Encrypt with our PGP key (optional, see below)

3. **Private Message**
   - Contact maintainers directly via GitHub (if urgent)

### What to Include

Please provide as much information as possible:

- **Description:** Clear description of the vulnerability
- **Impact:** What could an attacker do with this vulnerability?
- **Affected versions:** Which versions are impacted?
- **Reproduction steps:** Detailed steps to reproduce the issue
- **Proof of concept:** Code or examples demonstrating the vulnerability
- **Suggested fix:** If you have ideas on how to fix it

**Example Report:**
```
Title: Path traversal in configuration loader

Description: The configuration loader does not properly sanitize file paths,
allowing an attacker to read arbitrary files from the filesystem.

Impact: An attacker could read sensitive files like /etc/passwd or
application secrets by crafting malicious configuration paths.

Affected versions: All versions <= 0.1.0

Reproduction:
1. Create config with path: "../../../etc/passwd"
2. Load configuration
3. Observe file contents returned

Suggested fix: Validate paths with os.path.abspath() and reject paths
outside the expected configuration directory.
```

---

## Response Timeline

We aim to respond to security reports according to this timeline:

| Timeframe | Action |
|-----------|--------|
| 24 hours  | Initial acknowledgment of report |
| 7 days    | Preliminary assessment and severity classification |
| 30 days   | Fix developed and tested |
| 45 days   | Security patch released (if feasible) |

**Note:** Timeline may vary based on severity and complexity. We'll keep you updated throughout the process.

---

## Disclosure Policy

We follow **coordinated disclosure** principles:

1. **Private Disclosure:** You report the vulnerability privately
2. **Assessment:** We assess and develop a fix
3. **Embargo:** We agree on an embargo period (typically 90 days)
4. **Fix Release:** We release a patched version
5. **Public Disclosure:** We publish a security advisory with credits
6. **CVE Assignment:** We request a CVE if applicable

### Public Disclosure

After a fix is released:
- We publish a GitHub Security Advisory
- We credit the reporter (unless they prefer to remain anonymous)
- We update CHANGELOG.md with security fixes
- We notify users via release notes

---

## Security Update Process

When a security issue is fixed:

1. **Patch Release:** We release a new patch version (e.g., 0.1.1)
2. **Security Advisory:** Published on GitHub Security tab
3. **CHANGELOG Update:** Security section added to CHANGELOG.md
4. **User Notification:** Announced in release notes
5. **CVE Issued:** If severity warrants (CVSS ≥ 7.0)

### How to Stay Informed

- **Watch this repository:** Get notified of all releases
- **GitHub Security Advisories:** https://github.com/yourusername/mcp-n8n/security/advisories
- **Dependabot Alerts:** Enable for your projects using mcp-n8n
- **Release Notes:** Check CHANGELOG.md regularly

---

## Security Best Practices for Users

When using mcp-n8n:

### 1. Keep Updated
```bash
# Check current version
pip show mcp-n8n

# Update to latest
pip install --upgrade mcp-n8n
```

### 2. Secure Credentials
- **Never commit** API keys, tokens, or secrets to version control
- Use environment variables or `.env` files (add `.env` to `.gitignore`)
- Rotate credentials regularly
- Use least-privilege API tokens

```bash
# Good: Environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export CODA_API_KEY="..."

# Bad: Hardcoded in config
# "api_key": "sk-ant-..." ❌
```

### 3. Validate Configuration
- Review MCP server configurations before deployment
- Use stable versions in production (not dev mode)
- Verify backend paths and commands
- Limit file system access where possible

### 4. Monitor Dependencies
```bash
# Check for vulnerabilities
pip install pip-audit
pip-audit

# Or use GitHub Dependabot alerts
```

### 5. Secure Transport
- mcp-n8n uses STDIO transport (no network exposure by default)
- If exposing via network, use TLS/SSL
- Restrict access with firewalls or authentication

### 6. Logging & Monitoring
- Review logs regularly: `logs/mcp-n8n.log`
- Monitor for unusual activity
- Set up alerts for errors or failures

---

## Known Security Considerations

### MCP Backend Execution
- mcp-n8n executes subprocess commands for MCP backends
- Ensure backend paths are trusted and validated
- Review backend configurations in `.env` and config files

### Environment Variables
- Sensitive data passed via environment variables
- Ensure proper file permissions on `.env` files: `chmod 600 .env`
- Use secrets management in production (e.g., vault, AWS Secrets Manager)

### Logging
- Logs may contain trace IDs and metadata
- Avoid logging sensitive data (API keys, tokens)
- Secure log files: `chmod 600 logs/*.log`

---

## Security Scanning

This project uses automated security scanning:

- **CodeQL:** Static analysis for vulnerabilities (weekly)
- **Dependency Review:** PR checks for vulnerable dependencies
- **Dependabot:** Automated dependency updates
- **pip-audit:** Python dependency vulnerability scanning

View security status:
- https://github.com/yourusername/mcp-n8n/security

---

## PGP Key (Optional)

For encrypted communications:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
(Your PGP public key here if you want to support encrypted reports)
-----END PGP PUBLIC KEY BLOCK-----
```

**Fingerprint:** `XXXX XXXX XXXX XXXX XXXX  XXXX XXXX XXXX XXXX XXXX`

---

## Acknowledgments

We appreciate security researchers who responsibly disclose vulnerabilities.

**Hall of Fame:**
- (Security researchers will be credited here)

**Thank you for helping keep mcp-n8n secure!** 🔒

---

## Contact

- **Security Issues:** security@example.com
- **GitHub Security:** https://github.com/yourusername/mcp-n8n/security
- **General Issues:** https://github.com/yourusername/mcp-n8n/issues

---

**Last updated:** 2025-10-17
