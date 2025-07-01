package com.odk.mediahub.mcp_docs_server.dto;

public class ApiDocsRequestDto {
    private String repo;
    private String branch;

    public String getRepo() { return repo; }
    public void setRepo(String repo) { this.repo = repo; }

    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }
}
