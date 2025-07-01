package com.odk.mediahub.mcp_docs_server.service;

import org.eclipse.jgit.api.Git;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.odk.mediahub.mcp_docs_server.service.CommandExecutor;

import java.io.File;
import java.nio.file.Files;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;

@Component
public class GitService {
    private final CommandExecutor commandExecutor;

    public GitService(CommandExecutor commandExecutor) {
        this.commandExecutor = commandExecutor;
    }

    @Value("${repos.directory:/clone/repos}")
    private String reposDirectory;
    

    public File cloneRepo(String repoUrl, String branch) {
        File reposDir = new File(reposDirectory);
        if (!reposDir.exists()) {
            reposDir.mkdirs();
        }

        String repoName = extractRepoName(repoUrl);
        File destination = new File(reposDir, repoName);
        
        if (destination.exists()) {
            System.out.println("Repository already exists: " + destination.getAbsolutePath());
            return destination;
        }

        try {
            System.out.println("Cloning repository: " + repoUrl + " to branch: " + branch);
            System.out.println("Destination: " + destination.getAbsolutePath());
            
            commandExecutor.executeCommand(reposDir, "git", "clone", "-b", branch, repoUrl, repoName);

            return destination;
        } catch (IOException | InterruptedException e) {
            System.err.println("Error cloning repository: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
    
    private String extractRepoName(String repoUrl) {
        String[] parts = repoUrl.split("/");
        String lastPart = parts[parts.length - 1];
        return lastPart.replace(".git", "");
    }

}
