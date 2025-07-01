package com.odk.mediahub.mcp_docs_server.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.odk.mediahub.mcp_docs_server.dto.ApiDocsRequestDto;

import org.springframework.stereotype.Component;

import java.io.*;
import java.util.*;

@Component
public class PythonOpenApiAnalyzer {
    public List<ApiDocsRequestDto> analyze(File repoPath) {
        List<ApiDocsRequestDto> endpoints = new ArrayList<>();
        try {
            ProcessBuilder pb = new ProcessBuilder("python3", "python-parser/main.py", repoPath.getAbsolutePath());
            pb.redirectErrorStream(true);
            Process process = pb.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            process.waitFor();

            ObjectMapper mapper = new ObjectMapper();
            System.out.println("Output: " + output.toString());
            ApiDocsRequestDto[] parsed = mapper.readValue(output.toString(), ApiDocsRequestDto[].class);
            endpoints.addAll(Arrays.asList(parsed));
        } catch (Exception e) {
            throw new RuntimeException("Failed to run python parser", e);
        }
        System.out.println("Endpoints: " + endpoints);
        return endpoints;
    }
}
