#include <gtest/gtest.h>
#include <immintrin.h>

namespace kernel::simd {
    inline int find_first_index_tzcnt(uint64_t mask) {
        if (mask == 0) return -1;
        // Native hardware abstraction mapping to TZCNT via GCC/Clang builtins
        return __builtin_ctzll(mask);
    }
}

class AvxScannerTestSuite : public ::testing::Test {
protected:
    void SetUp() override {
        // Fallback safety check: verify the target CPU natively supports AVX-512 Foundation instructions
        #ifndef __AVX512F__
        GTEST_SKIP() << "Hardware target architecture does not support AVX-512 instructions. Skipping SIMD evaluation.";
        #endif
    }
};

TEST_F(AvxScannerTestSuite, VerifiesTrailingZeroCountBitmath) {
    // Binary: 0000...0100 (Token located precisely at index position 2)
    uint64_t mock_mask_at_index_two = 0x4ULL; 
    int result_index = kernel::simd::find_first_index_tzcnt(mock_mask_at_index_two);
    EXPECT_EQ(result_index, 2);

    // Test position zero element matching
    uint64_t mock_mask_at_index_zero = 0x1ULL;
    EXPECT_EQ(kernel::simd::find_first_index_tzcnt(mock_mask_at_index_zero), 0);

    // Handline empty vector scenarios gracefully
    uint64_t empty_mask = 0x0ULL;
    EXPECT_EQ(kernel::simd::find_first_index_tzcnt(empty_mask), -1);
}

TEST_F(AvxScannerTestSuite, IntegrationScanVerification) {
    // Construct a synthetic 64-byte page-aligned buffer block
    alignas(64) char block[64];
    std::memset(block, 'X', 64);
    block[42] = '<'; // Target token boundary tag injection

    // Execute standard AVX-512 compilation logic block
    __m512i target_vector = _mm512_set1_epi8('<');
    __m512i payload_vector = _mm512_loadu_si512(reinterpret_cast<const __m512i*>(block));
    
    uint64_t match_mask = _mm512_cmpeq_epi8_mask(target_vector, payload_vector);
    int match_index = kernel::simd::find_first_index_tzcnt(match_mask);

    // Verify hardware evaluated the exact position correctly without loop iteration loops
    EXPECT_EQ(match_index, 42);
}
