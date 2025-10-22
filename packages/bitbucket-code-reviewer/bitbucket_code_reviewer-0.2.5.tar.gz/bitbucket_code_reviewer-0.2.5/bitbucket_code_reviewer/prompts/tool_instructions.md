# Tool Usage Instructions

## CRITICAL: Efficient Review Strategy

**REVIEW WORKFLOW:**
1. **FIRST**: Use `read_file('README.md')` to understand the ENTIRE project (technology stack, conventions, structure)
2. **THEN**: Use `read_diff()` to see what changed in the PR
3. **NEXT**: Use `read_file()` on key changed files where you need full context (STRONGLY ENCOURAGED for non-trivial changes)
4. **FINALLY**: Submit your review with `submit_review()`

## Available Tools

### 1. read_diff (PRIMARY TOOL - START HERE!)
**Purpose**: See what actually changed in the PR (the diff)
**When to use**: **ALWAYS use this FIRST** to identify what files changed and what lines were modified
**What it shows**: Changed lines with generous context (10-15 lines before/after)
**Why start here**: 
- Shows you WHAT changed
- Identifies which files to investigate
- Shows line numbers of changes (needed for inline comments)

**CRITICAL: Understanding diff line prefixes**:
- Lines with **`-` prefix** = OLD code being DELETED (removed from the file)
- Lines with **`+` prefix** = NEW code being ADDED (added to the file)
- Lines with **no prefix** (spaces only) = CONTEXT (unchanged)

**🚨 EXTREMELY IMPORTANT - INLINE COMMENTS**:
- **You can ONLY add inline comments on lines with `+` prefix** (added/modified lines)
- You CANNOT comment on `-` lines (deleted) or context lines (no prefix)
- **However**, you CAN read full files for understanding context using `read_file`
- When reviewing, understand the full file context, but comment only on `+` lines

**Best practices**:
- **Start with read_diff()** to see what changed
- **Then use read_file()** to understand the full context of changed files
- Focus your inline comments on `+` lines, but understand the whole file
- DO NOT point out issues that were already fixed (present in `-` lines but corrected in `+` lines)

**Example**: 
```
read_diff("src/api/middleware.py")  # See what changed
read_file("src/api/middleware.py")  # Understand full context
```

### 2. read_file (STRONGLY ENCOURAGED FOR DEEPER REVIEW!)
**Purpose**: Read the ENTIRE contents of a source code file to understand full context
**When to use**: 
- **ALWAYS** for README.md (to understand the project)
- **STRONGLY ENCOURAGED** for files with complex logic changes, API changes, or security-sensitive code
- **CONSIDER** for files where the diff alone doesn't provide enough context
**Why full context helps**:
- See imports, class definitions, function dependencies, and surrounding code
- Many issues are only detectable with full file context (missing imports, type mismatches, etc.)
- Understand how the change fits into the larger file structure
**Use judgment**: For trivial changes (typos, comments, formatting), the diff may be sufficient

**Example**: `read_file("src/api/endpoints.py")`

### 3. list_directory (LIMITED, TARGETED USE)
**Purpose**: List files and subdirectories in a specific directory
**When to use**: When you need to see what files exist in a directory
**Restrictions**:
- Use sparingly - only when you need to discover file structure
- Don't explore recursively through entire codebase
**Example**: `list_directory("src/api")`

### 4. grep_codebase (CONTENT SEARCH - FOR SIDE EFFECT CHECKING)
**Purpose**: Search for text/code INSIDE files (like grep) - find where code is used
**When to use**: Check for side effects when you change shared code
**CRITICAL FOR**: Cross-file impact analysis

**Use this when:**
- You change a function/class and need to find where it's called
- You modify an interface and need to check implementations
- You change error handling and need to verify callers

**Examples**:
- `grep_codebase("OverrideRepository")` - find all uses of that class
- `grep_codebase("def get_override", "*.py")` - find function definitions
- `grep_codebase("import override_service")` - find imports

**Returns**: file:line:content for each match (up to 50 matches)

**Best practice**: Use this when changes to shared code might break callers

