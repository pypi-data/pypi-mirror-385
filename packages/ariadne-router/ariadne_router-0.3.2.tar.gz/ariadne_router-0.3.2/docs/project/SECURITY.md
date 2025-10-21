# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Ariadne seriously. If you have discovered a security vulnerability, please follow these steps:

### 1. Do NOT Create a Public Issue
Security vulnerabilities should **never** be reported through public GitHub issues.

### 2. Report via GitHub Security Policy
Please report vulnerabilities through the repository's **Security Policy**:
https://github.com/Hmbown/ariadne/security/policy

Include the following information:
- Type of vulnerability
- Affected components
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. What to Expect
- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Regular Updates**: Every 2 weeks until resolved
- **Public Disclosure**: Coordinated after fix is available

### 4. Responsible Disclosure
We kindly ask that you:
- Give us reasonable time to address the issue
- Not exploit the vulnerability beyond necessary testing
- Not share the vulnerability publicly until we've addressed it

## Security Best Practices for Users

### When Using Ariadne:
1. **Keep Updated**: Always use the latest version
2. **Secure Your Environment**: Don't expose Ariadne services to the internet
3. **API Keys**: Never commit API keys or credentials if using cloud backends
4. **Input Validation**: Validate quantum circuits from untrusted sources

### For CUDA Users:
- Ensure CUDA drivers are up to date
- Be cautious with untrusted circuit files that could exploit GPU memory
- Monitor GPU memory usage for unusual patterns

## Security Features

Ariadne includes several security features:
- Input validation for quantum circuits
- Memory limits for circuit simulation
- Safe deserialization of circuit data
- No execution of arbitrary code

## Acknowledgments

We appreciate responsible disclosure from the security community.

---

Thank you for helping keep Ariadne and its users safe! 🔐
