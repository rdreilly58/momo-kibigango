# Telegraph Formatting for High-Quality Output

**Research Date:** March 21, 2026  
**Status:** Complete & Ready for Review  
**Use Case:** Display formatted content (code, tables, documentation) over Telegraph channel with rich formatting

---

## Executive Summary

Telegraph is Telegram's minimalist publishing platform that supports **rich HTML/Markdown formatting** for articles. It's the ideal solution for displaying high-quality formatted output (code blocks, tables, documentation, blog posts) when Telegram's native message formatting is insufficient.

**Key Finding:** Telegraph provides professional-grade formatting capabilities that are perfect for OpenClaw's needs, with multiple implementation options available.

---

## What is Telegraph?

- **Official Service:** Telegram's minimalist publishing tool
- **Format:** Full HTML/Markdown support (not just Telegram's limited HTML)
- **Display:** Beautiful Instant View pages in Telegram
- **Use Case:** Long-form content, formatted articles, code documentation
- **Free:** No cost, no authentication required for basic usage
- **API:** Fully documented Telegraph API available

**Links:**
- Official: https://telegra.ph
- API Docs: https://telegra.ph/api
- Instant View info: https://telegram.org/blog/instant-view

---

## Supported HTML Tags (Telegraph)

Telegraph supports a richer set of HTML than Telegram's bot API:

### Core Formatting
- **`<b>`, `<strong>`** — Bold text
- **`<i>`, `<em>`** — Italic text
- **`<u>`, `<ins>`** — Underline
- **`<s>`, `<strike>`** — Strikethrough
- **`<code>`** — Inline code
- **`<pre><code>`** — Code blocks

### Structure
- **`<h3>`, `<h4>`** — Headings (h3-h6 supported)
- **`<p>`** — Paragraphs
- **`<br>`** — Line breaks
- **`<a href="url">`** — Links
- **`<img>`** — Images
- **`<blockquote>`** — Quoted text
- **`<hr>`** — Horizontal rule

### Lists
- **`<ul>`, `<ol>`, `<li>`** — Unordered/ordered lists
- **`<dl>`, `<dt>`, `<dd>`** — Definition lists

### Advanced
- **`<aside>`** — Sidebars
- **`<figure>`, `<figcaption>`** — Image captions
- **`<iframe>`** — Embedded content (YouTube, Vimeo)
- **`<table>`** — HTML tables (limited, no CSS styling)

### Not Supported
- CSS styling/classes
- Complex layouts (flexbox, grid)
- Custom attributes (mostly ignored)
- Media embedding (use iframe instead)

---

## Implementation Options

### Option 1: Python `html-telegraph-poster` (RECOMMENDED)

**Repository:** https://github.com/mercuree/html-telegraph-poster  
**Language:** Python  
**Maturity:** Stable, actively used

**Pros:**
- ✅ Converts HTML → Telegraph format automatically
- ✅ Supports HTML cleanup/normalization
- ✅ Markdown support available
- ✅ Easy Python integration
- ✅ YouTube/Vimeo iframe embedding
- ✅ Can edit existing pages

**Cons:**
- Requires API token setup
- Limited to Python ecosystem

**Installation:**
```bash
pip install html-telegraph-poster
```

**Usage:**
```python
from html_telegraph_poster import TelegraphPoster

t = TelegraphPoster(use_api=True)
t.create_api_token('MyApp', 'author_name', 'https://example.com')

# Create page from HTML
page = t.post(
    title='My Formatted Content',
    author='OpenClaw',
    text='<h3>Title</h3><p>Content here</p>'
)
print(f"Published at: {page['url']}")
```

**Example Output:**
```
{
  'path': 'My-Formatted-Content-12-31-abc',
  'url': 'http://telegra.ph/My-Formatted-Content-12-31-abc'
}
```

---

### Option 2: JavaScript `@dcdunkan/telegraph` (MODERN)

**Repository:** https://github.com/dcdunkan/telegraph  
**Language:** TypeScript/JavaScript (Deno, Node.js)  
**Registry:** JSR (https://jsr.io/@dcdunkan/telegraph)

**Pros:**
- ✅ Modern TypeScript implementation
- ✅ Native Markdown parsing (via `marked`)
- ✅ HTML parsing support (via `deno-dom`)
- ✅ Media upload support
- ✅ Works with GFM (GitHub Flavored Markdown)
- ✅ Well-documented

**Cons:**
- Requires Node.js or Deno runtime
- Not ideal for OpenClaw's Python-first environment

**Installation (Deno):**
```bash
import { Telegraph, parse } from "jsr:@dcdunkan/telegraph";
```

**Installation (Node.js):**
```bash
npm install @dcdunkan/telegraph marked
```

**Usage Example:**
```javascript
import { Telegraph, parse } from "jsr:@dcdunkan/telegraph";

const telegraph = new Telegraph({ token: "your_token" });

const content = parse(`
# My Title
This is **bold** and this is *italic*.

\`\`\`python
def hello():
    print("world")
\`\`\`
`, "Markdown");

const page = await telegraph.create({
  title: "My Post",
  content: content
});
```

---

### Option 3: Native Telegraph API

**Direct API:** https://api.telegra.ph/

**Pros:**
- ✅ Language-agnostic
- ✅ Full control
- ✅ No dependencies

**Cons:**
- Requires manual Node format construction (complex)
- Lower-level than libraries

**Node Format (Telegraph API):**
```json
{
  "tag": "h3",
  "children": ["Heading Text"]
}
```

This is complex compared to HTML, so libraries are recommended.

---

## Best Practices for High-Quality Output

### 1. **Markdown-First Approach** ✅
- Write content in Markdown
- Convert to Telegraph HTML
- Publish via API
- Best for: Documentation, blog posts, formatted reports

### 2. **Code Block Formatting**
```markdown
## Example Code

\`\`\`python
def process_data(items):
    return [x * 2 for x in items]
\`\`\`

The function above doubles each value.
```

Renders as:
- Syntax highlighting
- Proper indentation
- Monospace font

### 3. **Table Support**
Telegraph supports HTML tables:
```html
<table>
  <tr>
    <th>Column 1</th>
    <th>Column 2</th>
  </tr>
  <tr>
    <td>Value A</td>
    <td>Value B</td>
  </tr>
</table>
```

**Note:** Tables render as plain HTML; no markdown table syntax support.

### 4. **Link Formatting**
```markdown
[Visit OpenClaw](https://github.com/openclaw/openclaw)
```

Renders as clickable links with Instant View preview.

### 5. **Media Embedding**
```html
<img src="https://example.com/image.jpg" />

<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>
```

Supported:
- Images (PNG, JPG, GIF)
- YouTube videos
- Vimeo videos
- Direct media URLs

### 6. **Heading Hierarchy**
Use proper heading structure:
- `<h3>` — Main title (top-level)
- `<h4>` — Sections
- `<h5>` — Subsections (supported)
- `<h6>` — Minor headings (supported)

### 7. **Blockquotes for Emphasis**
```html
<blockquote>
  Important note or quote here.
</blockquote>
```

Renders with left border, distinct styling.

### 8. **Asides for Metadata**
```html
<aside>
  Author: John Doe<br/>
  Published: March 21, 2026
</aside>
```

Renders as sidebar information.

---

## Integration with OpenClaw

### Strategy 1: Subagent Task Output

When a subagent completes a task with formatted output (e.g., blog post, documentation):

1. Subagent writes output as Markdown
2. Main session converts to Telegraph HTML
3. Publishes via Telegraph API
4. Sends Telegram message with link to full article

```python
# In main session
from html_telegraph_poster import TelegraphPoster

# Get markdown from subagent
article_markdown = subagent_result.get('content')

# Convert to Telegraph
poster = TelegraphPoster(use_api=True)
poster.create_api_token('OpenClaw', 'Momotaro')

page = poster.post(
    title=subagent_result.get('title'),
    author='OpenClaw',
    text=article_markdown  # API handles Markdown conversion
)

# Send Telegram link
send_message(f"📄 Full article: {page['url']}")
```

### Strategy 2: HEARTBEAT Status Reports

**Current:** Plain text, limited formatting  
**Future:** Rich Telegraph article with:
- Project status
- Metrics/analytics
- Task summaries
- Links to resources

```
📊 Daily Status Report
━━━━━━━━━━━━━━━━━━━━━━

Tasks Completed: 5
Projects Active: 3
...

View full report: [Telegraph link]
```

### Strategy 3: Code Review / Documentation

Publish:
- Code snippets with syntax highlighting
- Architecture diagrams (as images)
- API documentation
- Tutorial posts

---

## Implementation Roadmap

### Phase 1: Proof of Concept (Week 1)
- [ ] Set up Telegraph API credentials
- [ ] Install `html-telegraph-poster`
- [ ] Create Python wrapper utility
- [ ] Test with sample Markdown → Telegraph → Telegram flow

### Phase 2: Integration (Week 2)
- [ ] Hook into subagent completion events
- [ ] Auto-detect formatted output (code blocks, tables)
- [ ] Route to Telegraph instead of plain Telegram message
- [ ] Add "View Full Article" link to chat

### Phase 3: Enhancement (Week 3)
- [ ] Implement HEARTBEAT report publishing
- [ ] Add image/media upload support
- [ ] Create templates for common output types
- [ ] Document best practices for users

---

## Code Quality Standards for Telegraph Output

When publishing to Telegraph, ensure:

1. **Markdown Valid**
   - Proper heading hierarchy
   - Balanced lists
   - Correct code block syntax

2. **HTML Compliant**
   - Valid nesting (no overlapping tags)
   - Closed tags
   - Proper attribute syntax

3. **Readability**
   - Clear structure with headings
   - Short paragraphs
   - Whitespace for visual separation
   - Links to external resources

4. **SEO-Friendly**
   - Descriptive title
   - Meta description (if supported)
   - Keywords in headings
   - Internal/external links

---

## GitHub Projects & Libraries

| Project | Language | Purpose | Status |
|---------|----------|---------|--------|
| **html-telegraph-poster** | Python | HTML → Telegraph converter | ⭐ Recommended |
| **@dcdunkan/telegraph** | TypeScript | Full API wrapper | ✅ Modern |
| **telegraph.md** | JavaScript | Markdown → Telegraph | ✅ Utilities |
| **sulguk** | Python | HTML → Telegram entities | ✅ Alt option |

---

## OpenClaw Integration Points

### 1. Sessions / Subagent Output
```python
# In main session after subagent completes
if subagent_result.get('format') == 'markdown':
    publish_to_telegraph(subagent_result)
```

### 2. HEARTBEAT Reports
```python
# In heartbeat.md task
telegraph_link = publish_status_report(tasks, metrics)
send_message(f"📊 Status: {telegraph_link}")
```

### 3. Blog Publishing
```python
# Auto-publish blog posts from workspace
for post in workspace.blog_posts:
    telegraph_link = publish_to_telegraph(post)
```

---

## Limitations & Workarounds

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| No CSS styling | Tables/layouts basic | Use proper HTML structure |
| No custom fonts | Font limited to Telegram's | Use bold/italic for emphasis |
| No Markdown tables | Can't use \|--\| syntax | Use HTML `<table>` tags |
| Limited media types | Images only (no direct video) | Use `<iframe>` for YouTube/Vimeo |
| Page length limit | Very long content may fail | Split into multiple pages |

---

## Security Considerations

✅ **Safe to Use:**
- Telegraph is official Telegram service
- No private data leaked (Telegraph serves public URLs)
- Appropriate for publishing documentation, reports, blog posts

⚠️ **What NOT to Publish:**
- API keys, secrets, passwords
- Private user data
- Proprietary source code (unless open-source)
- Sensitive logs

---

## Next Steps for Review

1. **Evaluate Options:** Python vs TypeScript preference?
2. **Choose Integration Point:** Subagent output, HEARTBEAT, or both?
3. **Approve Best Practices:** Agree on formatting standards?
4. **Schedule Implementation:** Which phase first?

---

## Additional Resources

- **Official Telegraph API:** https://telegra.ph/api
- **Telegram Instant View:** https://telegram.org/blog/instant-view
- **Telegraph Editor:** https://edit.telegra.ph (manual page creation)
- **Python Library Docs:** https://github.com/mercuree/html-telegraph-poster
- **JavaScript Docs:** https://jsr.io/@dcdunkan/telegraph/doc

---

**Questions for Bob:**
1. Do you want to publish subagent output (code, reports, blog posts) to Telegraph?
2. Should daily briefings/status reports be published as Telegraph articles?
3. Preference: Python (`html-telegraph-poster`) or JavaScript (`@dcdunkan/telegraph`)?
4. Any specific content types you want to prioritize?
