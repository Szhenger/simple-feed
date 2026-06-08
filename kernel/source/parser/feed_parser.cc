#include "feed_parser.h"
#include "simd/scanner.h"

namespace simplefeed::parser {

std::vector<core::ParsedEntry> FeedParser::parse_stream(std::string_view payload) {
    std::vector<core::ParsedEntry> entries;
    
    // Pre-allocate to prevent vector reallocation overhead
    entries.reserve(50); 
    
    const char* buffer = payload.data();
    size_t length = payload.length();
    size_t cursor = 0;

    // A hyper-optimized scan loop. We are looking for the <item> (RSS) or <entry> (Atom) tags.
    // For simplicity in this kernel abstraction, we will target standard RSS <item> arrays.
    std::string_view item_open = "<item>";
    std::string_view item_close = "</item>";

    while (cursor < length) {
        // Use the AVX-512 scanner to jump directly to the next '<' bracket
        size_t tag_start = simd::AvxScanner::find_next_char(buffer, length, cursor, '<');
        
        if (tag_start == std::string_view::npos) break;

        // Verify if this is an <item> tag
        if (tag_start + item_open.length() <= length && 
            payload.substr(tag_start, item_open.length()) == item_open) {
            
            size_t item_end = payload.find(item_close, tag_start);
            if (item_end == std::string_view::npos) break;

            // We have isolated an entire <item> block.
            std::string_view item_block = payload.substr(tag_start, item_end - tag_start);

            core::ParsedEntry entry;
            
            // Extract core fields. 
            // Note: In a production kernel, extract_tag_content would also use the AVX scanner.
            entry.title = extract_tag_content(item_block, "title", 0);
            entry.url = extract_tag_content(item_block, "link", 0);
            entry.guid = extract_tag_content(item_block, "guid", 0);
            entry.content = extract_tag_content(item_block, "description", 0);
            entry.published_at = extract_tag_content(item_block, "pubDate", 0);

            // Fallback for GUID if missing (common in malformed RSS)
            if (entry.guid.empty()) {
                entry.guid = entry.url; 
            }

            entries.push_back(std::move(entry));
            cursor = item_end + item_close.length();
        } else {
            cursor = tag_start + 1;
        }
    }

    return entries;
}

std::string_view FeedParser::extract_tag_content(std::string_view payload, std::string_view tag_name, size_t start_pos) {
    // Standard string operations for inner-tag extraction.
    // For ultimate speed, these are replaced with AVX scanners in deeper optimizations.
    std::string open_tag = "<" + std::string(tag_name) + ">";
    std::string close_tag = "</" + std::string(tag_name) + ">";

    size_t start = payload.find(open_tag, start_pos);
    if (start == std::string_view::npos) {
        // Try to handle attributes (e.g., <link href="...">)
        open_tag = "<" + std::string(tag_name) + " ";
        start = payload.find(open_tag, start_pos);
        if (start == std::string_view::npos) return "";
        
        start = payload.find(">", start);
        if (start == std::string_view::npos) return "";
    } else {
        start += open_tag.length();
    }

    size_t end = payload.find(close_tag, start);
    if (end == std::string_view::npos) return "";

    return payload.substr(start, end - start);
}

} // namespace simplefeed::parser
