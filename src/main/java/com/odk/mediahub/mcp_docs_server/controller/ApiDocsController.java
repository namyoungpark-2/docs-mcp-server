package com.odk.mediahub.mcp_docs_server.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.MediaType;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.odk.mediahub.mcp_docs_server.constants.FilePath;
import com.odk.mediahub.mcp_docs_server.constants.ErrorHtml;
import com.odk.mediahub.mcp_docs_server.dto.ApiDocsRequestDto;

@RestController
public class ApiDocsController {

    @GetMapping(value = "/api-docs/html", produces = MediaType.TEXT_HTML_VALUE)
    public ResponseEntity<String> getApiDocsHtml(
            @RequestParam String repo,
            @RequestParam String branch) {
        try {
            Resource resource = new ClassPathResource(FilePath.SWAGGER_VIEWER_HTML);
            String html = new String(resource.getInputStream().readAllBytes());
            html = html.replace("${specUrl}", repo + "/" + branch);
            return ResponseEntity.ok(html);
            
        } catch (IOException e) {
            String errorHtml = ErrorHtml.ERROR_HTML.formatted(e.getMessage());
            return ResponseEntity.ok(errorHtml);
        }
    }

    @GetMapping(value = "/api-docs/json", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getApiDocsJson() {
        try {
            String docsPath = FilePath.API_DOCS_DIRECTORY + "/ucms-be_api_docs.json";
            
            String jsonContent = new String(Files.readAllBytes(Paths.get(docsPath)));
            
            return ResponseEntity.ok(jsonContent);
            
        } catch (IOException e) {
            return ResponseEntity.status(500)
                .body("{\"error\": \"문서 파일을 읽을 수 없습니다: " + e.getMessage() + "\"}");
        }
    }
} 