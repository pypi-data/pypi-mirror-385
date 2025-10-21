## 🖥️ Platform-Specific PR

**Platform**: [ ] CUDA (PC) [ ] Metal (Mac)

## 📋 Description
<!-- Describe your platform-specific changes -->

## 🧪 Hardware Tested On
<!-- Specify exact hardware configuration -->
- **GPU/Processor**:
- **Memory**:
- **OS Version**:
- **Driver Version**:

## 📊 Performance Benchmarks

### Clifford Circuits
| Qubits | Gates | Baseline Time | Platform Time | Speedup |
|--------|-------|---------------|---------------|---------|
| 10 | 50 | | | |
| 20 | 100 | | | |
| 50 | 200 | | | |

### General Circuits (with T gates)
| Qubits | Gates | Baseline Time | Platform Time | Speedup |
|--------|-------|---------------|---------------|---------|
| 8 | 20 | | | |
| 12 | 50 | | | |
| 16 | 100 | | | |

### Memory Usage
- Peak GPU/Unified Memory:
- Largest circuit tested:

## ✅ Platform Testing Checklist

### CUDA Specific
- [ ] CUDA tests pass (`pytest tests/test_cuda_backend.py`)
- [ ] Performance validation passes (`python benchmarks/cuda_performance_validation.py`)
- [ ] GPU memory management tested
- [ ] CPU fallback works correctly
- [ ] Windows compatibility verified
- [ ] Linux compatibility verified

### Metal Specific
- [ ] Metal/JAX tests pass
- [ ] Performance benchmarks documented
- [ ] Unified memory tested
- [ ] macOS 12.0+ compatibility
- [ ] M1/M2/M3/M4 tested

## 🔄 Cross-Platform Considerations
<!-- How do these changes affect other platforms? -->

## 📝 Notes for Other Platform Team
<!-- Any special considerations for the other platform -->

## 🚦 Ready for Merge?
- [ ] All platform-specific tests pass
- [ ] Performance meets or exceeds targets
- [ ] No regressions in shared code
- [ ] Documentation updated
- [ ] Benchmarks recorded

---

**Reviewer from other platform**: Please test these changes don't break your platform!
