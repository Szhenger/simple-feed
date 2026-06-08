#include "server.hpp"

namespace simplefeed::server {

grpc::Status SyndicationServiceImpl::ParseStream(
    grpc::ServerContext* context, 
    const kernel::RawStreamRequest* request, 
    kernel::ParsedStreamResponse* response) {
    
    if (request->payload().empty()) {
        return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT, "Empty payload received.");
    }

    try {
        // 1. Wrap the raw gRPC bytes in our AVX-512 safe padding abstraction
        core::SafeByteBuffer safe_payload(request->payload());

        // 2. Execute the C++20 parsing kernel
        auto parsed_entries = parser::FeedParser::parse_stream(safe_payload.view());

        // 3. Serialize back into the protobuf response
        for (const auto& entry : parsed_entries) {
            auto* new_entry = response->add_entries();
            new_entry->set_guid(entry.guid);
            new_entry->set_title(entry.title);
            new_entry->set_url(entry.url);
            new_entry->set_content(entry.content);
            new_entry->set_published_at(entry.published_at);
        }

        return grpc::Status::OK;

    } catch (const std::exception& e) {
        return grpc::Status(grpc::StatusCode::INTERNAL, std::string("Kernel panic: ") + e.what());
    }
}

} // namespace simplefeed::server
