# Resilient File Handling & PowerPoint Generation

Tools for robust file operations and automated PowerPoint creation using Claude Skills.

## 📚 What's Included

### 1. **Resilient File Handler** (`resilient_file_handler.py`)
Production-ready file handling with graceful error recovery and automatic fallbacks.

### 2. **PowerPoint Generator** (`claude_skills_pptx.py`)
Generate professional presentations using Claude's pptx skill.

---

## 🛡️ Resilient File Handler

### Philosophy

**Traditional Approach:**
```python
# ❌ Crashes on missing file
with open('config.json') as f:
    data = json.load(f)  # FileNotFoundError!
```

**Resilient Approach:**
```python
# ✅ Gracefully handles errors
handler = ResilientFileHandler(create_missing=True)
data = handler.safe_read_json('config.json', default={})
# Returns default if missing, creates file automatically
```

### Features

- ✅ **Auto-create missing files** with sensible defaults
- ✅ **Graceful error handling** for permissions, encoding, corruption
- ✅ **JSON support** with automatic parsing and formatting
- ✅ **Atomic writes** using temporary files
- ✅ **Retry logic** with exponential backoff
- ✅ **Operations logging** for debugging
- ✅ **Context managers** for safe file operations

### Installation

```bash
chmod +x resilient_file_handler.py
```

### Quick Start

**Basic File Operations:**
```python
from resilient_file_handler import ResilientFileHandler

handler = ResilientFileHandler(create_missing=True)

# Read with automatic fallback
content = handler.read_file('data.txt', default='Default content')

# Write with error handling
handler.write_file('output.txt', 'Hello, world!')

# Append safely
handler.append_file('log.txt', 'New log entry\n')
```

**JSON Operations:**
```python
# Read JSON with fallback
config = handler.read_json('config.json', default={'debug': False})

# Write JSON with formatting
handler.write_json('config.json', {'debug': True, 'port': 8080})
```

**Atomic Writes:**
```python
# Write is atomic - file appears fully written or not at all
with handler.atomic_write('important.txt') as f:
    f.write('Critical data')
    f.write('More critical data')
# File appears with all content or not at all
```

**Retry Logic:**
```python
# Retry on network filesystem glitches
def flaky_operation():
    return handler.read_file('/network/share/file.txt')

result = handler.with_retry(flaky_operation, max_retries=3, backoff=0.5)
```

### Usage Examples

#### Example 1: Configuration Management

```python
from resilient_file_handler import ResilientFileHandler

handler = ResilientFileHandler(create_missing=True, log_operations=True)

# Load config with defaults
config = handler.read_json('app_config.json', default={
    'api_url': 'https://api.example.com',
    'timeout': 30,
    'retry_count': 3
})

# Update config
config['last_run'] = '2025-01-05'
handler.write_json('app_config.json', config)
```

**Benefits:**
- App works even if config file is missing
- Creates sensible defaults automatically
- Handles permission errors gracefully
- Logs all operations for debugging

#### Example 2: Log File Management

```python
import datetime

handler = ResilientFileHandler(create_missing=True)

# Append to log (creates if missing)
timestamp = datetime.datetime.now().isoformat()
handler.append_file('app.log', f'[{timestamp}] Application started\n')

# Even if log file is corrupted or unreadable
logs = handler.read_file('app.log', default='')
print(f"Found {len(logs.splitlines())} log entries")
```

#### Example 3: Data Processing Pipeline

```python
handler = ResilientFileHandler(create_missing=True, log_operations=True)

# Process files that might be missing or corrupted
for filename in ['data1.json', 'data2.json', 'data3.json']:
    data = handler.read_json(filename, default=[])

    # Process data
    processed = [item for item in data if item.get('valid', False)]

    # Atomically write results
    output = filename.replace('.json', '_processed.json')
    handler.write_json(output, processed)
```

**Benefits:**
- Pipeline doesn't crash on missing files
- Corrupted files get replaced with defaults
- Atomic writes prevent partial data
- All operations are logged

#### Example 4: Network File Operations

