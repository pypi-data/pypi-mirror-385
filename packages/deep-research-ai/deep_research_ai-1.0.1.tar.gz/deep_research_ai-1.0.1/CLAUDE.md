# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MCP Server for Deep Research** is a Model Context Protocol (MCP) server that provides an AI-powered research tool called `start_deep_research`. It conducts comprehensive, multi-layered research on complex topics with adaptive methodology, critical analysis, and publication-quality report generation.

### Key Tech Stack
- **Language**: Python 3.10+
- **Package Manager**: `uv` (fast Python package manager)
- **MCP Protocol**: `mcp>=1.0.0` (Model Context Protocol)
- **Build System**: Hatchling
- **Entry Point**: Runs via Claude Desktop as an MCP server
- **Current Version**: 1.0.0 (Production Release)

## Common Development Commands

### Setup & Dependencies
```bash
# Install dependencies using uv
uv sync

# Create virtual environment
uv venv
```

### Running & Testing
```bash
# Run the server directly (for development/debugging)
uv run deepresearch

# Test with MCP Inspector (Node.js required)
npx @modelcontextprotocol/inspector uv --directory . run deepresearch
```

### Building & Publishing
```bash
# Build source and wheel distributions
uv build

# Publish to PyPI (requires auth)
uv publish
```

## Architecture Overview

### Core Design Pattern
This is an **MCP server** that exposes tools and prompts to Claude Desktop via the Model Context Protocol using stdio transport.

### Key Components

**1. `server.py` (main entry point - ~480 lines)**
   - **ResearchProcessor class**: Manages research state (question, elaboration, subquestions, findings, final report) and maintains research notes
   - **PROMPT_TEMPLATE**: Comprehensive research methodology (5 steps: understand question → break into subquestions → research each → analyze → generate report)
   - **MCP Server handlers**:
     - `list_resources()`: Exposes `research://notes` and `research://data`
     - `read_resource()`: Returns notes as text or data as JSON
     - `list_prompts()`: Exposes `deep-research` prompt with `research_question` argument
     - `get_prompt()`: Returns formatted PROMPT_TEMPLATE with research question injected
     - `list_tools()`: Exposes `start_deep_research` tool
     - `call_tool()`: Executes tool by returning the PROMPT_TEMPLATE

**2. Research Methodology (embedded in PROMPT_TEMPLATE)**
   - **Step 1**: Analyze the research question for clarity, complexity (Simple/Moderate/Complex/Highly Complex), and relevant perspectives
   - **Step 2**: Decompose into 3-8 subquestions based on complexity
   - **Step 3**: Research each subquestion with three progressive layers:
     - Layer 1 (Overview): Foundational searches for all questions
     - Layer 2 (Deep Dive): Focused investigation for moderate+ complexity
     - Layer 3 (Expert Analysis): Frontier research for complex+ topics
   - **Step 4**: Analyze findings with critical frameworks (evidence mapping, bias assessment, hypothesis testing)
   - **Step 5**: Generate structured report with 10+ sections (executive summary, introduction, findings per subquestion, critical analysis, synthesis, conclusions, recommendations, limitations, references, glossary)

**3. Report Structure**
   - **Executive Summary** (200-300 words): Standalone overview
   - **Methodology**: Complexity justification and framework selection
   - **Findings**: Detailed subsections per subquestion with evidence credibility ratings
   - **Critical Analysis**: Evidence strength, logical coherence, bias evaluation
   - **Synthesis & Discussion**: Interdisciplinary patterns and emergent insights
   - **Conclusions**: Direct answers with confidence levels (HIGH/MODERATE/LOW/SPECULATIVE)
   - **Recommendations**: Stakeholder-specific actionable guidance
   - **Research Limitations**: Transparent constraints
   - **Further Research**: Knowledge gaps and future directions
   - **References**: Comprehensive citations
   - **Appendices**: Glossary and supplementary data

### Data Flow
1. User calls `start_deep_research` tool with a research question
2. Tool handler updates `ResearchProcessor` state and returns PROMPT_TEMPLATE
3. Claude receives the prompt and follows the methodology
4. Claude uses Claude's built-in search capabilities to research each subquestion
5. Claude synthesizes findings into a structured report (typically output as artifact)
6. Research notes/data remain accessible via resources for iterative refinement

