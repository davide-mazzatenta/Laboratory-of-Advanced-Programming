package com.lexygraph.wrapper;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import org.slf4j.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.*;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.reactive.function.client.*;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;
import java.util.*;
import java.util.function.Supplier;

// CORS (Servlet stack)
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

@SpringBootApplication
public class OrchestrationWrapperApplication {

  public static void main(String[] args) {
    System.setProperty("server.port", System.getenv().getOrDefault("WRAPPER_PORT", "8010"));
    SpringApplication.run(OrchestrationWrapperApplication.class, args);
  }

  // WebClient con timeout
  @Bean
  public WebClient webClient(@Value("${REQUEST_TIMEOUT_SECONDS:60}") long timeoutSec) {
    HttpClient httpClient = HttpClient.create().responseTimeout(Duration.ofSeconds(timeoutSec));
    return WebClient.builder().clientConnector(new ReactorClientHttpConnector(httpClient)).build();
  }

  // CORS (Servlet)
  @Bean
  public CorsFilter corsFilter(@Value("${ALLOWED_ORIGINS:*}") String allowedOrigins) {
    CorsConfiguration cfg = new CorsConfiguration();
    cfg.setAllowCredentials(true);
    if ("*".equals(allowedOrigins.trim())) {
      cfg.addAllowedOriginPattern("*");
    } else {
      for (String o : allowedOrigins.split(",")) {
        String v = o.trim();
        if (!v.isEmpty()) cfg.addAllowedOrigin(v);
      }
    }
    cfg.addAllowedHeader("*");
    cfg.addAllowedMethod("*");

    UrlBasedCorsConfigurationSource src = new UrlBasedCorsConfigurationSource();
    src.registerCorsConfiguration("/**", cfg);
    return new CorsFilter(src);
  }

  // Service per downstream + retry
  @org.springframework.stereotype.Service
  public static class DownstreamService {
    private static final Logger log = LoggerFactory.getLogger(DownstreamService.class);
    private final WebClient webClient;
    private final int retryAttempts;

    public DownstreamService(WebClient webClient, @Value("${RETRY_ATTEMPTS:1}") int retryAttempts) {
      this.webClient = webClient;
      this.retryAttempts = Math.max(1, retryAttempts);
    }

    public record HttpResult(int status, String body) {}

    public HttpResult postJson(String url, Map<String, Object> body, String executionId) {
      Supplier<HttpResult> call = () -> webClient.post()
          .uri(url)
          .headers(h -> {
            if (executionId != null && !executionId.isBlank()) h.add("X-Execution-Id", executionId);
          })
          .contentType(MediaType.APPLICATION_JSON)
          .bodyValue(body == null ? Map.of() : body)
          .exchangeToMono(resp -> resp.bodyToMono(String.class).defaultIfEmpty("")
              .map(b -> new HttpResult(resp.statusCode().value(), b)))
          .block();

      Exception last = null;
      for (int i = 1; i <= retryAttempts; i++) {
        try { return call.get(); }
        catch (Exception e) { last = e; log.warn("retry {}/{} failed: {}", i, retryAttempts, e.toString()); }
      }
      throw new RuntimeException(last);
    }
  }

  // DTO
  public record SearchIn(@NotBlank String query, String agent_id) {}
  public record SearchOut(String results, List<Map<String,Object>> sources, Map<String,Object> provider_summary) {}

  public static class ProcessIn {
    @NotBlank
    @Pattern(regexp = "^(extract(or)?ion-agent|generation-agent)$")
    private String agentId;
    private String prompt = "";
    private List<String> documentIds = new ArrayList<>();
    private String executionId;
    private Boolean fullDoc;

