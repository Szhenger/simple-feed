#include <gtest/gtest.h>
#include <string>

extern "C" {
    const char* extract_dense_chunks(const char* text_stream, size_t length, int threshold);
    void free_extracted_text(const char* ptr);
}

class EduScannerTest : public ::testing::Test {};

TEST_F(EduScannerTest, DropsFluffAndExtractsTechnicalParagraphs) {
    std::string document = 
        "Welcome to the course. Today we will talk about grades and the syllabus. "
        "Please buy the textbook by Friday.\n\n" // Low signal (0 hits)
        
        "To achieve horizontal scalability, we must eliminate the bottleneck in our "
        "asynchronous pipeline. We will use a lock-free distributed consensus model.\n\n" // High signal (5 hits)
        
        "Have a great weekend and remember to rest!"; // Low signal (0 hits)

    // Require at least 3 keyword hits to survive the filter
    const char* result_ptr = extract_dense_chunks(document.c_str(), document.length(), 3);
    
    ASSERT_NE(result_ptr, nullptr);
    
    std::string result_str(result_ptr);
    
    // Verify the fluff was dropped
    EXPECT_EQ(result_str.find("grades and the syllabus"), std::string::npos);
    EXPECT_EQ(result_str.find("Have a great weekend"), std::string::npos);
    
    // Verify the core engineering paragraph was retained
    EXPECT_NE(result_str.find("lock-free distributed consensus"), std::string::npos);

    // Prevent memory leaks in the test suite
    free_extracted_text(result_ptr);
}

TEST_F(EduScannerTest, ReturnsNullForCompletelyUselessDocuments) {
    std::string marketing_fluff = "We are synergistic and proactive with our cloud journey.";
    
    const char* result_ptr = extract_dense_chunks(marketing_fluff.c_str(), marketing_fluff.length(), 2);
    
    // Kernel must cleanly return a null pointer, signaling Python to abort the pipeline
    EXPECT_EQ(result_ptr, nullptr);
}
