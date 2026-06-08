#include "scanner.h"
#include <immintrin.h>

namespace simplefeed::simd {

size_t AvxScanner::find_next_char(const char* buffer, size_t length, size_t start_idx, char target) {
    if (start_idx >= length) return std::string_view::npos;

    size_t i = start_idx;
    
    // Broadcast the target character into a 512-bit register (64 copies of the 8-bit char)
    __m512i target_vec = _mm512_set1_epi8(target);

    // Process 64 bytes at a time
    while (i + 64 <= length) {
        // Load 64 bytes from the buffer into the register (unaligned load is safe here)
        __m512i chunk = _mm512_loadu_si512(reinterpret_cast<const __m512i*>(buffer + i));
        
        // Compare chunk with target_vec. Returns a 64-bit bitmask where 1 means equality.
        __mmask64 mask = _mm512_cmpeq_epi8_mask(chunk, target_vec);
        
        if (mask != 0) {
            // Find the position of the lowest set bit (tzcnt), which gives the index of the match
            return i + __builtin_ctzll(mask);
        }
        
        i += 64;
    }

    // Scalar fallback for the tail elements (less than 64 bytes remaining)
    for (; i < length; ++i) {
        if (buffer[i] == target) {
            return i;
        }
    }

    return std::string_view::npos;
}

} // namespace simplefeed::simd
