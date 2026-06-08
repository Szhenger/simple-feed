#pragma once

#include <cstddef>
#include <string_view>

namespace simplefeed::simd {

    /**
     * @brief Hardware-accelerated scanner for XML tokenization.
     * Requires AVX-512F and AVX-512BW instruction sets.
     */
    class AvxScanner {
    public:
        /**
         * @brief Scans a 64-byte aligned chunk for a specific character.
         * @param buffer Pointer to the start of the memory block.
         * @param length Total length of the buffer.
         * @param start_idx The index to begin scanning from.
         * @param target The character to find (e.g., '<' or '>').
         * @return The absolute index of the character, or std::string_view::npos if not found.
         */
        static size_t find_next_char(const char* buffer, size_t length, size_t start_idx, char target);
    };

} // namespace simplefeed::simd
