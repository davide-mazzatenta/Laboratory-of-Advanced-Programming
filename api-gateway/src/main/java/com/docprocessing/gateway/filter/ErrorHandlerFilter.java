package com.docprocessing.gateway.filter;

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class ErrorHandlerFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        return chain.filter(exchange)
                .onErrorResume(throwable -> {
                    // Handle specific exceptions
                    if (throwable instanceof ResponseStatusException) {
                        exchange.getResponse().setStatusCode(((ResponseStatusException) throwable).getStatus());
                    } else {
                        // Default to internal server error
                        exchange.getResponse().setStatusCode(HttpStatus.INTERNAL_SERVER_ERROR);
                    }
                    
                    // Complete the response
                    return exchange.getResponse().setComplete();
                });
    }

    @Override
    public int getOrder() {
        // Make sure this filter runs last
        return Ordered.LOWEST_PRECEDENCE;
    }
}