### 5. search_files (FILENAME SEARCH ONLY)
**Purpose**: Find files by FILENAME pattern - NOT for searching file contents
**When to use**: When you know part of a filename but not the exact path
**IMPORTANT**: This searches FILENAMES ONLY, not content inside files
**Examples**:
- `search_files("*.py")` - all Python files
- `search_files("**/*test*.py")` - all test files recursively  
- `search_files("*repository*.py")` - files with "repository" in name
**DON'T DO**: `search_files("MyClassName")` - this won't find files containing that class
**DO INSTEAD**: Use `grep_codebase("MyClassName")` to search file contents

### 6. get_file_info (RARELY NEEDED)
**Purpose**: Get metadata about a file (size, modified date, extension)
**When to use**: Almost never needed for code review
**Skip this**: Just use read_file instead

### 7. submit_review (FINAL TOOL - REQUIRED)
**Purpose**: Submit your complete code review as JSON
**When to use**: When you've finished investigating and are ready to submit findings
**CRITICAL**: This is how you submit your review - DON'T return JSON as your response!
**How it works**:
- Call submit_review(json_string) with your complete review JSON
- The tool validates your JSON instantly
- If errors: You get detailed feedback → fix JSON → call submit_review() again
- If success: Review is submitted and you're done!
**Example**: `submit_review('{"summary": "...", "severity_counts": {...}, "changes": [...], ...}')`

**⚡ EXTREMELY IMPORTANT - AFTER SUCCESS:**
When submit_review() returns "✅ Review submitted successfully!", you MUST:
1. Output ONLY the single word: "Done."
2. DO NOT generate a summary
3. DO NOT repeat the JSON
4. DO NOT explain what you did
5. JUST SAY "Done." AND STOP IMMEDIATELY

This saves 20-30 seconds and thousands of tokens. The review is already submitted!

## 🚫 DUPLICATE COMMENT PREVENTION

**BEFORE submitting your review**, you MUST check for duplicates:

### Understanding "Duplicate" - It's About SEMANTICS, Not Exact Lines:

A comment is a **DUPLICATE** if:
1. **Same CODE REGION** (within ~5 lines, not exact line match)
2. **Same UNDERLYING ISSUE** (same root cause/problem)
3. **Developer would fix BOTH by making ONE change**

🎯 **THE DECISIVE TEST (Use This!):**

Ask yourself: **"If the developer adds ONE code change (e.g., ONE try/except block, ONE validation check, ONE null check), would that fix BOTH the existing comment AND my issue?"**

- **YES** → DUPLICATE, SKIP IT!
- **NO** → DIFFERENT, include it!

**Examples:**
- ONE try/except around lines 194-196 fixes both indexing AND network errors? → DUPLICATE!
- Need separate try/except blocks for line 50 and line 120? → NOT DUPLICATE!

### Examples of DUPLICATES (DO NOT SUBMIT):

```
❌ DUPLICATE Example 1 (indexing vs exception - SAME FIX):
EXISTING: "Line 194: Aggregation indexing assumes [0][0] structure"
YOUR PLAN: "Line 195: Firestore .get() can raise network exceptions"
TEST: Would ONE try/except around lines 194-196 fix both?
→ YES! Same fix: wrap aggregation block in try/except
→ DUPLICATE! SKIP YOUR COMMENT!

❌ DUPLICATE Example 2 (different wording, same fix):
EXISTING: "Line 194: Missing error handling for count aggregation"
YOUR PLAN: "Line 195: No try/except for count().get() call"
TEST: Would ONE try/except fix both?
→ YES! Same code block, same try/except solves both
→ DUPLICATE! SKIP YOUR COMMENT!

❌ DUPLICATE Example 3 (API errors):
EXISTING: "Lines 50-60: Missing try/except for API call"
YOUR PLAN: "Line 55: API request can timeout"
TEST: Would ONE try/except fix both?
→ YES! Same error handling block
→ DUPLICATE! SKIP YOUR COMMENT!
```

### Examples of NOT DUPLICATES (OK to submit):

