package com.odk.mediahub.mcp_docs_server.service;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;
import java.lang.String;

import org.springframework.http.HttpEntity;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import java.util.Map;
import java.util.HashMap;
import com.fasterxml.jackson.databind.ObjectMapper;

@Component
public class LLMClient {
    @Value("${ollama.api.url:http://localhost:11434}")
    private String ollamaApiUrl;
    
    @Value("${ollama.model:llama3}")
    private String ollamaModel;
    
    public LLMClient() {}

    public String generateOpenApiJson(String prompt) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", ollamaModel);
            requestBody.put("prompt", prompt);
            requestBody.put("stream", false);
            requestBody.put("options", Map.of(
                "temperature", 0.1,  // 더 일관된 응답을 위해 낮춤
                "top_p", 0.9,
                "num_predict", 4096
            ));
            HttpEntity<?> requestEntity = new HttpEntity<>(requestBody, headers);
        
            ResponseEntity<Map> response = new RestTemplate().postForEntity(
                ollamaApiUrl + "/api/generate",
                requestEntity, Map.class
            );

            Map<String, Object> responseBody = response.getBody();
            if (responseBody == null) {
                throw new RuntimeException("Empty response from Ollama");
            }
            
            String responseText = (String) responseBody.get("response");
            if (responseText == null || responseText.trim().isEmpty()) {
                throw new RuntimeException("Empty response content from Ollama. Response: " + responseBody);
            }
            
            // 응답에서 JSON만 추출
            // String cleanedResponse = extractJsonFromResponse(responseText);
            return responseText;
            
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate test data with Ollama: " + e.getMessage());
        }
    }

    private String extractJsonFromResponse(String response) {
        // JSON 객체 시작과 끝 찾기
        int startBrace = response.indexOf('{');
        int endBrace = response.lastIndexOf('}');
        
        if (startBrace != -1 && endBrace != -1 && endBrace > startBrace) {
            String jsonPart = response.substring(startBrace, endBrace + 1);
            
            // JSON 유효성 검사
            try {
                new ObjectMapper().readTree(jsonPart);
                return jsonPart;
            } catch (Exception e) {
            }
        }
        
        // JSON을 찾을 수 없으면 원본 반환
        return response;
    }
}