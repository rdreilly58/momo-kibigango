/**
 * Telegraph Integration Module - TypeScript
 * Integrates Telegraph with OpenClaw workflows
 */

import TelegraphPublisher from "./telegraph_publisher.ts";

/**
 * Code block formatter with syntax highlighting support
 */
export class CodeBlockFormatter {
  /**
   * Format code block with language specification
   */
  static formatCodeBlock(code: string, language: string = "javascript"): string {
    // Escape HTML
    code = code
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    return `<pre><code class="language-${language}">${code}</code></pre>`;
  }

  /**
   * Extract code blocks from content
   */
  static extractCodeBlocks(
    content: string
  ): Record<string, string[]> {
    const blocks: Record<string, string[]> = {};

    // Match ```language ... ``` blocks
    const pattern = /```(\w+)?\n(.*?)```/gs;
    let match;

    while ((match = pattern.exec(content)) !== null) {
      const lang = match[1] || "plaintext";
      const code = match[2].trim();

      if (!blocks[lang]) {
        blocks[lang] = [];
      }
      blocks[lang].push(code);
    }

    return blocks;
  }
}

/**
 * Table formatter with HTML generation
 */
export class TableFormatter {
  /**
   * Convert Markdown table to HTML
   */
  static markdownTableToHtml(markdownTable: string): string {
    const lines = markdownTable.trim().split("\n");
    if (lines.length < 2) return "";

    // Extract headers
    const headers = lines[0]
      .split("|")
      .map((h) => h.trim())
      .filter((h) => h);

    // Skip separator line
    // Extract rows
    const rows: string[][] = [];
    for (let i = 2; i < lines.length; i++) {
      const line = lines[i];
      if (line.trim()) {
        const cells = line
          .split("|")
          .map((c) => c.trim())
          .filter((c) => c);
        rows.push(cells);
      }
    }

    // Generate HTML
    let html = '<table border="1" cellpadding="5">';

    // Header
    html += "<thead><tr>";
    for (const header of headers) {
      html += `<th>${header}</th>`;
    }
    html += "</tr></thead>";

    // Body
    html += "<tbody>";
    for (const row of rows) {
      html += "<tr>";
      for (const cell of row) {
        html += `<td>${cell}</td>`;
      }
      html += "</tr>";
    }
    html += "</tbody>";

    html += "</table>";
    return html;
  }
}

/**
 * Metrics formatter with visualization
 */
export class MetricsFormatter {
  /**
   * Format metrics as HTML cards
   */
  static formatMetrics(metrics: Record<string, string | number>): string {
    let html =
      '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">';

    for (const [metricName, metricValue] of Object.entries(metrics)) {
      html += `
      <div style="border: 1px solid #ccc; padding: 10px; border-radius: 5px;">
          <strong>${metricName}</strong><br/>
          <span style="font-size: 24px; color: #0066cc;">${metricValue}</span>
      </div>
      `;
    }

    html += "</div>";
    return html;
  }

  /**
   * Format status report with metrics and summary
   */
  static formatStatusReport(data: Record<string, any>): string {
    let html = "<h2>Status Report</h2>";
    html += `<p><em>Generated: ${new Date().toLocaleString()} EDT</em></p>`;

    if (data.summary) {
      html += `<p>${data.summary}</p>`;
    }

    if (data.metrics) {
      html += "<h3>Metrics</h3>";
      html += this.formatMetrics(data.metrics);
    }

    if (data.sections) {
      for (const [sectionName, sectionContent] of Object.entries(
        data.sections
      )) {
        html += `<h3>${sectionName}</h3>`;
        html += `<p>${sectionContent}</p>`;
      }
    }

    return html;
  }
}

/**
 * Subagent output integration
 */
export class SubagentOutputIntegration {
  private publisher: TelegraphPublisher;

  constructor(publisher: TelegraphPublisher) {
    this.publisher = publisher;
  }

  /**
   * Process subagent output and publish to Telegraph
   */
  async processSubagentOutput(
    output: string,
    title?: string,
    author?: string
  ): Promise<string> {
    if (!title) {
      const now = new Date();
      title = `Subagent Report - ${now.toISOString().split("T")[0]}`;
    }

    // Format output
    const formattedOutput = this.formatSubagentOutput(output);

    // Publish
    const url = await this.publisher.publishHtml(title, formattedOutput, author);

    console.log(`[INFO] Subagent output published: ${url}`);
    return url;
  }

