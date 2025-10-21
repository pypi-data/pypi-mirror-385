# Output Format Instructions

## Response Format Specification

You MUST respond with valid JSON containing exactly these fields:

**REQUIRED FIELDS:**
- **severity_counts**: Object with four integer counts: critical, major, minor, info
- **changes**: Array of issue objects (each with: file_path, line, severity, category, title, description, suggestion, code_snippet, suggested_code, rationale)

**VALID SEVERITY VALUES:** "critical", "major", "minor", "info"
**VALID CATEGORY VALUES:** "security", "performance", "maintainability", "architecture", "style"

**EXAMPLE STRUCTURE:**
```json
{
  "severity_counts": {
    "critical": 0,
    "major": 1,
    "minor": 2,
    "info": 0
  },
  "changes": [
    {
      "file_path": "path/to/file.py",
      "line": 42,
      "severity": "major",
      "category": "security",
      "title": "Missing input validation",
      "description": "User input is not validated before use",
      "suggestion": "Add input validation before processing",
      "code_snippet": "value = request.data['key']",
      "suggested_code": "value = validate_input(request.data.get('key', ''))",
      "rationale": "Prevents injection attacks and handles missing keys"
    }
  ]
}
```

## Important Notes
- Respond with **raw JSON only** - no markdown, no explanations
- Use the exact field names and types specified in the schema
- changes array can be empty if no issues found
- All severity counts should be integers (0 or higher)
- Focus only on REAL ISSUES that need fixing, not descriptions of what was done