```python
import time

handler = ResilientFileHandler()

# Read from network share with retry
def read_network_file():
    return handler.read_file('/mnt/network/shared/data.txt')

# Retry up to 3 times with exponential backoff
try:
    data = handler.with_retry(read_network_file, max_retries=3, backoff=0.5)
    print(f"Successfully read: {data}")
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Error Handling

The handler gracefully manages common errors:

| Error | Traditional | Resilient Handler |
|-------|-------------|-------------------|
| **FileNotFoundError** | Crash | Auto-create with default content |
| **PermissionError** | Crash | Return default, log warning |
| **UnicodeDecodeError** | Crash | Try binary mode with ignore |
| **json.JSONDecodeError** | Crash | Return default, log error |
| **OSError** (disk full) | Crash | Raise with context |

### API Reference

#### Class: `ResilientFileHandler`

**Constructor:**
```python
ResilientFileHandler(
    create_missing=False,  # Auto-create missing files
    default_encoding='utf-8',  # Default encoding
    log_operations=False  # Log all operations
)
```

**Methods:**

```python
# Basic operations
read_file(path, default=None) -> str
write_file(path, content, mode='w') -> bool
append_file(path, content) -> bool

# JSON operations
read_json(path, default=None) -> dict|list
write_json(path, data, indent=2) -> bool

# Advanced operations
atomic_write(path) -> ContextManager
with_retry(operation, max_retries=3, backoff=0.5) -> Any
```

**Convenience Functions:**
```python
# Quick helpers (no class needed)
safe_read(path, default='')
safe_write(path, content)
safe_read_json(path, default={})
safe_write_json(path, data)
```

---

## 🎨 PowerPoint Generator

### Features

- ✅ **AI-powered content generation** using Claude Sonnet 4.5
- ✅ **Multiple presentation styles** (professional, creative, minimal, corporate, educational)
- ✅ **Automatic file download** and management
- ✅ **Configurable slide count** or let Claude decide
- ✅ **Additional context** for specific requirements
- ✅ **CLI interface** for easy automation

### Prerequisites

```bash
# Install Anthropic SDK
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Quick Start

**Basic Presentation:**
```bash
python claude_skills_pptx.py "Introduction to Machine Learning"
```

**With Specific Options:**
```bash
python claude_skills_pptx.py "Quarterly Business Review" \
  --slides 10 \
  --style corporate \
  --output presentations/q4_review.pptx
```

### Usage Examples

#### Example 1: Educational Presentation

```bash
python claude_skills_pptx.py "Python Programming Basics" \
  --style educational \
  --slides 12 \
  --context "Include code examples, common pitfalls, and practice exercises"
```

**Output:**
- 12 slides with educational style
- Code examples on slides
- Common mistakes highlighted
- Practice exercises included
- Clean, student-friendly design

#### Example 2: Business Presentation

```bash
python claude_skills_pptx.py "Product Launch Strategy" \
  --style corporate \
  --slides 15 \
  --context "Include market analysis, competitive landscape, go-to-market timeline, and budget breakdown"
```

**Output:**
- 15 slides in corporate style
- Market analysis section
- Competitor comparison
- Launch timeline with milestones
- Budget breakdown tables
- Executive-ready formatting

#### Example 3: Creative Workshop

```bash
python claude_skills_pptx.py "Creative Brainstorming Workshop" \
  --style creative \
  --context "Use bold colors, include ice-breaker activities, and add visual thinking exercises"
```

**Output:**
- Vibrant, engaging design
- Ice-breaker slides
- Interactive activities
- Visual exercises
- Fun, approachable style

#### Example 4: Technical Deep Dive

```bash
python claude_skills_pptx.py "Kubernetes Architecture" \
  --style professional \
  --slides 20 \
  --context "Include architecture diagrams, component breakdown, deployment examples, and best practices"
```

**Output:**
- 20 technical slides
- System architecture visuals
- Component details
- Practical examples
- Best practices checklist

### Programmatic Usage

```python
from claude_skills_pptx import PowerPointGenerator

# Initialize
generator = PowerPointGenerator()

# Create presentation
result = generator.create_presentation(
    topic="Cloud Migration Strategy",
    slides=12,
    style="corporate",
    additional_context="Focus on AWS services, include cost analysis"
)

# Check result
if result["success"]:
    file_id = result["file_ids"][0]
    print(f"Presentation created: {file_id}")

    # Get file info
    info = generator.get_file_info(file_id)
    print(f"Filename: {info['filename']}")
    print(f"Size: {info['size'] / 1024:.1f} KB")

    # Download
    generator.download_file(file_id, "cloud_migration.pptx")
else:
    print("Failed to create presentation")
```

### Presentation Styles

| Style | Use Case | Design |
|-------|----------|--------|
| **professional** | Business meetings, client presentations | Clean, modern, corporate colors |
| **creative** | Workshops, brainstorming, team building | Bold colors, playful elements, engaging |
| **minimal** | Tech talks, product demos | Lots of white space, simple, focused |
| **corporate** | Executive presentations, board meetings | Formal, conservative, data-driven |
| **educational** | Training, tutorials, teaching | Clear explanations, examples, structured |