  /**
   * Format subagent output with proper styling
   */
  private formatSubagentOutput(output: string): string {
    let html =
      "<div style='font-family: system-ui, -apple-system, sans-serif; line-height: 1.6;'>";

    // Process code blocks
    output = output.replace(
      /```(\w+)?\n(.*?)```/gs,
      (_match, lang, code) =>
        CodeBlockFormatter.formatCodeBlock(code, lang || "plaintext")
    );

    // Convert basic markdown
    output = output.replace(/^# (.*?)$/gm, "<h1>$1</h1>");
    output = output.replace(/^## (.*?)$/gm, "<h2>$1</h2>");
    output = output.replace(/^### (.*?)$/gm, "<h3>$1</h3>");

    // Bold and italic
    output = output.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    output = output.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Links
    output = output.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

    // Line breaks
    output = output.replace(/\n\n/g, "</p><p>");
    output = `<p>${output}</p>`;

    html += output;
    html += "</div>";

    return html;
  }
}

/**
 * Media handler for file uploads
 */
export class MediaHandler {
  private publisher: TelegraphPublisher;

  constructor(publisher: TelegraphPublisher) {
    this.publisher = publisher;
  }

  /**
   * Upload media file
   */
  async uploadMedia(filePath: string): Promise<string> {
    return this.publisher.uploadMedia(filePath);
  }

  /**
   * Create image embed HTML
   */
  createImageEmbed(
    mediaUrl: string,
    alt: string = "Image",
    width: number = 400
  ): string {
    return `<img src="${mediaUrl}" alt="${alt}" style="max-width: ${width}px; border-radius: 5px;">`;
  }

  /**
   * Create video embed HTML (YouTube)
   */
  createVideoEmbed(
    videoId: string,
    width: number = 400,
    height: number = 300
  ): string {
    return `
    <iframe width="${width}" height="${height}" 
            src="https://www.youtube.com/embed/${videoId}" 
            frameborder="0" allowfullscreen></iframe>
    `;
  }
}

/**
 * Telegraph heartbeat integration
 */
export class TelegraphHeartbeatIntegration {
  private publisher: TelegraphPublisher;
  private tokenPath: string;

  constructor(publisher: TelegraphPublisher, tokenPath: string) {
    this.publisher = publisher;
    this.tokenPath = tokenPath;
  }

  /**
   * Publish heartbeat report to Telegraph
   */
  async publishHeartbeatReport(reportData: Record<string, any>): Promise<string> {
    const now = new Date();
    const title = `OpenClaw Heartbeat - ${now.toLocaleString()} EDT`;
    const content = MetricsFormatter.formatStatusReport(reportData);

    const url = await this.publisher.publishHtml(title, content, "OpenClaw");

    console.log(`[INFO] Heartbeat report published: ${url}`);
    return url;
  }

  /**
   * Log heartbeat URLs to file for history
   */
  async logHeartbeatHistory(
    heartbeatLog: Record<string, string>,
    filePath: string
  ): Promise<void> {
    try {
      // Load existing log
      let logData: Array<{
        timestamp: string;
        name: string;
        url: string;
      }> = [];

      try {
        if (typeof Deno !== "undefined") {
          const content = await Deno.readTextFile(filePath);
          logData = JSON.parse(content);
        } else {
          const fs = await import("fs");
          const fsPromises = fs.promises;
          const content = await fsPromises.readFile(filePath, "utf-8");
          logData = JSON.parse(content);
        }
      } catch {
        // File doesn't exist yet
        logData = [];
      }

      // Add new entries
      for (const [name, url] of Object.entries(heartbeatLog)) {
        logData.push({
          timestamp: new Date().toISOString(),
          name,
          url,
        });
      }

      // Save
      if (typeof Deno !== "undefined") {
        await Deno.writeTextFile(filePath, JSON.stringify(logData, null, 2));
      } else {
        const fs = await import("fs");
        const fsPromises = fs.promises;
        await fsPromises.writeFile(filePath, JSON.stringify(logData, null, 2));
      }

      console.log(`[INFO] Heartbeat history logged: ${filePath}`);
    } catch (error) {
      console.error(`[ERROR] Failed to log heartbeat history: ${error}`);
    }
  }
}

/**
 * CLI helper for command-line interface
 */
export class TelegraphCliHelper {
  /**
   * Load or create publisher
   */
  static async loadOrCreatePublisher(
    tokenPath?: string
  ): Promise<TelegraphPublisher> {
    try {
      if (tokenPath) {
        const token = await TelegraphPublisher.loadToken(tokenPath);
        console.log(`[INFO] Loaded token from ${tokenPath}`);
        return new TelegraphPublisher(token);
      }
    } catch {
      // Token doesn't exist, create new account
    }

    console.log("[INFO] Creating new Telegraph account...");
    const publisher = new TelegraphPublisher();
    await publisher.createAccount();
    if (tokenPath) {
      await publisher.saveToken(tokenPath);
    }
    return publisher;
  }

  /**
   * Load file content
   */
  static async loadFileContent(filePath: string): Promise<string> {
    try {
      if (typeof Deno !== "undefined") {
        return await Deno.readTextFile(filePath);
      } else {
        const fs = await import("fs");
        const fsPromises = fs.promises;
        return await fsPromises.readFile(filePath, "utf-8");
      }
    } catch (error) {
      throw new Error(`Failed to read file: ${error}`);
    }
  }

  /**
   * Format file content for publishing
   */
  static formatFileContent(
    content: string,
    formatType: string = "markdown"
  ): string {
    switch (formatType) {
      case "markdown":
        // Markdown is handled by publisher
        return content;
      case "html":
        return content;
      case "text":
        // Wrap in <pre> for code/text
        return `<pre style="white-space: pre-wrap; word-wrap: break-word;">${content}</pre>`;
      default:
        return content;
    }
  }
}

export default {
  CodeBlockFormatter,
  TableFormatter,
  MetricsFormatter,
  SubagentOutputIntegration,
  MediaHandler,
  TelegraphHeartbeatIntegration,
  TelegraphCliHelper,
};
