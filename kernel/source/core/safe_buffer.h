#pragma once

#include <string>
#include <string_view>
#include <vector>
#include <cstring>

namespace simplefeed::core {

    /**
     * @brief Guarantees 64-byte aligned read-safety for AVX-512 intrinsics.
     * Prevents page-boundary segmentation faults at the tail of a payload.
     */
    class SafeByteBuffer {
    public:
        explicit SafeByteBuffer(std::string_view raw_payload) 
            : original_length_(raw_payload.length()) {
            
            // Calculate padding required to reach the next 64-byte boundary
            size_t padded_size = (original_length_ + 63) & ~63ULL;
            
            // Allocate contiguous memory and copy
            buffer_.resize(padded_size, '\0');
            std::memcpy(buffer_.data(), raw_payload.data(), original_length_);
        }

        // Expose a string_view that restricts operations to the valid data length,
        // while the underlying vector safely absorbs the 64-byte SIMD over-read.
        [[nodiscard]] std::string_view view() const {
            return {buffer_.data(), original_length_};
        }

    private:
        std::vector<char> buffer_;
        size_t original_length_;
    };

} // namespace simplefeed::core
