package com.odk.mediahub.mcp_docs_server.dto;

import java.util.List;
import java.util.Map;

public class ApiDocsRequestDto {
    private String repo;
    private String branch;
    private String path;
    private List<String> methods;
    private String view;
    private String summary;
    private String description;
    private List<Map<String, Object>> parameters;
    private Map<String, Object> requestBody;
    private Map<String, Object> responses;

    // 기본 생성자
    public ApiDocsRequestDto() {}

    // repo, branch만 받는 생성자
    public ApiDocsRequestDto(String repo, String branch) {
        this.repo = repo;
        this.branch = branch;
    }

    // 모든 필드를 받는 생성자
    public ApiDocsRequestDto(String repo, String branch, String path, List<String> methods, String view) {
        this.repo = repo;
        this.branch = branch;
        this.path = path;
        this.methods = methods;
        this.view = view;
    }

    // Getters and Setters
    public String getRepo() { return repo; }
    public void setRepo(String repo) { this.repo = repo; }

    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }

    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }

    public List<String> getMethods() { return methods; }
    public void setMethods(List<String> methods) { this.methods = methods; }

    public String getView() { return view; }
    public void setView(String view) { this.view = view; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public List<Map<String, Object>> getParameters() { return parameters; }
    public void setParameters(List<Map<String, Object>> parameters) { this.parameters = parameters; }

    public Map<String, Object> getRequestBody() { return requestBody; }
    public void setRequestBody(Map<String, Object> requestBody) { this.requestBody = requestBody; }

    public Map<String, Object> getResponses() { return responses; }
    public void setResponses(Map<String, Object> responses) { this.responses = responses; }
}
