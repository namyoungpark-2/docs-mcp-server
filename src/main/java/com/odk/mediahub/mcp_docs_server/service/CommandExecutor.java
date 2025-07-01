package com.odk.mediahub.mcp_docs_server.service;

import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;

@Component
public class CommandExecutor {

  public String executeCommand(File workingDir, String... command) throws IOException, InterruptedException {
    ProcessBuilder processBuilder = new ProcessBuilder(command);
    processBuilder.directory(workingDir);
    processBuilder.redirectErrorStream(true);
    
    Process process = processBuilder.start();
    
    StringBuilder output = new StringBuilder();
    try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
        String line;
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
        }
    }

    int exitCode = process.waitFor();
    
    if (exitCode != 0) {
        String errorMsg = "Command failed with exit code " + exitCode + ": " + String.join(" ", command);
        throw new RuntimeException(errorMsg + "\nOutput: " + output.toString());
    }
    
    return output.toString();
  }
}
