package com.docprocessing.gateway.config;

import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Mono;

@Configuration
public class RouteConfig {

    @Bean
    public KeyResolver userKeyResolver() {
        // Usa solo l'IP come identificatore
        return exchange -> {
            String ip = exchange.getRequest()
                                .getRemoteAddress()
                                .getAddress()
                                .getHostAddress();
            return Mono.just(ip != null ? ip : "unknown");
        };
    }
}