#include <immintrin.h>
#include <cmath>
#include <vector>
#include <span>

namespace kernel::quant {

    extern "C" {
        // Exposed to Python via FFI/ctypes
        float compute_rolling_z_score(const float* prices, size_t length) {
            if (length == 0) return 0.0f;

            float sum = 0.0f;
            // Standard scalar loop for the mean (can also be vectorized, but 
            // keeping it simple for the initial summation)
            for (size_t i = 0; i < length; ++i) {
                sum += prices[i];
            }
            float mean = sum / length;

            // ---------------------------------------------------------
            // AVX-512 VECTORIZED VARIANCE CALCULATION
            // ---------------------------------------------------------
            __m512 v_mean = _mm512_set1_ps(mean);       // Broadcast mean to 16 lanes
            __m512 v_variance_sum = _mm512_setzero_ps(); // Accumulator initialized to 0

            size_t i = 0;
            // Process 16 floating-point numbers per cycle
            for (; i + 15 < length; i += 16) {
                // Load 16 prices into the 512-bit register
                __m512 v_prices = _mm512_loadu_ps(&prices[i]);
                
                // Subtract mean: (x - mu)
                __m512 v_diff = _mm512_sub_ps(v_prices, v_mean);
                
                // Square the differences: (x - mu)^2
                __m512 v_sq_diff = _mm512_mul_ps(v_diff, v_diff);
                
                // Accumulate into the sum
                v_variance_sum = _mm512_add_ps(v_variance_sum, v_sq_diff);
            }

            // Horizontal add to collapse the 16-lane vector accumulator into a single scalar float
            float variance_sum = _mm512_reduce_add_ps(v_variance_sum);

            // Scalar tail processing for any remaining elements not divisible by 16
            for (; i < length; ++i) {
                float diff = prices[i] - mean;
                variance_sum += (diff * diff);
            }

            float std_dev = std::sqrt(variance_sum / length);
            
            // Prevent division by zero if the asset price is completely flat
            if (std_dev == 0.0f) return 0.0f;

            // Z-Score of the most recent price (the last element in the array)
            float current_price = prices[length - 1];
            return (current_price - mean) / std_dev;
        }
    }
}
