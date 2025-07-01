package com.odk.mediahub.mcp_docs_server.service;

import org.springframework.stereotype.Service;

import com.odk.mediahub.mcp_docs_server.dto.ApiDocsRequestDto;

import java.io.File;
import java.util.Collections;
import java.util.List;

@Service
public class DjangoOpenApiExtractor {
    public List<ApiDocsRequestDto> extract(File repo) {
        // Optional fallback logic, replaced by PythonOpenApiAnalyzer
        return Collections.emptyList();
    }
}
