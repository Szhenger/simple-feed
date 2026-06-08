#pragma once

#include "core/types.hpp"
#include <string_view>
#include <vector>

namespace simplefeed::parser {

    class FeedParser {
    public:
        /**
         * @brief Parses a raw RSS 2.0 or Atom payload into structured entries.
         * @param payload The raw byte buffer received from Python.
         * @return A vector of memory-owned entries ready for gRPC serialization.
         */
        static std::vector<core::ParsedEntry> parse_stream(std::string_view payload);

    private:
        // Internal helper to extract the inner content between two tags using SIMD
        static std::string_view extract_tag_content(std::string_view payload, std::string_view tag_name, size_t start_pos);
    };

} // namespace simplefeed::parser
