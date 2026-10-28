# Security Policy & Architecture

## 1. Defensive Purpose & Legal Boundaries
**Router Health Checker** is strictly an educational, defensive, read-only diagnostic utility designed to verify and strengthen the security posture of the user's **own Wi-Fi router** or networks for which the user holds explicit written authorization.

- **Non-Intrusive & Read-Only**: The application never exploits vulnerabilities, alters firewall rules, modifies administrative settings, or carries out denial-of-service tests.
- **Compliance**: Adheres to ethical penetration testing guidelines and Indian Information Technology Act 2000 (Sections 43 & 66), as well as international unauthorized access statutes.
- **Hard Target Restrictions**: Automated checks strictly discard public IP addresses and accept only RFC 1918 private IPv4 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) and link-local ranges (`169.254.0.0/16`). Public hostnames, domain names, and external ranges are outright rejected to eliminate Server-Side Request Forgery (SSRF).

---

## 2. Threat Model & OWASP Top 10 Mitigations

| Threat (OWASP) | Risk in Local Security Tools | Mitigation in Router Health Checker |
| :--- | :--- | :--- |
| **A01: Broken Access Control** | Unauthorized triggers of network scans | Session cookie validation (`SameSite=Strict`, `HttpOnly`), mandatory user consent gate before scanning, user data isolation in SQLite. |
| **A02: Cryptographic Failures** | Weak password storage, plain credentials | Argon2id hashing for local user accounts, TLS enforcement options, secrets isolated in `.env`. |
| **A03: Injection** | Command injection via network tools (`ping`, `arp`, `netsh`) | Safe subprocess argument lists without shell wrappers (`shell=False`); strict input regex validation for IP addresses and nicknames. |
| **A04: Insecure Design** | Tool abused as a scanning proxy against the internet | Strict `ipaddress` RFC 1918 checks. Scans bounded to a maximum of 9 defined router ports. |
| **A05: Security Misconfiguration** | Missing security headers, exposed CORS | Strict Content Security Policy (CSP), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, CORS restricted to same origin. |
| **A06: Vulnerable & Outdated Components** | Outdated libraries | Pinned package versions in `requirements.txt`, automated GitHub Actions security scanning with `pip-audit`. |
| **A07: Identification & Authentication Failures** | Brute force against local dashboard | Account lockout with exponential delay after 5 failed login attempts; constant-time hash comparisons. |
| **A08: Software & Data Integrity Failures** | Malicious script injection | Strict CSP disallowing inline script execution; vendored Chart.js and local SVG assets; no external unverified CDN dependencies. |
| **A09: Security Logging & Monitoring Failures** | Unaudited network scans | Structured audit logging into local SQLite `audit_log` and rotating text log without logging plaintext credentials. |
| **A10: Server-Side Request Forgery (SSRF)** | Using the scanner backend to pivot to intranet or public endpoints | Strict private IP validation parser; strict timeout bounds (≤ 1.5s per socket); hardcoded probe targets. |

---

## 3. Production Deployment Guidelines

1. **Host Binding**:
   - By default, the application binds strictly to loopback: `127.0.0.1:8000`.
   - Never bind to `0.0.0.0` on untrusted networks unless fronted by a reverse proxy with TLS and firewall rules.
2. **Reverse Proxy (Nginx / Caddy)**:
   - When serving to multiple devices in a home or lab, place behind Caddy or Nginx with automated Let's Encrypt or local CA certificates.
3. **Environment Hardening**:
   - Ensure the `.env` file has restricted file system permissions (`chmod 600 .env` on Unix).

---

## 4. Responsible Disclosure
If you discover any security issue or vulnerability within this application, please report it privately via GitHub Security Advisories or by emailing security@routerhealth.local. We commit to acknowledging reports within 48 hours and providing a remediation patch promptly.
