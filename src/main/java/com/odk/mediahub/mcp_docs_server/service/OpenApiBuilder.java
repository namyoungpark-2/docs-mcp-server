package com.odk.mediahub.mcp_docs_server.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.*;
import com.odk.mediahub.mcp_docs_server.dto.ApiDocsRequestDto;

import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Component
public class OpenApiBuilder {
    public String build(List<ApiDocsRequestDto> endpoints) {
        ObjectMapper mapper = new ObjectMapper();
        ObjectNode root = mapper.createObjectNode();

        root.put("openapi", "3.0.0");
        ObjectNode info = root.putObject("info");
        info.put("title", "Auto-generated API");
        info.put("version", "1.0.0");

        ObjectNode paths = root.putObject("paths");

        for (ApiDocsRequestDto ep : endpoints) {
            if (ep.getPath() != null && ep.getMethods() != null) {
                ObjectNode pathItem = paths.putObject(ep.getPath());
                for (String method : ep.getMethods()) {
                    ObjectNode methodNode = pathItem.putObject(method.toLowerCase());
                    
                    // Summary
                    if (ep.getSummary() != null) {
                        methodNode.put("summary", ep.getSummary());
                    } else {
                        methodNode.put("summary", "Generated endpoint for " + ep.getView());
                    }
                    
                    // Description
                    if (ep.getDescription() != null) {
                        methodNode.put("description", ep.getDescription());
                    }
                    
                    // Parameters
                    if (ep.getParameters() != null && !ep.getParameters().isEmpty()) {
                        ArrayNode parameters = methodNode.putArray("parameters");
                        for (Map<String, Object> param : ep.getParameters()) {
                            ObjectNode paramNode = parameters.addObject();
                            param.forEach((key, value) -> {
                                if (value instanceof String) {
                                    paramNode.put(key, (String) value);
                                } else if (value instanceof Boolean) {
                                    paramNode.put(key, (Boolean) value);
                                } else if (value instanceof Integer) {
                                    paramNode.put(key, (Integer) value);
                                }
                            });
                        }
                    }
                    
                    // Request Body
                    if (ep.getRequestBody() != null) {
                        ObjectNode requestBody = methodNode.putObject("requestBody");
                        ep.getRequestBody().forEach((key, value) -> {
                            if (value instanceof String) {
                                requestBody.put(key, (String) value);
                            } else if (value instanceof Boolean) {
                                requestBody.put(key, (Boolean) value);
                            }
                        });
                    }
                    
                    // Responses
                    ObjectNode responses = methodNode.putObject("responses");
                    if (ep.getResponses() != null) {
                        ep.getResponses().forEach((statusCode, response) -> {
                            ObjectNode responseNode = responses.putObject(statusCode);
                            if (response instanceof Map) {
                                Map<String, Object> responseMap = (Map<String, Object>) response;
                                responseMap.forEach((key, value) -> {
                                    if (value instanceof String) {
                                        responseNode.put(key, (String) value);
                                    } else if (value instanceof Boolean) {
                                        responseNode.put(key, (Boolean) value);
                                    }
                                });
                            }
                        });
                    } else {
                        responses.putObject("200").put("description", "OK");
                    }
                }
            }
        }

        try {
            return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(root);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize OpenAPI", e);
        }
    }
}
