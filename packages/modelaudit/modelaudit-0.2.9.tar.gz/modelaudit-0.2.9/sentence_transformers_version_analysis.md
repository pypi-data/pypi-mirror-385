# sentence-transformers/all-MiniLM-L6-v2 - ModelAudit Version Analysis

## Executive Summary

This document tracks the evolution of ModelAudit's security detection capabilities for `sentence-transformers/all-MiniLM-L6-v2`, a popular text embedding model, across 10 released versions (0.1.5 → 0.2.8).

**Key Finding**: Version 0.2.7 introduced CVE-2025-32434 detection, revealing that this "safe" model contains dangerous REDUCE opcodes that contradict PyTorch's `weights_only=True` security assumptions.

## Model Introduction

- **Commit**: 56b17c1 (2025-08-23)
- **PR**: #336 - "docs: comprehensive modelscan comparison analysis and documentation"
- **Initial Version**: 0.1.5
- **Purpose**: Baseline clean model for negative control testing (expected to scan clean)
- **Classification**: Safe Model - Safetensors format, no pickle execution risk

## Version-by-Version Scan Results

| Version | Files | Total Issues | Critical | Warning | Info | Exit Code | Status |
|---------|-------|--------------|----------|---------|------|-----------|--------|
| 0.1.5   | N/A   | N/A          | N/A      | N/A     | N/A  | FAILED    | CLI incompatibility - no `hf://` support |
| 0.2.0   | 0     | 138          | 0        | 1       | 56   | 0         | Noisy - false positive PE patterns |
| 0.2.1   | 0     | 0            | 0        | 0       | 0    | 0         | Clean scan ✓ |
| 0.2.2   | 0     | 0            | 0        | 0       | 0    | 0         | Clean scan ✓ |
| 0.2.3   | 0     | 0            | 0        | 0       | 0    | 0         | Clean scan ✓ |
| 0.2.4   | 0     | 0            | 0        | 0       | 0    | 0         | Clean scan ✓ |
| 0.2.5   | 0     | 0            | 0        | 0       | 0    | 0         | Clean scan ✓ |
| 0.2.6   | 0     | 0            | 0        | 0       | 0    | 0         | Clean scan ✓ |
| 0.2.7   | 0     | 213          | 1        | 212     | 0    | 0         | **CVE-2025-32434 detected** ⚠️ |
| 0.2.8   | 0     | 213          | 1        | 212     | 0    | 0         | Same as 0.2.7 |

## Critical Timeline Changes

### v0.1.5 (2025-08-23) - Model Added
- **Status**: Failed to scan
- **Reason**: CLI didn't support `hf://` URL scheme
- **Error**: `No such command 'hf://sentence-transformers/all-MiniLM-L6-v2'`

### v0.2.0 → v0.2.1 - Noise Reduction (-138 issues)
- **Change**: Removed false positive PE pattern warnings
- **Result**: Clean baseline scan achieved
- **Impact**: Model correctly identified as safe

### v0.2.6 → v0.2.7 - CVE-2025-32434 Detection (+213 issues)
- **Change**: PR #384 - "enable advanced TorchScript vulnerability detection"
- **Critical Issue**: PyTorch model contains dangerous REDUCE opcodes
- **Warning Issues**: 208 individual REDUCE opcode detections + 4 opcode sequences
- **Impact**: Model now flagged as potentially unsafe despite using SafeTensors

## The CVE-2025-32434 Critical Issue

### Issue Details
```json
{
  "message": "PyTorch model contains dangerous opcodes (REDUCE) that can execute code even when loaded with torch.load(weights_only=True)",
  "severity": "critical",
  "location": "pytorch_model.bin:archive/data.pkl",
  "cve_id": "CVE-2025-32434",
  "vulnerability_description": "The weights_only=True parameter in torch.load() does not prevent code execution from malicious pickle files",
  "affected_pytorch_versions": "All versions ≤2.5.1",
  "fixed_in": "PyTorch 2.6.0"
}
```

### Impact Analysis
- **Before v0.2.7**: Model appeared completely safe (0 issues)
- **After v0.2.7**: Model flagged with 1 critical + 212 warnings
- **Real-world risk**: The `pytorch_model.bin` file contains 208 REDUCE opcodes that could be exploited
- **Mitigation**: Use `model.safetensors` instead (already available in this model)

## Warning Issue Breakdown (v0.2.7/v0.2.8)

- **208 warnings**: Individual REDUCE opcode detections at specific byte positions
- **4 warnings**: Suspicious opcode sequence patterns (`MANY_DANGEROUS_OPCODES`)
- **1 critical**: Overall CVE-2025-32434 vulnerability summary

### Sample Warning
```
Found REDUCE opcode - potential __reduce__ method execution
Location: pytorch_model.bin:archive/data.pkl (pos 180)
```

## Recommendations Impact

### For Model Publishers (sentence-transformers team)
1. ✅ **Already done**: SafeTensors format available (`model.safetensors`)
2. ⚠️ **Consider**: Deprecate `pytorch_model.bin` in favor of SafeTensors
3. ✅ **Already done**: Model card documents SafeTensors as recommended format

### For Model Consumers
1. **Use SafeTensors**: Load via `model.safetensors` instead of `pytorch_model.bin`
2. **Upgrade PyTorch**: Use PyTorch 2.6.0+ for improved pickle security
3. **Never trust `weights_only=True`**: This provides false sense of security

### For ModelAudit Development
1. ✅ **Successful detection**: CVE-2025-32434 detector works correctly
2. 🔄 **Consider enhancement**: Add guidance distinguishing SafeTensors (safe) vs PyTorch bin (risky) in same repo
3. 🔄 **Future enhancement**: Auto-recommend SafeTensors when both formats present

## Conclusion

This version analysis demonstrates ModelAudit's evolution from basic scanning to sophisticated CVE-specific detection:

1. **v0.1.5**: Couldn't scan (CLI limitation)
2. **v0.2.0**: Noisy with false positives
3. **v0.2.1-0.2.6**: Clean, accurate baseline (6 versions of stable detection)
4. **v0.2.7-0.2.8**: Advanced CVE detection reveals hidden risks

The fact that this "safe" model (listed in docs as clean) now shows critical issues highlights:
- The importance of format choice (SafeTensors > PyTorch pickle)
- The evolution of security knowledge (CVE-2025-32434 discovered later)
- The value of continuous scanning as detection capabilities improve

**Verdict**: The model is safe **if loaded via SafeTensors**, but risky **if loaded via pytorch_model.bin**. ModelAudit correctly identifies this risk as of v0.2.7.

## Appendix: Reproduction Commands

```bash
# Test current version
rye run modelaudit hf://sentence-transformers/all-MiniLM-L6-v2 --format json

# Test specific version (requires virtual environment)
python3 -m venv /tmp/test_venv
source /tmp/test_venv/bin/activate
pip install modelaudit==0.2.7
modelaudit hf://sentence-transformers/all-MiniLM-L6-v2 --format json
deactivate
rm -rf /tmp/test_venv
```

## References

- **Model Repository**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **CVE-2025-32434**: PyTorch weights_only=True bypass vulnerability
- **PR #384**: https://github.com/promptfoo/modelaudit/pull/384
- **PR #336**: https://github.com/promptfoo/modelaudit/pull/336 (where model was added)
- **CHANGELOG**: See CHANGELOG.md for version 0.2.7

---
**Generated**: 2025-10-21
**Analysis Script**: `version_scan_test.sh`, `analyze_version_results.py`
**Scan Results**: `version_scan_results/scan_*.json`
