# SimpleFeed++ Native Kernel Documentation

**Location:** `kernel/`  
**Stack:** C++20, CMake, SIMD (AVX-512/NEON), FFI (PyBind11)

This directory houses the bare-metal ingestion core of SimpleFeed++. By offloading XML/Atom parsing, date-time normalization, and string tokenization to a native C++20 layer, we bypass the Python Global Interpreter Lock (GIL) and achieve throughput levels unattainable in pure Python environments.

---

## 🎯 Engineering Philosophy: Throughput at the Edge

The `kernel` is not merely a library; it is a high-performance execution engine. Standard XML parsers in dynamic languages often suffer from excessive heap allocation and poor cache locality. Our kernel is designed for:

1.  **SIMD Parallelism:** We leverage Single Instruction, Multiple Data (SIMD) vectorization (AVX-512 on x86_64, NEON on ARM64) to process multiple characters in a single CPU cycle.
2.  **Zero-Copy Memory Management:** We map incoming feed streams directly into memory-resident buffers, parsing in-place to minimize allocation latency.
3.  **Deterministic Latency:** The parsing logic has no branching dependencies that cause pipeline stalls, ensuring consistent performance regardless of feed size.

[Image of SIMD architecture processing data]

---

## 🏗️ Technical Architecture

### 1. SIMD-Accelerated Tokenization
The parser treats the input stream as a vector of bytes. Using AVX-512 intrinsics, we can scan for XML tags and delimiters across 512-bit registers simultaneously, allowing us to tokenize gigabytes of feed data per second on standard infrastructure.

### 2. The Python-Native Bridge (FFI)
The bridge between Python and C++ is maintained via `pybind11`. This allows the Python Celery workers to call native C++ functions as if they were standard library methods, while passing raw memory pointers to avoid serialization overhead.

### 3. Memory Safety
While C++ is memory-unsafe by nature, the kernel utilizes RAII (Resource Acquisition Is Initialization) patterns and smart pointers. Strict compile-time checks (`-Wall -Wextra -Werror`) ensure no memory leaks occur during high-concurrency ingestion cycles.

---

## 📂 Directory Structure

```text
kernel/
├── include/                 # Public C++ headers
│   └── parser.hpp           # High-level interface definitions
├── src/                     # Core implementation
│   ├── simd_engine.cpp      # AVX-512/NEON intrinsic logic
│   ├── tokenization.cpp     # Optimized string extraction
│   └── parser.cpp           # FFI export and bridge logic
├── tests/                   # Benchmarks and unit tests
│   ├── benchmark_parse.cpp  # Throughput verification
│   └── test_edge_cases.py   # Python-side integration sanity checks
└── CMakeLists.txt           # Build configuration
```

---

## 🚀 Build & Compilation

The kernel requires a modern C++ compiler (GCC 11+, Clang 13+, or MSVC 19.30+).

```bash
# Build the native library
cd kernel
mkdir build && cd build
cmake ..
make -j$(nproc)
```

The resulting shared object (`.so` or `.dll`) is dynamically loaded by the Python worker at runtime.

---

## 🔒 Governance & Code Freeze

The `/kernel` directory is under a **Strict Code Freeze**. 

This component is the most critical point of failure in our infrastructure. Modifications to these files require:
1.  **Performance Regression Testing:** A 5% performance degradation in `benchmark_parse.cpp` will result in immediate PR rejection.
2.  **Memory Sanitizer Pass:** Any new code must pass `AddressSanitizer` (ASan) and `ThreadSanitizer` (TSan) testing during CI/CD.
3.  **Architecture Review:** Changes to the SIMD intrinsic implementations require architectural approval due to platform-specific hardware impacts.