### CLI Options

```bash
python claude_skills_pptx.py [TOPIC] [OPTIONS]

Arguments:
  TOPIC                 Presentation topic or title

Options:
  --slides, -s N        Number of slides (Claude decides if not specified)
  --style STYLE         Presentation style (default: professional)
  --context, -c TEXT    Additional context or requirements
  --output, -o PATH     Output file path (default: topic_name.pptx)
  --no-download         Don't download, just show file ID
```

### Advanced Usage

**Custom Output Location:**
```bash
python claude_skills_pptx.py "Annual Report 2024" \
  --output "/mnt/shared/reports/annual_2024.pptx"
```

**Get File ID Only:**
```bash
python claude_skills_pptx.py "Team Meeting" --no-download
# Returns: File ID: file_abc123xyz
# Download later: client.beta.files.download(file_id="file_abc123xyz")
```

**Complex Requirements:**
```bash
python claude_skills_pptx.py "Security Audit Findings" \
  --style corporate \
  --slides 25 \
  --context "Include: Executive summary, vulnerability breakdown by severity, \
remediation timeline, compliance impact, resource requirements, and next steps"
```

### File Management

**Automatic Naming:**
```bash
python claude_skills_pptx.py "Introduction to Machine Learning"
# Creates: introduction_to_machine_learning.pptx
```

**Custom Naming:**
```bash
python claude_skills_pptx.py "Q4 Review" --output "2024_q4_review.pptx"
```

**File Information:**
The tool automatically displays:
- File ID for reference
- Original filename
- File size in KB
- Download location

---

## 🔧 Integration Patterns

### Pattern 1: Automated Reporting

```python
from claude_skills_pptx import PowerPointGenerator
from resilient_file_handler import ResilientFileHandler
import datetime

# Load report data
handler = ResilientFileHandler()
data = handler.read_json('quarterly_data.json', default={})

# Generate presentation
generator = PowerPointGenerator()
context = f"""
Include:
- Revenue: ${data.get('revenue', 0):,.2f}
- Growth: {data.get('growth', 0)}%
- Top products: {', '.join(data.get('top_products', []))}
- Key metrics and trends
"""

result = generator.create_presentation(
    topic=f"Q{data.get('quarter', 1)} {datetime.datetime.now().year} Report",
    slides=15,
    style="corporate",
    additional_context=context
)

if result["success"]:
    generator.download_file(
        result["file_ids"][0],
        f"reports/q{data.get('quarter', 1)}_report.pptx"
    )
```

### Pattern 2: Batch Presentation Generation

```python
from claude_skills_pptx import PowerPointGenerator
import time

generator = PowerPointGenerator()

topics = [
    ("Product Overview", "professional", 10),
    ("Technical Architecture", "minimal", 15),
    ("Team Training", "educational", 12)
]

for topic, style, slides in topics:
    print(f"Generating: {topic}")

    result = generator.create_presentation(
        topic=topic,
        slides=slides,
        style=style
    )

    if result["success"]:
        filename = topic.lower().replace(' ', '_') + '.pptx'
        generator.download_file(result["file_ids"][0], filename)
        print(f"✓ Created: {filename}")

    time.sleep(1)  # Rate limiting
```

### Pattern 3: Resilient Presentation Workflow

```python
from claude_skills_pptx import PowerPointGenerator
from resilient_file_handler import ResilientFileHandler

handler = ResilientFileHandler(create_missing=True, log_operations=True)
generator = PowerPointGenerator()

# Load config with fallback
config = handler.read_json('presentation_config.json', default={
    'style': 'professional',
    'slides': 10,
    'output_dir': 'presentations'
})

# Generate presentation
try:
    result = generator.create_presentation(
        topic=config.get('topic', 'Untitled Presentation'),
        slides=config.get('slides'),
        style=config.get('style')
    )

    if result["success"]:
        # Atomic write to log success
        output_path = f"{config['output_dir']}/{config.get('topic', 'untitled')}.pptx"
        generator.download_file(result["file_ids"][0], output_path)

        # Update log
        handler.append_file('generation_log.txt',
            f"{datetime.datetime.now()}: Created {output_path}\n")

except Exception as e:
    # Log error resiliently
    handler.append_file('error_log.txt',
        f"{datetime.datetime.now()}: Error: {e}\n")
```

---

## 🎯 Use Cases

