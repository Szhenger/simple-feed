#pragma once

#include <string>
#include <string_view>
#include <vector>

namespace simplefeed::core {

    /**
     * @brief The native representation of the feed.proto FeedEntry.
     * We use std::string here because these values will outlive the 
     * raw gRPC byte buffer and must own their memory before serialization.
     */
    struct ParsedEntry {
        std::string guid;
        std::string title;
        std::string url;
        std::string content;
        std::string published_at;
    };

    /**
     * @brief Zero-copy representation of an XML node used during traversal.
     */
    struct XmlNodeView {
        std::string_view tag_name;
        std::string_view inner_content;
    };

} // namespace simplefeed::core
