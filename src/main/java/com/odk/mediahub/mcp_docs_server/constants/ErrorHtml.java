package com.odk.mediahub.mcp_docs_server.constants;

public final class ErrorHtml {
  public static final String ERROR_HTML = """
    <html>
    <head><title>API 문서 오류</title></head>
    <body>
        <h1>API 문서를 불러올 수 없습니다</h1>
        <p>오류: %s</p>
        <p>python-parser에서 API 문서를 먼저 생성해주세요.</p>
    </body>
    </html>
    """;
}
