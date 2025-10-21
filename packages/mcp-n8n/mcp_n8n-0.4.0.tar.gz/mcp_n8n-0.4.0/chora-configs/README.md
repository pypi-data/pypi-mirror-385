# chora-configs Directory

This directory contains chora-compose templates and content configurations for mcp-n8n workflows.

## Directory Structure

```
chora-configs/
├── templates/          # Jinja2 templates for content generation
│   └── daily-report.md.j2
├── content/            # Content configuration files
│   └── daily-report.json
└── README.md           # This file
```

## Purpose

Following the [n8n-chora-compose-integration architecture](../docs/architecture/n8n-chora-compose-integration.md), templates and configs belong in the **project repository** (mcp-n8n), NOT in the chora-compose repository.

**Key Principle:** chora-compose is a **template engine** (like Jinja2/Flask), not a template library. Each project maintains its own templates.

## How chora-compose Discovers These Configs

chora-compose discovers configs from the project's working directory. Configure in Claude Desktop:

```json
{
  "mcpServers": {
    "chora-compose": {
      "command": "python",
      "args": ["-m", "chora_compose.mcp.server"],
      "cwd": "/absolute/path/to/mcp-n8n",  // Points to mcp-n8n root
      "env": {}
    }
  }
}
```

chora-compose will then load:
- Templates from: `/absolute/path/to/mcp-n8n/chora-configs/templates/`
- Content configs from: `/absolute/path/to/mcp-n8n/chora-configs/content/`

**Note:** The directory is named `chora-configs/` but chora-compose may expect `configs/`. If templates aren't discovered, create a symlink:

```bash
ln -s chora-configs configs
```

## Available Templates

### daily-report.md.j2

Generates daily engineering reports with git commits and gateway events.

**Usage:**
```python
result = await backend.call_tool("generate_content", {
    "content_config_id": "daily-report",
    "context": {
        "date": "2025-10-20",
        "generated_at": "2025-10-20T10:00:00Z",
        "since_hours": 24,
        "commits": [
            {
                "hash": "abc123...",
                "author": "Alice",
                "message": "feat: add feature",
                "timestamp": "2025-10-20T09:00:00Z"
            }
        ],
        "events": [...],
        "stats": {
            "total_events": 50,
            "tool_calls": 30,
            "success_rate": 90.0,
            ...
        }
    },
    "force": True
})
```

**Output:** Markdown report in `ephemeral/daily-report/<timestamp>.md`

## Creating New Templates

### 1. Create Jinja2 Template

Create `templates/my-report.md.j2`:

```jinja2
# My Report - {{ date }}

{% for item in items %}
- {{ item.name }}: {{ item.value }}
{% endfor %}
```

### 2. Create Content Config

Create `content/my-report.json`:

```json
{
  "type": "content",
  "id": "my-report",
  "schemaRef": {"id": "content-schema", "version": "3.1"},
  "metadata": {
    "description": "My custom report",
    "version": "1.0.0",
    "output_format": "markdown"
  },
  "generation": {
    "patterns": [{
      "id": "my-report-generation",
      "type": "jinja2",
      "template": "my-report.md.j2",
      "generation_config": {
        "context": {
          "date": {"source": "runtime", "required": true},
          "items": {"source": "runtime", "required": true, "type": "array"}
        }
      }
    }]
  }
}
```

### 3. Use in Workflow

```python
result = await backend.call_tool("generate_content", {
    "content_config_id": "my-report",
    "context": {
        "date": "2025-10-20",
        "items": [{"name": "foo", "value": "bar"}]
    }
})
```

## Template Best Practices

1. **Validate Input:** Use Jinja2 filters and conditionals to handle missing data gracefully
   ```jinja2
   {% if items %}
   ...
   {% else %}
   *No items available*
   {% endif %}
   ```

2. **Format Data:** Use Jinja2 filters for formatting
   ```jinja2
   {{ timestamp | datetimeformat('%Y-%m-%d %H:%M') }}
   {{ duration_ms | round(2) }}ms
   {{ items | length }} items
   ```

3. **Keep Templates Readable:** Break complex logic into separate templates and use `{% include %}`
   ```jinja2
   {% include 'partials/header.md.j2' %}
   ```

4. **Document Context:** Specify required context fields in content config

5. **Version Templates:** Use semantic versioning in metadata

## Testing Templates

Test templates locally before using in workflows:

```python
# In Python console or script
from mcp_n8n.backends import get_registry

registry = get_registry()
backend = registry.get_backend_by_namespace("chora")

result = await backend.call_tool("generate_content", {
    "content_config_id": "daily-report",
    "context": {...},  # Test context
    "force": True
})

print(result["content"])
```

## Related Documentation

- [n8n + chora-compose Integration](../docs/architecture/n8n-chora-compose-integration.md) - Architecture overview
- [chora-compose Documentation](https://github.com/liminalcommons/chora-compose) - Official chora-compose docs
- [Sprint 5 Intent](../docs/change-requests/sprint-5-workflows/intent.md) - Sprint 5 goals and design

---

**Note:** This directory is project-specific. Do NOT submit templates to chora-compose repository. Templates belong here.
