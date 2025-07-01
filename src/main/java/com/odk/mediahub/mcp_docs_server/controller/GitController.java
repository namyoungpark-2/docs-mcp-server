package com.odk.mediahub.mcp_docs_server.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.io.File;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

import com.odk.mediahub.mcp_docs_server.dto.GitRequestDto;
import com.odk.mediahub.mcp_docs_server.service.GitService;

@RestController
@RequestMapping("/git")
public class GitController {
    private final GitService gitService;

    public GitController(GitService gitService) {
        this.gitService = gitService;
    }

    @PostMapping("/clone")
    public ResponseEntity<String> cloneRepo(@RequestBody GitRequestDto request) {
        File repoDir = gitService.cloneRepo(request.getRepoUrl(), request.getBranch());

        return ResponseEntity.ok(repoDir.getAbsolutePath());
    }
}
