#include <cstddef>
#include <limits>

extern "C" {
    /**
     * @brief Computes the lowest friction score across a massive array of flight parameters.
     * @param prices Array of flight prices (USD).
     * @param durations Array of flight durations (Minutes).
     * @param layovers Array of layover counts.
     * @param count The number of elements in the arrays.
     * @param w_price User weight for price sensitivity.
     * @param w_duration User weight for duration sensitivity.
     * @param layover_penalty Flat numeric penalty per layover.
     * @return The integer index of the optimal flight.
     */
    int find_optimal_itinerary(
        const double* __restrict prices,
        const double* __restrict durations,
        const int* __restrict layovers,
        size_t count,
        double w_price,
        double w_duration,
        double layover_penalty
    ) {
        if (count == 0) return -1;

        int best_index = 0;
        double lowest_score = std::numeric_limits<double>::max();

        // The __restrict keyword and contiguous memory layout allow 
        // modern compilers (GCC/Clang) to unroll this into AVX-512 instructions.
        #pragma GCC ivdep
        for (size_t i = 0; i < count; ++i) {
            double score = (w_price * prices[i]) + 
                           (w_duration * durations[i]) + 
                           (layovers[i] * layover_penalty);

            if (score < lowest_score) {
                lowest_score = score;
                best_index = i;
            }
        }

        return best_index;
    }
}
