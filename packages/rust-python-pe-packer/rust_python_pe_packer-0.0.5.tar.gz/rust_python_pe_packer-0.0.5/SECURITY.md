📄 SECURITY.md

# 🔒 Security Policy & Responsible Use

**Last updated:** 2025-10-15  
**Project:** PE-Packer (Educational Portable Executable Laboratory)

---

## 🧭 Purpose and Scope

PE-Packer is provided **for educational and research purposes only.**  
Its goal is to help students, educators, and security researchers understand the PE (Portable Executable) file format, metadata, and defensive unpacking workflows.

The software **does not and must not** be used to conceal, obfuscate, or distribute real software or code in a way that could mislead users, bypass detection systems, or facilitate unauthorized activity.

---

## ⚠️ Safe Defaults

All distributed builds of PE-Packer are **hardened** and **disable binary packing by default.**

To intentionally enable packing functionality, a user must:
1. Set the environment variable  
   ```bash
   export PE_PACKER_ALLOW_PACKING=1

2. Use the CLI flag

--force



These steps exist to prevent accidental or unauthorized binary generation.
Without both conditions, all CLI operations run in dry-run (analysis-only) mode.


---

🛡️ Ethical and Legal Use

By using or redistributing this software, you agree to the following:

Use it only for authorized research, educational instruction, reverse-engineering training, or defensive security purposes.

Do not use it on systems, binaries, or environments for which you lack explicit permission.

Do not distribute packed executables or derivative tools that bypass these safeguards.

Do not remove or alter safety warnings, disclaimers, or gating mechanisms.


Violation of these terms may violate applicable laws or institutional policies.


---

🧪 Reporting Security Issues

If you discover a vulnerability, defect, or security concern within this project, please report it privately.

Preferred method:

Email: annmargaret.mailforce@gmail.com

Subject: Security Disclosure – PE-Packer


Alternative:

Open a GitHub issue labeled security without including exploit samples or sensitive data.


We will acknowledge receipt within 5 business days, and coordinate a responsible fix or clarification as appropriate.


---

🔐 Safe Release Process

All builds are verified by continuous-integration tests (test_safety.py) before any PyPI or GitHub release.

Releases require an explicit CI secret (ALLOW_PYPI_RELEASE=true) to prevent accidental publication.

The repository automatically blocks release workflows if the safety suite fails.



---

📜 Disclaimer of Liability

The authors and maintainers of PE-Packer disclaim all liability for any misuse of this software.
Use of this repository constitutes agreement that the user assumes full responsibility for compliance with applicable laws and ethical guidelines.


---

📬 Contact: annmargaret.mailforce@gmail.com



---

Thank you for helping us maintain a safe, educational, and transparent research environment.

---