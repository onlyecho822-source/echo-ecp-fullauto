# EchoFile Inspector — Gumroad Product Listing

**Product name:** EchoFile Inspector v3.3 — Forensic File Intelligence Tool  
**Price:** $19  
**File to upload:** EchoFileInspector_v3.3.zip  
**Category:** Software / Security Tools  

---

## SHORT DESCRIPTION (shown in search/cards — 160 chars)

Forensic file inspector for Windows. Detects hidden streams, timestamp manipulation, 
magic byte mismatches, and entropy anomalies. One-click launcher. No install required.

---

## FULL DESCRIPTION

**What it does**

EchoFile Inspector scans files and folders for forensic anomalies that standard file 
browsers miss. Built on the Echo Fabric operator — the same anomaly detection 
mathematics used in the Echo Universe research ecosystem.

**Detects:**
- Alternate Data Streams (hidden data attached to files on Windows NTFS)
- Timestamp inversions (files created after they were modified — a classic sign of manipulation)
- Magic byte vs. extension mismatches (a .pdf that isn't actually a PDF)
- Zero-length files with extensions
- Hidden and System file attributes
- Byte entropy analysis (high entropy = possible encrypted or packed payload)

**Resonance scoring:**
Every file gets an anomaly score 0–100 with a resonance label:
- 🟢 TRUE ECHO (0–19): clean file
- 🟡 WEAK SIGNAL (20–49): minor irregularities
- 🟠 ECHO DRIFT (50–79): significant anomaly
- 🔴 CORRUPTED ECHO (80–100): high priority

**Output:**
- Color-coded console results
- Optional JSON report saved to Desktop
- ζ dual-hash (SHA256+MD5) for every file

**Who it's for:**
- IT professionals doing incident response
- Researchers and journalists verifying file integrity
- Anyone who received a file they don't fully trust
- Digital forensics students

**Technical:**
- Windows 10/11, PowerShell 5.1+
- No installation required — unzip and run
- Double-click the .bat launcher

**What's in the ZIP:**
- EchoFileInspector_v3.3.ps1 (the engine)
- Launch_EchoFileInspector.bat (one-click launcher)
- README.txt (full documentation)

---

## COVER IMAGE COPY

*EchoFile Inspector — See What Your File Browser Can't*

---

*Built by Nathan Poinsette | Echo Universe*
