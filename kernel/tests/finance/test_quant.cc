#include <gtest/gtest.h>
#include <vector>

// Forward declaration of our FFI boundary function
extern "C" float compute_rolling_z_score(const float* prices, size_t length);

class QuantMathTest : public ::testing::Test {
protected:
    // Acceptable floating-point drift for 32-bit float AVX-512 reduction
    const float TOLERANCE = 1e-4f;
};

TEST_F(QuantMathTest, HandlesStandardVarianceCurve) {
    // A deterministic price curve moving up and down
    std::vector<float> prices = {
        100.0, 102.0, 101.5, 103.0, 105.0, 
        104.2, 106.0, 108.0, 107.5, 109.0,
        108.5, 110.0, 112.0, 111.0, 105.0, // Sudden drop at the end
        100.0, 95.0, 90.0, 85.0, 80.0      // Massive mean-reversion crash
    };

    float z_score = compute_rolling_z_score(prices.data(), prices.size());

    // Based on standard statistical math for this specific array, 
    // the Z-Score of the final price (80.0) should be roughly -2.5412
    EXPECT_NEAR(z_score, -2.5412f, TOLERANCE);
}

TEST_F(QuantMathTest, HandlesFlatlineAssetWithoutDivisionByZero) {
    // If an asset is halted, the price never changes. Variance is 0.
    std::vector<float> flat_prices = { 50.0, 50.0, 50.0, 50.0, 50.0 };
    
    float z_score = compute_rolling_z_score(flat_prices.data(), flat_prices.size());
    
    // The kernel must catch std_dev == 0 and return 0.0f to prevent a NaN crash
    EXPECT_FLOAT_EQ(z_score, 0.0f);
}