## Important Architectural Notes

### How the Tool Works
- The `start_deep_research` tool doesn't perform research itself—it returns a **structured prompt template** that guides Claude through the research process
- Claude then executes the methodology using its own web search and reasoning capabilities
- This approach keeps the MCP server lightweight while leveraging Claude's powerful research capabilities

### Quality Features
- **Adaptive complexity assessment**: Simple questions get 3-4 subquestions, highly complex get 8+
- **Multiple analysis frameworks**: Tool description lists 9+ frameworks (SWOT, PEST, 5W2H, Comparative Analysis, Trend Analysis, Case Study, Stakeholder Analysis, Evidence Pyramid, Systems Thinking)
- **Credibility & evidence grading**: Source credibility (High/Medium/Low) and evidence strength (Strong/Moderate/Weak/Speculative)
- **Confidence levels**: All conclusions tagged with confidence (HIGH/MODERATE/LOW/SPECULATIVE)
- **Source evaluation**: Authority, recency, and bias assessment
- **Ethical research standards**: Proper citations, paraphrasing, avoiding plagiarism, presenting multiple viewpoints

## Key Files

- `src/mcp_server_deep_research/server.py`: Main MCP server with all handlers and research methodology
- `src/mcp_server_deep_research/__init__.py`: Package entry point that calls `server.main()`
- `pyproject.toml`: Project metadata, dependencies, build config
- `setup.py`: Installation script with Claude Desktop configuration setup
- `README.md`: User documentation with examples and usage instructions
- `CHANGELOG.md`: Version history and feature timeline

## Adding Features or Making Changes

### Modifying the Research Methodology
Edit the `PROMPT_TEMPLATE` constant in `server.py`. The template is the "brain" of the system—any changes here affect how Claude conducts research.

### Adding New Tools or Prompts
1. Add new enum values to `DeepResearchPrompts` and `PromptArgs`
2. Add handler in `list_prompts()` and `get_prompt()` for prompts, or `list_tools()` and `call_tool()` for tools
3. Update handlers with logic to generate appropriate templates/outputs

### Changing State Management
The `ResearchProcessor` class stores all research state. Modify its `research_data` dictionary structure and methods as needed. Current structure includes: question, elaboration, subquestions, search_results, extracted_content, final_report.

### Distribution
When publishing updates:
1. Update version in `pyproject.toml` and `setup.py`
2. Update `CHANGELOG.md` with changes
3. Run `uv build` to create distributions
4. Run `uv publish` to publish to PyPI

## Testing & Validation

The project includes example test cases in README.md for:
- **Simple questions** (3-4 subquestions, Layer 1 only)
- **Moderate questions** (5-6 core + 2-3 deep-dive, Layer 1+2)
- **Complex questions** (6-7 core + 3-5 deep-dive, all layers with multiple frameworks)

Test by invoking the tool with different complexity questions and verifying:
1. Report structure matches specification
2. Evidence is properly cited
3. Confidence levels are assigned
4. Analysis covers all perspectives
5. Methodology matches stated complexity

## Configuration Notes

### Claude Desktop Integration
The server integrates with Claude Desktop via MCP. Configuration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Config entry (development):
```json
{
  "mcpServers": {
    "deepresearch": {
      "command": "uv",
      "args": ["--directory", "/path/to/repo", "run", "deepresearch"]
    }
  }
}
```

Config entry (published/PyPI - v1.0.0+):
```json
{
  "mcpServers": {
    "deepresearch": {
      "command": "uvx",
      "args": ["--from", "deep-research-ai", "deepresearch"]
    }
  }
}
```

This automatically installs and runs the latest version from PyPI.

## Dependencies

- `mcp>=1.0.0`: Model Context Protocol implementation
- Python 3.10+: Core language requirement
- `pydantic`: Type validation (via MCP)
- `hatchling`: Build backend

No external web search dependencies—leverages Claude's built-in search capabilities.
