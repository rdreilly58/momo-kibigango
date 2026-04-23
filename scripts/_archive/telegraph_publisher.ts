/**
 * Telegraph Publisher - TypeScript Implementation
 * Supports both Deno and Node.js runtimes
 */

import type { RequestInit } from "https://deno.land/std@0.208.0/http/http_status.ts";

interface TelegraphConfig {
  apiUrl: string;
  maxRetries: number;
  retryDelay: number;
  timeout: number;
  defaultAuthor: string;
  defaultAuthorUrl: string;
}

interface TelegraphResponse<T = any> {
  ok: boolean;
  result?: T;
  error?: string;
}

interface PageResult {
  url: string;
  path: string;
  title: string;
  content?: any[];
}

interface AccountResult {
  short_name: string;
  access_token: string;
  auth_url: string;
}

interface MediaResult {
  src: string;
}

/**
 * TelegraphPublisher class - Main wrapper for Telegraph API
 */
export class TelegraphPublisher {
  private config: TelegraphConfig;
  private accessToken?: string;
  private accountInfo?: AccountResult;

  constructor(accessToken?: string, config?: Partial<TelegraphConfig>) {
    this.config = {
      apiUrl: "https://api.telegra.ph",
      maxRetries: 3,
      retryDelay: 1.0,
      timeout: 30000,
      defaultAuthor: "OpenClaw",
      defaultAuthorUrl: "https://github.com/anthropics/openclaw",
      ...config,
    };

    this.accessToken = accessToken;

    console.log(
      `[INFO] Initializing Telegraph Publisher (API: ${this.config.apiUrl})`
    );
  }

