package com.odk.mediahub.mcp_docs_server.service;

import org.springframework.stereotype.Component;

@Component
public class LLMPromptBuilder {

    public String buildPrompt(String fullCode) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("당신은 OpenAPI 문서를 생성하는 AI입니다.\n");
        prompt.append("다음은 Django REST Framework 기반의 코드입니다.\n");
        prompt.append("이 코드로부터 OpenAPI 3.0 JSON 문서를 생성해주세요.\n");
        prompt.append("코드:\n\n");
        prompt.append(fullCode);
        prompt.append("\n\n---\n출력 형식: JSON (OpenAPI 3.0 호환)");

        return prompt.toString();
    }
}