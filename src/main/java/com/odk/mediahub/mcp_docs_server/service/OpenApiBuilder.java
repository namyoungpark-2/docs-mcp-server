package com.odk.mediahub.mcp_docs_server.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.*;
import com.odk.mediahub.mcp_docs_server.dto.ApiDocsRequestDto;

import org.springframework.stereotype.Component;

import java.util.List;

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
            ObjectNode pathItem = paths.putObject(ep.getPath());
            for (String method : ep.getMethods()) {
                ObjectNode methodNode = pathItem.putObject(method.toLowerCase());
                methodNode.put("summary", "Generated endpoint for " + ep.getView());
                ObjectNode responses = methodNode.putObject("responses");
                responses.putObject("200").put("description", "OK");
            }
        }

        try {
            return mapper.writerWithDefaultPrettyPrinter().writeValueAsString(root);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize OpenAPI", e);
        }
    }
}
