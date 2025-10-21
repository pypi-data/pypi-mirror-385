# 📘 License Appendix – Educational Use and Liability Statement

**Project:** PE-Packer  
**Primary License:** Apache-2.0  
**Effective Date:** 2025-10-15  

---

## 1. Purpose of This Appendix

This appendix supplements the main license file to clarify the **intended scope and ethical limitations** of the PE-Packer project.

The purpose of PE-Packer is **educational and research-oriented learning** about the Windows Portable Executable (PE) format, static analysis, and safe unpacking.  
It is **not designed or authorized** for use in software concealment, obfuscation, or malware deployment of any kind.

This clarification does not alter the legal permissions of the MIT or Apache-2.0 license but provides additional binding terms of **responsible use** and **liability disclaimers** specific to this project.

---

## 2. Educational-Use Intent

By obtaining, using, or redistributing this software, you acknowledge that:

- The software is provided **solely for authorized research, teaching, academic, or defensive cybersecurity education**.  
- It **must not** be used to disguise or distribute executables, payloads, or binaries outside a controlled educational or testing environment.  
- You assume **full responsibility** for ensuring compliance with your institution’s and jurisdiction’s cybersecurity laws and policies.

---

## 3. Safety Controls

PE-Packer enforces a **safety gating system**:

1. Binary packing functionality is **disabled by default**.  
2. Activation requires both:
   - The environment variable `PE_PACKER_ALLOW_PACKING=1`, **and**
   - The command-line flag `--force`.

This gating mechanism exists to prevent accidental or unauthorized generation of packed executables.

---

## 4. No Warranty or Liability

Consistent with the MIT and Apache-2.0 licenses:

- The software is provided **“as is,” without warranty of any kind**, express or implied.  
- Under no circumstances shall the authors, contributors, or affiliated institutions be liable for **any claim, damages, or other liability** arising from misuse, modification, or redistribution of this software.  
- You are solely responsible for ensuring compliance with all applicable laws, export regulations, and institutional policies.

---

## 5. Academic Citation

If you use PE-Packer in an academic, instructional, or research context, please cite the repository as follows:

> **Tutu, A.M. (2025). PE-Packer: An Educational PE File Packing Laboratory.**  
> Available at: [https://github.com/codeamt/rust-python-pe-packer](https://github.com/codeamt/rust-python-pe-packer)

---

## 6. Contact

| Purpose | Contact |
|----------|----------|
| General inquiries | annmargaret.mailforce@gmail.com |
| Security disclosures | annmargaret.mailforce@gmail.com |
| License & institutional use | annmargaret.mailforce@gmail.com |

---

*This appendix is intended to reinforce ethical, transparent, and responsible software distribution practices in alignment with open-source security research standards.*