  /**
   * Make HTTP request to Telegraph API with exponential backoff
   */
  private async request<T = any>(
    method: string,
    endpoint: string,
    data?: Record<string, any>,
    retries: number = 0
  ): Promise<T> {
    const url = `${this.config.apiUrl}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "User-Agent": "OpenClaw/1.0",
    };

    try {
      const requestOptions: RequestInit = {
        method,
        headers,
      };

      if (method === "POST" && data) {
        requestOptions.body = JSON.stringify(data);
      }

      // Use native fetch (works in both Deno and Node.js 18+)
      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result: TelegraphResponse<T> = await response.json();

      if (!result.ok) {
        throw new Error(`Telegraph API error: ${result.error || "Unknown error"}`);
      }

      return result.result as T;
    } catch (error) {
      if (retries < this.config.maxRetries) {
        const waitTime =
          this.config.retryDelay * Math.pow(2, retries); // Exponential backoff
        console.warn(
          `[WARN] Request failed (${retries + 1}/${this.config.maxRetries}): ${error}. Retrying in ${waitTime}s...`
        );
        await this.sleep(waitTime * 1000);
        return this.request<T>(method, endpoint, data, retries + 1);
      } else {
        console.error(
          `[ERROR] Request failed after ${this.config.maxRetries} retries: ${error}`
        );
        throw error;
      }
    }
  }

  /**
   * Sleep for milliseconds (works in both Deno and Node.js)
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Create Telegraph account and return access token
   */
  async createAccount(
    shortName?: string,
    authorName?: string,
    authorUrl?: string
  ): Promise<string> {
    if (!shortName) {
      // Generate unique short name
      const timestamp = Math.floor(Date.now() / 1000);
      shortName = `openclaw_${timestamp}`;
    }

    const data = {
      short_name: shortName,
      author_name: authorName || this.config.defaultAuthor,
      author_url: authorUrl || this.config.defaultAuthorUrl,
    };

    console.log(
      `[INFO] Creating Telegraph account: ${shortName}`
    );
    const result = await this.request<AccountResult>(
      "POST",
      "/createAccount",
      data
    );

    this.accessToken = result.access_token;
    this.accountInfo = result;

    console.log(
      `[INFO] Account created successfully. Token: ${this.accessToken.substring(0, 20)}...`
    );
    return this.accessToken;
  }

  /**
   * Publish Markdown content to Telegraph
   */
  async publishMarkdown(
    title: string,
    content: string,
    author?: string,
    authorUrl?: string
  ): Promise<string> {
    if (!this.accessToken) {
      await this.createAccount();
    }

    // Convert markdown to HTML
    const htmlContent = this.markdownToHtml(content);

    return this.publishHtml(title, htmlContent, author, authorUrl);
  }

  /**
   * Publish HTML content to Telegraph
   */
  async publishHtml(
    title: string,
    content: string | Record<string, any>[],
    author?: string,
    authorUrl?: string
  ): Promise<string> {
    if (!this.accessToken) {
      await this.createAccount();
    }

    // Parse content into Telegraph format if it's HTML string
    let parsedContent: Record<string, any>[] = Array.isArray(content)
      ? content
      : [{ tag: "p", children: [content] }];

    const data: Record<string, any> = {
      access_token: this.accessToken,
      title: title.substring(0, 256), // Telegraph limit
      author_name: author || this.config.defaultAuthor,
      author_url: authorUrl || this.config.defaultAuthorUrl,
      content: parsedContent,
      return_content: true,
    };

    console.log(`[INFO] Publishing page: ${title}`);
    const result = await this.request<PageResult>(
      "POST",
      "/createPage",
      data
    );

    const url = result.url;
    console.log(`[INFO] Page published successfully: ${url}`);
    return url;
  }

  /**
   * Update existing Telegraph page
   */
  async updatePage(
    path: string,
    content: string | Record<string, any>[],
    title?: string,
    author?: string,
    authorUrl?: string
  ): Promise<string> {
    if (!this.accessToken) {
      throw new Error("Access token required for updating pages");
    }

    // Parse content
    let parsedContent: Record<string, any>[] = Array.isArray(content)
      ? content
      : [{ tag: "p", children: [content] }];

    const data: Record<string, any> = {
      access_token: this.accessToken,
      path,
      content: parsedContent,
      return_content: true,
    };

    if (title) data.title = title.substring(0, 256);
    if (author) data.author_name = author;
    if (authorUrl) data.author_url = authorUrl;

    console.log(`[INFO] Updating page: ${path}`);
    const result = await this.request<PageResult>(
      "POST",
      "/editPage",
      data
    );

    const url = result.url;
    console.log(`[INFO] Page updated successfully: ${url}`);
    return url;
  }

  /**
   * Retrieve Telegraph page
   */
  async getPage(
    path: string,
    returnContent: boolean = true
  ): Promise<PageResult> {
    const data = {
      path,
      return_content: returnContent,
    };

    console.log(`[INFO] Fetching page: ${path}`);
    return this.request<PageResult>("GET", `/getPage/${path}`, data);
  }

  /**
   * Upload image or media file to Telegraph
   */
  async uploadMedia(filePath: string): Promise<string> {
    console.log(`[INFO] Uploading media: ${filePath}`);

    // Read file (works in both Deno and Node.js with conditional imports)
    let fileBuffer: Uint8Array;

    try {
      // Try Deno API first
      if (typeof Deno !== "undefined") {
        fileBuffer = await Deno.readFile(filePath);
      } else {
        // Node.js fallback
        const fs = await import("fs");
        const fsPromises = fs.promises;
        fileBuffer = await fsPromises.readFile(filePath);
      }
    } catch (error) {
      throw new Error(`Failed to read file: ${filePath}`);
    }

    // Create FormData and upload
    const formData = new FormData();
    const blob = new Blob([fileBuffer]);
    formData.append("file", blob, filePath);

    try {
      const response = await fetch(`${this.config.apiUrl}/upload`, {
        method: "POST",
        body: formData,
      });

      const result: MediaResult[] = await response.json();

      if (!Array.isArray(result) || result.length === 0) {
        throw new Error(`Media upload failed: ${JSON.stringify(result)}`);
      }

      const mediaUrl = `https://telegra.ph${result[0].src}`;
      console.log(`[INFO] Media uploaded: ${mediaUrl}`);
      return mediaUrl;
    } catch (error) {
      throw new Error(`Media upload error: ${error}`);
    }
  }

  /**
   * Convert basic Markdown to HTML
   */
  private markdownToHtml(markdown: string): string {
    let html = markdown;

    // Headers
    html = html.replace(/^### (.*?)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.*?)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.*?)$/gm, "<h1>$1</h1>");

    // Bold and italic
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    html = html.replace(/__(.*?)__/g, "<strong>$1</strong>");
    html = html.replace(/_(.*?)_/g, "<em>$1</em>");

    // Code blocks
    html = html.replace(/```(.*?)```/gs, "<pre><code>$1</code></pre>");
    html = html.replace(/`([^`]*?)`/g, "<code>$1</code>");

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

    // Line breaks
    html = html.replace(/\n\n/g, "</p><p>");
    html = `<p>${html}</p>`;

    // Lists
    html = html.replace(/^\* (.*?)$/gm, "<li>$1</li>");

    return html;
  }

  /**
   * Save access token to file
   */
  async saveToken(filePath: string): Promise<void> {
    if (!this.accessToken) {
      throw new Error("No access token to save");
    }

    const data = {
      access_token: this.accessToken,
      account_info: this.accountInfo,
      created_at: new Date().toISOString(),
    };

    try {
      // Try Deno API first
      if (typeof Deno !== "undefined") {
        const fileUrl = new URL("file:///" + filePath).href;
        await Deno.writeTextFile(filePath, JSON.stringify(data, null, 2));
      } else {
        // Node.js fallback
        const fs = await import("fs");
        const fsPromises = fs.promises;
        await fsPromises.writeFile(filePath, JSON.stringify(data, null, 2));
      }
      console.log(`[INFO] Token saved to: ${filePath}`);
    } catch (error) {
      throw new Error(`Failed to save token: ${error}`);
    }
  }

  /**
   * Load access token from file
   */
  static async loadToken(filePath: string): Promise<string> {
    try {
      let content: string;

      // Try Deno API first
      if (typeof Deno !== "undefined") {
        content = await Deno.readTextFile(filePath);
      } else {
        // Node.js fallback
        const fs = await import("fs");
        const fsPromises = fs.promises;
        content = await fsPromises.readFile(filePath, "utf-8");
      }

      const data = JSON.parse(content);
      return data.access_token;
    } catch (error) {
      throw new Error(`Failed to load token: ${error}`);
    }
  }
}

export default TelegraphPublisher;