### Use Case 1: Weekly Team Meetings

**Problem:** Manually creating meeting decks is time-consuming

**Solution:**
```bash
# Automated weekly deck generation
python claude_skills_pptx.py "Team Sync - Week $(date +%V)" \
  --style professional \
  --slides 8 \
  --context "Include: Last week recap, this week priorities, blockers, wins"
```

### Use Case 2: Client Deliverables

**Problem:** Need consistent, professional client presentations

**Solution:**
```bash
python claude_skills_pptx.py "Project Status Update" \
  --style corporate \
  --slides 12 \
  --context "Include: Progress summary, milestones achieved, upcoming deliverables, risk assessment, budget status"
```

### Use Case 3: Training Materials

**Problem:** Creating training decks from scratch is tedious

**Solution:**
```bash
python claude_skills_pptx.py "API Integration Workshop" \
  --style educational \
  --slides 15 \
  --context "Include: Step-by-step integration guide, code examples, common errors, troubleshooting tips"
```

### Use Case 4: Conference Talks

**Problem:** Need engaging presentation for tech conference

**Solution:**
```bash
python claude_skills_pptx.py "Scaling Microservices to 1M RPS" \
  --style minimal \
  --slides 20 \
  --context "Include: Architecture evolution, performance optimizations, lessons learned, live demo outline"
```

---

## 🐛 Troubleshooting

### Resilient File Handler

**Issue: Files still not being created**
```python
# Make sure create_missing=True
handler = ResilientFileHandler(create_missing=True)
```

**Issue: Unicode errors persist**
```python
# The handler tries binary mode automatically, but you can force it:
content = handler.read_file('file.txt', default='')
# Already handles UnicodeDecodeError internally
```

**Issue: Want to see what's happening**
```python
# Enable logging
handler = ResilientFileHandler(log_operations=True)
# Now all operations print to console
```

### PowerPoint Generator

**Issue: "API key not found"**
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or pass directly
generator = PowerPointGenerator(api_key="your-key-here")
```

**Issue: "No presentation file was generated"**
- Check Claude's response text for errors
- Try simplifying the topic
- Reduce additional context length
- Try a different style

**Issue: Download fails**
```python
# Get file ID and retry manually
file_id = result["file_ids"][0]
generator.download_file(file_id, "output.pptx")
```

**Issue: Presentation not what you expected**
```bash
# Be more specific in context
python claude_skills_pptx.py "Marketing Strategy" \
  --context "MUST include: competitor analysis table, 12-month timeline, budget breakdown by channel, success metrics"
```

---

## 📚 Best Practices

### Resilient File Handler

**DO:**
- ✅ Use `create_missing=True` for config files
- ✅ Always provide sensible defaults
- ✅ Enable logging during development
- ✅ Use atomic writes for critical data
- ✅ Use retry logic for network filesystems

**DON'T:**
- ❌ Rely on auto-create for data files (use for config only)
- ❌ Ignore the return value of write operations
- ❌ Use without defaults in production
- ❌ Skip validation of loaded data

### PowerPoint Generator

**DO:**
- ✅ Be specific in topic and context
- ✅ Choose appropriate style for audience
- ✅ Specify slide count for consistent results
- ✅ Include all requirements in context
- ✅ Use descriptive output filenames

**DON'T:**
- ❌ Use vague topics ("Presentation", "Meeting")
- ❌ Overload with too many requirements
- ❌ Forget to specify technical depth needed
- ❌ Use wrong style for audience (creative for executives)

---

## 🔗 Related Resources

**This Repository:**
- `README_THINKING_TOOLS.md` - Extended thinking with tools
- `README_ADVANCED_PATTERNS.md` - Metaprompt & orchestrator patterns
- `README_COMMIT_HELPER.md` - Commit message generation

**External:**
- [Anthropic Skills API](https://docs.anthropic.com/en/docs/build-with-claude/skills)
- [Python File I/O Best Practices](https://docs.python.org/3/tutorial/inputoutput.html)
- [Atomic File Operations](https://lwn.net/Articles/457667/)

---

## 🎯 Next Steps

1. **Try resilient file handling:**
   ```bash
   python resilient_file_handler.py
   ```

2. **Generate your first presentation:**
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   python claude_skills_pptx.py "Your Topic" --slides 10
   ```

3. **Integrate into workflows:**
   - Add to CI/CD for automated reports
   - Use in data pipelines for robust file handling
   - Create presentation generation APIs
   - Build batch processing scripts

---

**Build resilient systems! 🛡️📊**
