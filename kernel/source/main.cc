#include <iostream>
#include <memory>
#include <string>
#include <grpcpp/grpcpp.h>
#include "server.hpp"

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    simplefeed::server::SyndicationServiceImpl service;

    grpc::ServerBuilder builder;
    
    // Disable compression for raw speed (our payloads are already traversing an internal network)
    builder.SetDefaultCompressionAlgorithm(GRPC_COMPRESS_NONE);
    
    // Listen on the given address without authentication (isolated within Docker mesh)
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    
    // Register the service
    builder.RegisterService(&service);
    
    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "🚀 SimpleFeed++ Kernel (C++20/AVX-512) listening on " << server_address << std::endl;
    
    // Block the main thread until shutdown is triggered
    server->Wait();
}

int main() {
    RunServer();
    return 0;
}
