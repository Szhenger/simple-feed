#include <gtest/gtest.h>
#include <string_view>

// Minimal mock inline representation of kernel safety boundaries
namespace kernel::core {
    struct SafeByteBuffer {
        size_t original_length;
        size_t padded_length;
        std::unique_ptr<char[]> data;

        SafeByteBuffer(std::string_view payload) {
            original_length = payload.length();
            // Upward mathematical ceiling bitmask allocation: (length + 63) & ~63
            padded_length = (original_length + 63) & ~63ULL;
            data = std::make_unique<char[]>(padded_length);
            
            // Memcpy the live string payload and initialize the tail to null bytes
            std::memcpy(data.get(), payload.data(), original_length);
            std::memset(data.get() + original_length, '\0', padded_length - original_length);
        }
    };
}

class BufferSafetyTestSuite : public ::testing::Test {};

TEST_F(BufferSafetyTestSuite, VerifiesStrictSixtyFourByteBoundaryPaddingMath) {
    // 1. Create a payload that is 5 bytes long.
    std::string_view micro_payload = "START";
    kernel::core::SafeByteBuffer safe_buf(micro_payload);

    // 2. The padded size must round perfectly up to 64 bytes.
    EXPECT_EQ(safe_buf.padded_length, 64);
    EXPECT_EQ(safe_buf.data[5], '\0'); // First trailing bit must be null
    EXPECT_EQ(safe_buf.data[63], '\0'); // Absolute end of block must be safe
}

TEST_F(BufferSafetyTestSuite, VerifiesPerfectMultiBlockAlignment) {
    // 65-byte string spills precisely 1 byte into the second vector window.
    std::string long_payload(65, 'A');
    kernel::core::SafeByteBuffer safe_buf(long_payload);

    // Must calculate out to exactly 128 bytes of safe allocation area
    EXPECT_EQ(safe_buf.padded_length, 128);
    EXPECT_EQ(safe_buf.data[64], 'A');
    EXPECT_EQ(safe_buf.data[65], '\0');
}
