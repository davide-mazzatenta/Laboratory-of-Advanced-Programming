package com.docprocessing.gateway.filter;

import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.UUID;

@Component
@Slf4j
public class LoggingFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Generate request ID for tracking
        String requestId = UUID.randomUUID().toString();
        
        // Add request ID to response header
        exchange.getResponse().getHeaders().add("X-Request-ID", requestId);
        
        // Get request details
        String path = exchange.getRequest().getPath().value();
        String method = exchange.getRequest().getMethod().name();
        String remoteAddress = exchange.getRequest().getRemoteAddress().getAddress().getHostAddress();
        
        // Log incoming request
        log.info("Request: [{}] {} {} from {}", requestId, method, path, remoteAddress);
        
        // Record start time
        long startTime = System.currentTimeMillis();
        
        // Continue the filter chain and log the response
        return chain.filter(exchange)
                .then(Mono.fromRunnable(() -> {
                    // Calculate request duration
                    long duration = System.currentTimeMillis() - startTime;
                    
                    // Log response details
                    int statusCode = exchange.getResponse().getStatusCode() != null ? 
                            exchange.getResponse().getStatusCode().value() : 0;
                            
                    log.info("Response: [{}] {} {} completed with status {} in {} ms", 
                            requestId, method, path, statusCode, duration);
                }));
    }

    @Override
    public int getOrder() {
        // Run this filter first
        return -1;
    }
}
