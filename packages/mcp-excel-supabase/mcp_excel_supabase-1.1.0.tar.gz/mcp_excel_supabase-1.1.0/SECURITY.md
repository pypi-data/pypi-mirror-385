# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Excel MCP Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **hikaru_lamperouge@163.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Security Best Practices

### API Keys and Credentials

- **Never commit** `.env` files or any files containing API keys to version control
- Use environment variables for all sensitive configuration
- Rotate your Supabase service role keys regularly
- Use the principle of least privilege when configuring Supabase permissions

### Supabase Storage Security

- Configure Row Level Security (RLS) policies on your Supabase buckets
- Use signed URLs for temporary access to files
- Validate file types and sizes before upload
- Implement rate limiting on file operations

### Input Validation

- All user inputs are validated using the `Validator` class
- File paths are sanitized to prevent path traversal attacks
- Excel file sizes are limited to prevent DoS attacks
- Cell ranges are validated to prevent formula injection

### Dependencies

- We use `pip-audit` to scan for known vulnerabilities in dependencies
- Dependencies are kept up-to-date with security patches
- We follow semantic versioning for dependency updates

## Known Security Considerations

### 1. Formula Execution

The formula engine executes Excel formulas using the `formulas` library. While this library is well-maintained, be aware that:

- Complex formulas may consume significant CPU resources
- Circular references are detected and prevented
- Formula execution is sandboxed within the Python environment

### 2. File Upload/Download

When using Supabase Storage:

- Files are stored in your Supabase bucket with your configured permissions
- The service role key has full access to all buckets
- Consider using signed URLs for client-side uploads/downloads
- Implement file size limits and type validation

### 3. Environment Variables

The server requires the following environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase service role key (keep this secret!)
- `DEFAULT_BUCKET`: (Optional) Default bucket name

**Important**: The service role key bypasses Row Level Security. Use it only in trusted server environments.

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and announced via:

- GitHub Security Advisories
- GitHub Releases
- Project README

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release new security fix versions as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue to discuss.

## Attribution

This security policy is adapted from the [GitHub Security Policy template](https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository).

