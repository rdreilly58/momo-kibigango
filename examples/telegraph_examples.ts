/**
 * Telegraph Examples - TypeScript/Deno
 * Demonstrates all major Telegraph use cases
 */

import TelegraphPublisher from "../scripts/telegraph_publisher.ts";
import {
  CodeBlockFormatter,
  TableFormatter,
  MetricsFormatter,
  SubagentOutputIntegration,
  MediaHandler,
  TelegraphCliHelper,
} from "../scripts/telegraph_integration.ts";

/**
 * Example 1: Simple Markdown publication
 */
async function example1SimplMarkdown(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 1: Simple Markdown Publication");
  console.log("=".repeat(60));

  // Create publisher and account
  const publisher = new TelegraphPublisher();
  const token = await publisher.createAccount(
    "deno_example1",
    "OpenClaw"
  );
  console.log(`✓ Account created with token: ${token.substring(0, 30)}...`);

  // Markdown content
  const markdownContent = `
# Hello Telegraph!

This is a **simple** Markdown document published to Telegraph.

## Features

- Easy to use
- Supports *markdown* formatting
- Fast publication

[Visit GitHub](https://github.com)
`;

  // Publish
  const url = await publisher.publishMarkdown(
    "Simple Markdown Example (Deno)",
    markdownContent,
    "OpenClaw"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Example 2: Code documentation with syntax highlighting
 */
async function example2CodeDocumentation(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 2: Code Documentation with Syntax Highlighting");
  console.log("=".repeat(60));

  const publisher = new TelegraphPublisher();
  await publisher.createAccount("deno_example2", "OpenClaw");

  // TypeScript code example
  const typeScriptCode = `
interface TelegraphConfig {
  apiUrl: string;
  maxRetries: number;
}

class TelegraphPublisher {
  async publishMarkdown(
    title: string,
    content: string
  ): Promise<string> {
    // Implementation here
    return url;
  }
}
`;

  // Format code block
  const formattedCode = CodeBlockFormatter.formatCodeBlock(
    typeScriptCode,
    "typescript"
  );

  const htmlContent = `
<h1>TypeScript Telegraph Integration</h1>
<p>A complete example of using Telegraph with TypeScript:</p>
${formattedCode}
<p><strong>Features:</strong></p>
<ul>
    <li>Full type safety</li>
    <li>Modern async/await</li>
    <li>Deno and Node.js support</li>
</ul>
`;

  // Publish
  const url = await publisher.publishHtml(
    "TypeScript Code Documentation",
    htmlContent,
    "Code Reviewer"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Example 3: Status report with GFM (GitHub Flavored Markdown)
 */
async function example3StatusReport(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 3: Status Report with GFM");
  console.log("=".repeat(60));

  const publisher = new TelegraphPublisher();
  await publisher.createAccount("deno_example3", "OpenClaw");

  // Report data
  const reportData: Record<string, any> = {
    summary: "Weekly development status - All on track",
    metrics: {
      "Completed Tasks": "24",
      "In Progress": "8",
      "Pending": "12",
      "Build Success": "98.5%",
      "Test Coverage": "92%",
    },
    sections: {
      "Development": "Completed core API endpoints and database migrations.",
      "Testing": "All unit tests passing, integration tests 95% complete.",
      "DevOps": "CI/CD pipeline optimized, deployment time reduced by 30%.",
    },
  };

  // Format as status report
  const htmlContent = MetricsFormatter.formatStatusReport(reportData);

  // Publish
  const url = await publisher.publishHtml(
    `Development Status Report - ${new Date().toISOString().split("T")[0]}`,
    htmlContent,
    "Project Lead"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Example 4: Blog post publishing
 */
async function example4BlogPost(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 4: Blog Post Publishing");
  console.log("=".repeat(60));

  const publisher = new TelegraphPublisher();
  await publisher.createAccount("deno_blog_example", "OpenClaw Blog");

  const blogContent = `
# Telegraph + Deno: A Powerful Publishing Combination

Telegraph is an excellent platform for publishing content,
and Deno provides a modern runtime for TypeScript.

## Why Telegraph?

Telegraph offers several advantages:

1. **Simplicity** - Clean API, minimal overhead
2. **Speed** - Content published instantly
3. **Reliability** - Built on robust infrastructure
4. **Flexibility** - HTML and Markdown support

## Getting Started with Deno

Here's a quick example:

\`\`\`typescript
import TelegraphPublisher from "./telegraph_publisher.ts";

const publisher = new TelegraphPublisher();
await publisher.createAccount();

const url = await publisher.publishMarkdown(
  "My First Post",
  "Hello from Deno!"
);
console.log(\`Published: \${url}\`);
\`\`\`

## Key Features

- Full TypeScript support
- Zero dependencies
- Works in both Deno and Node.js
- Automatic retries with exponential backoff
- Media upload support

## Conclusion

Telegraph + Deno is the ideal combination for fast, reliable content publishing.

**Happy publishing!**
`;

  const url = await publisher.publishMarkdown(
    "Telegraph + Deno: Publishing Made Easy",
    blogContent,
    "OpenClaw Team"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Example 5: Media embedding
 */
async function example5MediaEmbedding(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 5: Media Embedding");
  console.log("=".repeat(60));

  const publisher = new TelegraphPublisher();
  await publisher.createAccount("deno_media_example", "OpenClaw");

  const mediaHandler = new MediaHandler(publisher);

  // Create content with media
  const htmlContent = `
<h1>Media Embedding Example</h1>
<p>This page demonstrates media embedding in Telegraph:</p>

<h2>Embedded Video</h2>
<p>You can embed YouTube videos using iframe:</p>
${mediaHandler.createVideoEmbed("dQw4w9WgXcQ")}

<h2>Benefits of Rich Media</h2>
<ul>
    <li>Enhanced engagement</li>
    <li>Professional presentation</li>
    <li>Interactive content</li>
</ul>

<h2>Gallery of Options</h2>
<p>You can embed:</p>
<ul>
    <li>Images (JPG, PNG, GIF)</li>
    <li>Videos (YouTube, Vimeo)</li>
    <li>Iframes (custom content)</li>
</ul>
`;

  // Publish
  const url = await publisher.publishHtml(
    "Media Embedding Example",
    htmlContent,
    "Media Producer"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Example 6: Table formatting
 */
async function example6TableFormatting(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 6: Table Formatting");
  console.log("=".repeat(60));

  const publisher = new TelegraphPublisher();
  await publisher.createAccount("deno_table_example", "OpenClaw");

  // Markdown table
  const markdownTable = `
| Feature | Status | Progress |
|---------|--------|----------|
| Core API | ✓ Done | 100% |
| Frontend | ⚠ WIP | 75% |
| Mobile | ◯ Planned | 0% |
| Docs | ✓ Done | 100% |
`;

  // Convert to HTML
  const htmlTable = TableFormatter.markdownTableToHtml(markdownTable);

  const htmlContent = `
<h1>Product Roadmap</h1>
<p>Current progress across all components:</p>
${htmlTable}
<p style="font-style: italic; margin-top: 20px;">
    Last updated: ${new Date().toLocaleString()}
</p>
`;

  const url = await publisher.publishHtml(
    "Product Roadmap Status",
    htmlContent,
    "Product Manager"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Example 7: Subagent output integration
 */
async function example7SubagentIntegration(): Promise<string> {
  console.log("\n" + "=".repeat(60));
  console.log("Example 7: Subagent Output Integration");
  console.log("=".repeat(60));

  const publisher = new TelegraphPublisher();
  await publisher.createAccount("deno_subagent_example", "OpenClaw");

  // Simulate subagent output
  const subagentOutput = `
# Performance Analysis
## Request Summary
Task: Analyze and optimize database queries

## Key Findings

1. **Query Optimization**
   - Reduced average query time: 450ms → 120ms
   - Added strategic indexes
   - Implemented query caching

2. **Results**
   - Overall performance improved 73%
   - Memory usage down 25%
   - API response time halved

## Implementation

\`\`\`typescript
// Added database indexing
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_post_created ON posts(created_at);

// Query optimization
async function getUser(id: string) {
  return cache.get(\`user:\${id}\`) || 
    db.query('SELECT * FROM users WHERE id = ?', [id]);
}
\`\`\`

## Recommendations
- Continue monitoring slow queries
- Schedule weekly performance reviews
- Plan next optimization phase

## Status
✓ Complete - Ready for production deployment
`;

  // Use integration helper
  const integration = new SubagentOutputIntegration(publisher);
  const url = await integration.processSubagentOutput(
    subagentOutput,
    "Performance Analysis Report",
    "Database Optimization"
  );

  console.log(`✓ Published to: ${url}`);
  return url;
}

/**
 * Run all examples
 */
async function runAllExamples(): Promise<void> {
  console.log("\n" + "=".repeat(70));
  console.log("Telegraph Publishing Examples (TypeScript/Deno)");
  console.log("=".repeat(70));

  const examples: Array<{
    name: string;
    fn: () => Promise<string>;
  }> = [
    { name: "Simple Markdown", fn: example1SimplMarkdown },
    { name: "Code Documentation", fn: example2CodeDocumentation },
    { name: "Status Report", fn: example3StatusReport },
    { name: "Blog Post", fn: example4BlogPost },
    { name: "Media Embedding", fn: example5MediaEmbedding },
    { name: "Table Formatting", fn: example6TableFormatting },
    { name: "Subagent Integration", fn: example7SubagentIntegration },
  ];

  const results: Array<{
    name: string;
    result: string;
    status: string;
  }> = [];

  for (const { name, fn } of examples) {
    try {
      const url = await fn();
      results.push({ name, result: url, status: "✓" });
    } catch (error) {
      console.error(`✗ Error: ${error}`);
      results.push({ name, result: String(error), status: "✗" });
    }
  }

  // Summary
  console.log("\n" + "=".repeat(70));
  console.log("Example Results Summary");
  console.log("=".repeat(70));

  for (const { name, result, status } of results) {
    console.log(`${status} ${name}: ${result.substring(0, 80)}`);
  }

  console.log("\n✓ All examples completed!");
}

// Run examples if this is the main module
if (import.meta.main) {
  runAllExamples();
}

export {
  example1SimplMarkdown,
  example2CodeDocumentation,
  example3StatusReport,
  example4BlogPost,
  example5MediaEmbedding,
  example6TableFormatting,
  example7SubagentIntegration,
  runAllExamples,
};