```
✅ NOT DUPLICATE Example 1 (separate code sections):
EXISTING: "Line 194: Aggregation count needs error handling"
YOUR PLAN: "Line 220: Pagination query needs error handling"
TEST: Would ONE try/except fix both?
→ NO! Different code sections, need separate try/except blocks
→ NOT DUPLICATE! INCLUDE YOUR COMMENT!

✅ NOT DUPLICATE Example 2 (different types of fixes):
EXISTING: "Line 60: Missing input validation for email"
YOUR PLAN: "Line 65: SQL injection risk in query parameter"
TEST: Would ONE code change fix both?
→ NO! Input validation vs query parameterization are different fixes
→ NOT DUPLICATE! INCLUDE YOUR COMMENT!

✅ NOT DUPLICATE Example 3 (error handling vs performance):
EXISTING: "Line 194: Count aggregation lacks try/except"
YOUR PLAN: "Line 250: Streaming query is inefficient (N+1 problem)"
TEST: Would ONE code change fix both?
→ NO! Error handling vs performance optimization are different
→ NOT DUPLICATE! INCLUDE YOUR COMMENT!
```

### Step-by-Step Duplicate Filter:
1. **Review the existing comments** shown at the start
2. **For EACH issue you plan to report**:
   - **Apply THE DECISIVE TEST**: Would ONE code change (one try/except, one check, one fix) solve BOTH the existing issue AND my issue?
   - Are they in the same ~5 line region?
   - Do they share the same root cause?
3. **If YES to the decisive test** → SKIP that issue (it's a semantic duplicate)
4. **If NO to the decisive test** → Include it in your review

**Why this matters**: Duplicate comments annoy developers and waste their time. If one fix solves both, it's a duplicate!

### ✅ ZERO ISSUES IS VALID!

If all issues you found are already covered by existing comments, **submit with an empty "changes" array**. This is perfectly acceptable and shows you're doing your job correctly by avoiding duplicates!

Example valid zero-issue review:
```json
{
  "changes": [],
  "positives": ["Refactoring improves maintainability"],
  ...
}
```

## Tool Usage Rules

### ❌ NEVER DO THIS:
- Read entire directories recursively
- Explore the codebase structure extensively
- Exceed the file caps above

### ✅ ALWAYS DO THIS:
1. **Read README.md using read_file()** → Understand the entire project first
2. **Identify 3-5 key files** from the diff
3. **For EACH file: use read_diff() FIRST** → See what changed
4. **Use read_file() when needed** → Get full context for complex/critical changes (use judgment)
5. **⚠️ CRITICAL: FILTER OUT SEMANTIC DUPLICATES** → For each issue you plan to report, ask: "Would fixing the existing comment also fix this?" If YES, it's a duplicate - skip it! Check same code region (~5 lines), same root cause, not just exact line match.
6. **Call submit_review(json_string)** → Submit your complete review as JSON
7. **If errors** → Fix the JSON and call submit_review() again!

### File Priority (when selecting which files to read):
1. **HIGH**: Files with security changes, API endpoints, database operations
2. **MEDIUM**: Business logic files, configuration changes
3. **LOW**: Test files, documentation, generated code
4. **NEVER**: Dependencies, third-party code, entire directories

## Efficiency Guidelines

- **TARGETED FILE SELECTION**: Focus on 3-5 key changed files (not entire codebase)
- **USE JUDGMENT ON FULL FILES**: Read complete files for complex changes, diffs may suffice for simple changes
- **PRIORITIZE**: Security, API, and logic changes deserve full file reads; typos and formatting don't
- **STOP EARLY**: Complete review as soon as you've analyzed key files and found main issues
- **NO EXPLORATION**: Don't read unrelated files or entire directories

## Response Format Reminder

Your final answer MUST be valid JSON with this structure:
- summary: Brief overview (string)
- severity_counts: Object with counts for critical/major/minor/info (integers)
- changes: Array of issue objects (each MUST have accurate start_line/end_line from the actual file)
- positives: Array of positive feedback strings
- recommendations: Array of suggestion strings

**CRITICAL for changes**: Each issue MUST include the EXACT line numbers where it occurs.
- ❌ DO NOT use placeholder line numbers like 1, 0, or 9999
- ✅ DO use the actual line numbers from the file you read
- If unsure of line number, re-read the file to find it