    public String getAgentId() { return agentId; }
    public void setAgentId(String agentId) { this.agentId = agentId; }
    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }
    public List<String> getDocumentIds() { return documentIds; }
    public void setDocumentIds(List<String> documentIds) { this.documentIds = documentIds; }
    public String getExecutionId() { return executionId; }
    public void setExecutionId(String executionId) { this.executionId = executionId; }
    public Boolean getFullDoc() { return fullDoc; }
    public void setFullDoc(Boolean fullDoc) { this.fullDoc = fullDoc; }
  }

  @JsonInclude(JsonInclude.Include.NON_NULL)
  public static class AgentOut {
    private String agentId;
    private String prompt;
    private List<String> documentIds = new ArrayList<>();
    private String executionId;
    private Object response;
    private String completedAt;
    private Object fullResult;

    public String getAgentId() { return agentId; }
    public void setAgentId(String agentId) { this.agentId = agentId; }
    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }
    public List<String> getDocumentIds() { return documentIds; }
    public void setDocumentIds(List<String> documentIds) { this.documentIds = documentIds; }
    public String getExecutionId() { return executionId; }
    public void setExecutionId(String executionId) { this.executionId = executionId; }
    public Object getResponse() { return response; }
    public void setResponse(Object response) { this.response = response; }
    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
    public Object getFullResult() { return fullResult; }
    public void setFullResult(Object fullResult) { this.fullResult = fullResult; }
  }

  @JsonIgnoreProperties(ignoreUnknown = true)
  public static class OrchestrateIn {
    private List<String> document_ids;
    private List<String> documentIds;
    @NotBlank private String prompt;
    private String agent_id = "orchestration-agent";
    private String execution_id;

    public List<String> getDocument_ids() { return document_ids; }
    public void setDocument_ids(List<String> document_ids) { this.document_ids = document_ids; }
    public List<String> getDocumentIds() { return documentIds; }
    public void setDocumentIds(List<String> documentIds) { this.documentIds = documentIds; }
    public String getPrompt() { return prompt; }
    public void setPrompt(String prompt) { this.prompt = prompt; }
    public String getAgent_id() { return agent_id; }
    public void setAgent_id(String agent_id) { this.agent_id = agent_id; }
    public String getExecution_id() { return execution_id; }
    public void setExecution_id(String execution_id) { this.execution_id = execution_id; }
  }

  public static class OrchestrateOut {
    public boolean success;
    public String agent_id;
    public String execution_id;
    public String prompt;
    public List<String> document_ids;
    public List<Map<String,Object>> actions_taken;
    public String final_response;
    public String message;
  }

  // Controller
  @RestController
  @Validated
  public static class WrapperController {
    private static final Logger log = LoggerFactory.getLogger(WrapperController.class);
    private final DownstreamService ds;
    private final ObjectMapper mapper = new ObjectMapper()
        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    @Value("${SEARCH_AGENT_URL:http://search-agent:8002}")        private String SEARCH_AGENT_URL;
    @Value("${EXTRACTION_AGENT_URL:http://extraction-agent:8001}")private String EXTRACTION_AGENT_URL;
    @Value("${GENERATION_AGENT_URL:http://generation-agent:8003}")private String GENERATION_AGENT_URL;
    @Value("${ORCHESTRATION_AGENT_URL:http://orchestration-agent:8005}") private String ORCHESTRATION_AGENT_URL;
    @Value("${REQUEST_TIMEOUT_SECONDS:60}") private double REQUEST_TIMEOUT_SECONDS;
    @Value("${RETRY_ATTEMPTS:1}")          private int RETRY_ATTEMPTS;

    public WrapperController(DownstreamService ds) { this.ds = ds; }

    @GetMapping({"/", "/health"})
    public Map<String,Object> health() {
      return Map.of(
          "status", "healthy",
          "service", "orchestration-wrapper",
          "downstreams", Map.of(
              "search", SEARCH_AGENT_URL,
              "extraction", EXTRACTION_AGENT_URL,
              "generation", GENERATION_AGENT_URL,
              "orchestration", ORCHESTRATION_AGENT_URL
          ),
          "timeouts", REQUEST_TIMEOUT_SECONDS,
          "retries", RETRY_ATTEMPTS
      );
    }

    @PostMapping("/api/v1/agents/search")
    public SearchOut search(@Valid @RequestBody SearchIn in,
                            @RequestHeader(value="X-Execution-Id", required=false) String xExecId) {
      String agentId = (in.agent_id() == null || in.agent_id().isBlank()) ? "search-agent" : in.agent_id();

      Map<String,Object> newBody = Map.of("query", in.query(), "agent_id", agentId);
      DownstreamService.HttpResult r1 =
          ds.postJson(SEARCH_AGENT_URL + "/api/v1/agents/search", newBody, xExecId);

      DownstreamService.HttpResult resp = r1;
      if (r1.status == 404) {
        Map<String,Object> oldBody = Map.of("query", in.query(), "max_results", 5, "include_sources", true);
        resp = ds.postJson(SEARCH_AGENT_URL + "/api/v1/search", oldBody, xExecId);
      }
      if (resp.status != 200) throw status(resp.status, resp.body);

      try {
        Map<String,Object> data = mapper.readValue(resp.body, new TypeReference<>() {});
        String results = (String) (data.getOrDefault("results", data.getOrDefault("summary", "No search results")));
        @SuppressWarnings("unchecked") List<Map<String,Object>> sources = (List<Map<String, Object>>) data.get("sources");
        @SuppressWarnings("unchecked") List<Object> providers = (List<Object>) data.get("search_providers_used");
        Map<String,Object> providerSummary = (providers != null) ? Map.of("providers", providers) : null;
        return new SearchOut(results, sources, providerSummary);
      } catch (Exception e) {
        throw status(HttpStatus.BAD_GATEWAY, "Invalid JSON from search-agent");
      }
    }

    @PostMapping("/api/v1/agents/process")
    public AgentOut process(@Valid @RequestBody ProcessIn in,
                            @RequestHeader(value="X-Execution-Id", required=false) String xExecId) {
      String agentNorm = in.getAgentId();
      String baseUrl;
      if ("extractor-agent".equals(agentNorm) || "extraction-agent".equals(agentNorm)) {
        agentNorm = "extraction-agent";
        baseUrl = EXTRACTION_AGENT_URL;
      } else if ("generation-agent".equals(agentNorm)) {
        baseUrl = GENERATION_AGENT_URL;
      } else {
        throw status(HttpStatus.BAD_REQUEST, "Unsupported agentId '" + in.getAgentId() + "'");
      }

      Map<String,Object> body = new HashMap<>();
      body.put("agentId", agentNorm);
      body.put("prompt", in.getPrompt());
      body.put("documentIds", in.getDocumentIds() == null ? List.of() : in.getDocumentIds());
      body.put("executionId", in.getExecutionId());
      if ("generation-agent".equals(agentNorm)) {
        body.put("fullDoc", Boolean.TRUE.equals(in.getFullDoc()));
      }

      String corr = in.getExecutionId() != null ? in.getExecutionId() : xExecId;
      DownstreamService.HttpResult resp =
          ds.postJson(baseUrl + "/api/v1/agents/process", body, corr);

      if (resp.status != 200) throw status(resp.status, resp.body);

      try {
        JsonNode node = mapper.readTree(resp.body);
        AgentOut out = new AgentOut();

        if (node.has("agentId") && node.has("response")) {
          out.setAgentId(node.path("agentId").asText(null));
          out.setPrompt(node.path("prompt").isMissingNode() ? null : node.path("prompt").asText(null));
          if (node.has("documentIds") && node.get("documentIds").isArray()) {
            out.setDocumentIds(mapper.convertValue(node.get("documentIds"), new TypeReference<List<String>>(){}));
          }
          out.setExecutionId(node.path("executionId").isMissingNode() ? null : node.path("executionId").asText(null));
          out.setResponse(mapper.convertValue(node.get("response"), Object.class));
          out.setCompletedAt(node.path("completedAt").isMissingNode() ? null : node.path("completedAt").asText(null));
          if (node.has("fullResult")) {
            out.setFullResult(mapper.convertValue(node.get("fullResult"), Object.class));
          }
          return out;
        }

        out.setAgentId(agentNorm);
        out.setPrompt(in.getPrompt());
        out.setDocumentIds(in.getDocumentIds());
        out.setExecutionId(in.getExecutionId());
        out.setResponse(mapper.convertValue(node, Object.class));
        return out;

      } catch (Exception e) {
        throw status(HttpStatus.BAD_GATEWAY, "Invalid JSON from downstream");
      }
    }

    @PostMapping("/api/v1/agents/orchestrate")
    public OrchestrateOut orchestrate(@Valid @RequestBody OrchestrateIn in,
                                      @RequestHeader(value="X-Execution-Id", required=false) String xExecId) {

      List<String> docIds = (in.getDocument_ids() != null) ? in.getDocument_ids() : in.getDocumentIds();
      if (docIds == null || docIds.isEmpty() || in.getPrompt() == null || in.getPrompt().isBlank()) {
        throw status(HttpStatus.BAD_REQUEST, "Both 'prompt' and 'document_ids' (or 'documentIds') are required");
      }

      Map<String,Object> body = new HashMap<>();
      body.put("document_ids", docIds);
      body.put("prompt", in.getPrompt());
      body.put("agent_id", "orchestration-agent");
      body.put("execution_id", in.getExecution_id());

      String corr = in.getExecution_id() != null ? in.getExecution_id() : xExecId;
      DownstreamService.HttpResult resp =
          ds.postJson(ORCHESTRATION_AGENT_URL + "/api/v1/agents/orchestrate", body, corr);

      if (resp.status != 200) throw status(resp.status, resp.body);

      try {
        return new ObjectMapper().readValue(resp.body, OrchestrateOut.class);
      } catch (Exception e) {
        throw status(HttpStatus.BAD_GATEWAY, "Invalid JSON from orchestration-agent");
      }
    }

    @PostMapping("/api/v1/orchestrate")
    public OrchestrateOut orchestrateAlias(@Valid @RequestBody OrchestrateIn in,
                                           @RequestHeader(value="X-Execution-Id", required=false) String xExecId) {
      return orchestrate(in, xExecId);
    }

    private ResponseStatusException status(int code, String body) {
      return new ResponseStatusException(HttpStatus.valueOf(code), body);
    }
    private ResponseStatusException status(HttpStatus st, String msg) {
      return new ResponseStatusException(st, msg);
    }
  }
}
