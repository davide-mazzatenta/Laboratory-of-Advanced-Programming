package com.docprocessing.gateway.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

@Configuration
public class GatewayConfig {

    @Value("${services.document-service.url:http://localhost:8000}")
    private String documentServiceUrl;
    
    @Value("${services.extraction-agent.url:http://localhost:8001}")
    private String extractionAgentUrl;

    @Value("${services.search-agent.url:http://localhost:8002}")
    private String searchAgentUrl;

    @Value("${services.generation-agent.url:http://localhost:8003}")
    private String generationAgentUrl;

    // Orchestration service URL
    @Value("${SERVICES_ORCHESTRATION_SERVICE_URL:http://orchestration-agent:8005}")
    private String orchestrationServiceUrl;
    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration corsConfiguration = new CorsConfiguration();
        corsConfiguration.setAllowCredentials(true);
        
        // Use specific origins only
        corsConfiguration.addAllowedOrigin("http://localhost:3000"); // React dev server
        corsConfiguration.addAllowedOrigin("http://frontend:80");    // Docker container
        
        // Allow all headers and methods
        corsConfiguration.addAllowedHeader("*");
        corsConfiguration.addAllowedMethod("*");
        
        // Set max age for preflight requests
        corsConfiguration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfiguration);
        
        return new CorsWebFilter(source);
    }

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()

                // DOCUMENT SERVICE ROUTES - EXISTING

                // Get user projects
                .route("user_projects", r -> r
                        .path("/api/v1/projects/{user_id}")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                .route("document_upload", r -> r
                        .path("/api/v1/documents/upload")
                        .and()
                        .method(HttpMethod.POST)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                // Get document PDF binary
                .route("document_retrieve", r -> r
                        .path("/api/v1/documents/{user_id}/{project_id}/{doc_id}")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                // Get document PDF binary with /pdf suffix
                .route("document_retrieve_pdf", r -> r
                        .path("/api/v1/documents/{user_id}/{project_id}/{doc_id}/pdf")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                // Get document text content
                .route("document_text", r -> r
                        .path("/api/v1/documents/{user_id}/{project_id}/{doc_id}/text")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                // List documents in a project
                .route("documents_list", r -> r
                        .path("/api/v1/documents/{user_id}/{project_id}")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                .route("document_query", r -> r
                        .path("/api/v1/documents/query")
                        .and()
                        .method(HttpMethod.POST)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(documentServiceUrl))

                // EXTRACTION AGENT ROUTES - EXISTING

                // Main extraction endpoint
                .route("extraction_agent", r -> r
                        .path("/api/v1/agents/extract")
                        .and()
                        .method(HttpMethod.POST)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(extractionAgentUrl))

                // Orchestrator compatibility endpoint
                .route("agent_process", r -> r
                        .path("/api/v1/agents/process")
                        .and()
                        .method(HttpMethod.POST)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(extractionAgentUrl))

                // Extraction agent health check
                .route("extraction_agent_health", r -> r
                        .path("/api/v1/agents/health")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f
                                .setRequestHeader("X-Gateway-Source", "api-gateway")
                                .rewritePath("/api/v1/agents/health", "/health"))
                        .uri(extractionAgentUrl))

                // SEARCH AGENT ROUTES - EXISTING

                // Main search endpoint
                .route("search_agent", r -> r
                        .path("/api/v1/search")
                        .and()
                        .method(HttpMethod.POST)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(searchAgentUrl))

                // Search agent status endpoint
                .route("search_agent_status", r -> r
                        .path("/api/v1/search/status")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(searchAgentUrl))

                // Search agent health check
                .route("search_agent_health", r -> r
                        .path("/api/v1/search/health")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f
                                .setRequestHeader("X-Gateway-Source", "api-gateway")
                                .rewritePath("/api/v1/search/health", "/health"))
                        .uri(searchAgentUrl))

                // ORCHESTRATION AGENT ROUTES - NEW

                // Main orchestration endpoint - Direct to orchestration service
                .route("orchestration_agent", r -> r
                        .path("/api/v1/agents/orchestrate")
                        .and()
                        .method(HttpMethod.POST)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(orchestrationServiceUrl))

                // Orchestration health check
                .route("orchestration_agent_health", r -> r
                        .path("/api/v1/agents/orchestrate/health")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f
                                .setRequestHeader("X-Gateway-Source", "api-gateway")
                                .rewritePath("/api/v1/agents/orchestrate/health", "/health"))
                        .uri(orchestrationServiceUrl))

                // LEGACY ORCHESTRATION ROUTE - Keep for backward compatibility
                .route("orchestration-service-route", r -> r
                        .path("/api/v1/agents/route")
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri(orchestrationServiceUrl))

                // HEALTH CHECKS - EXISTING
                .route("document_service_health", r -> r
                        .path("/")
                        .and()
                        .method(HttpMethod.GET)
                        .uri(documentServiceUrl))

                .route("document_service_health_explicit", r -> r
                        .path("/health")
                        .and()
                        .method(HttpMethod.GET)
                        .uri(documentServiceUrl))

                // GATEWAY HEALTH - EXISTING
                .route("health_check", r -> r
                        .path("/api/health")
                        .and()
                        .method(HttpMethod.GET)
                        .filters(f -> f.setRequestHeader("X-Gateway-Source", "api-gateway"))
                        .uri("forward:/actuator/health"))

                .route("gateway_info", r -> r
                        .path("/api/v1/gateway/info")
                        .and()
                        .method(HttpMethod.GET)
                        .uri("forward:/gateway/info"))

                .build();
    }
}