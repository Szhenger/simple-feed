#include <gtest/gtest.h>
#include <vector>

extern "C" {
    int find_optimal_itinerary(
        const double* prices, const double* durations, const int* layovers,
        size_t count, double w_price, double w_duration, double layover_penalty
    );
}

class PlanOptimizerTest : public ::testing::Test {};

TEST_F(PlanOptimizerTest, SelectsAbsoluteCheapestWhenPriceWeightIsHigh) {
    std::vector<double> prices = {1200.0, 800.0, 1500.0};
    std::vector<double> durations = {600.0, 1400.0, 500.0}; // The cheap one is very long
    std::vector<int> layovers = {1, 3, 0};

    // Heavily weight price, ignore duration and layovers
    int best_idx = find_optimal_itinerary(
        prices.data(), durations.data(), layovers.data(),
        prices.size(), 1.0, 0.0, 0.0
    );

    EXPECT_EQ(best_idx, 1); // Should pick the $800 flight despite 3 layovers
}

TEST_F(PlanOptimizerTest, AvoidsLayoversWithHighPenalty) {
    std::vector<double> prices = {800.0, 850.0};
    std::vector<double> durations = {600.0, 550.0};
    std::vector<int> layovers = {2, 0}; // Flight 0 is $50 cheaper but has 2 layovers

    // Set a brutal layover penalty ($100 per layover)
    int best_idx = find_optimal_itinerary(
        prices.data(), durations.data(), layovers.data(),
        prices.size(), 1.0, 0.0, 100.0
    );

    EXPECT_EQ(best_idx, 1); // Flight 1 Score: 850. Flight 0 Score: 1000. Should pick Flight 1.
}

TEST_F(PlanOptimizerTest, HandlesEmptyArraysSafely) {
    int best_idx = find_optimal_itinerary(nullptr, nullptr, nullptr, 0, 1.0, 1.0, 1.0);
    EXPECT_EQ(best_idx, -1);
}
