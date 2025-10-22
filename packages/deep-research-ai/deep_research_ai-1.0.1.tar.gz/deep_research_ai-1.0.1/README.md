# MCP Server for Deep Research

MCP Server for Deep Research is a powerful tool designed for conducting comprehensive research on complex topics. It helps you explore questions in depth, find relevant sources, and generate structured research reports with proper citations.

🔬 Your personal AI Research Assistant - turning complex research questions into comprehensive, well-cited reports.

## ✨ What's New

### Latest Release: Academic Citations Update (v1.0.1)

Enhanced with academic-standard footnote citation system for professional research reports.

#### 📚 Academic Footnote Citations (v1.0.1)
- **Numbered References**: All citations use [1], [2], [3] format in text
- **First Appearance Numbering**: Sources assigned numbers when first cited
- **Organized References**: Complete source list with corresponding numbers
- **Academic Standard**: Follows scholarly publication citation conventions

#### 🎯 Intelligent Complexity Assessment
- Automatically evaluates question complexity (Simple/Moderate/Complex/Highly Complex)
- Dynamically adjusts research depth and methodology based on complexity
- Scales from quick comparisons to comprehensive multi-disciplinary analyses

#### 📊 Multi-Layer Progressive Research
- **Layer 1 (Overview)**: Foundational understanding for all questions
- **Layer 2 (Deep Dive)**: Focused investigation for moderate+ complexity
- **Layer 3 (Expert Analysis)**: Cutting-edge insights for complex topics

#### 🌳 Dynamic Hierarchical Subquestions
- **Adaptive quantity**: 3-4 questions (simple) → 7-8+ questions (highly complex)
- **Tree structure**: Core questions with secondary deep-dive sub-questions
- **Priority tagging**: High/Medium/Low with dependency mapping

#### 🔍 Critical Analysis Framework
- **Source Credibility Assessment**: Authority, recency, bias evaluation
- **Evidence Quality Grading**: Strong/Moderate/Weak/Speculative classifications
- **Viewpoint Comparison**: Mainstream vs. alternative perspectives
- **Logical Coherence Checking**: Causation vs. correlation, assumption identification
- **Hypothesis Testing**: Formulate and evaluate testable hypotheses

#### 🛠️ Professional Analysis Frameworks
Choose from 9+ structured methodologies:
- SWOT Analysis (strategic evaluation)
- PEST/PESTEL Analysis (macro-environmental factors)
- 5W2H Framework (diagnostic deep-dive)
- Comparative Analysis (multi-dimensional comparison)
- Trend Analysis (historical → present → future)
- Case Study Method (learn from examples)
- Stakeholder Analysis (perspective mapping)
- Evidence Pyramid (scientific rigor)
- Systems Thinking (interconnections and feedback loops)

#### 🌐 Interdisciplinary Synthesis
- Tags questions with relevant disciplines: Technical, Economic, Social, Ethical, Legal, Scientific, Historical
- Identifies cross-perspective patterns and tensions
- Generates emergent insights from integrated analysis

#### 📄 Publication-Quality Reports
Enhanced structure with:
- **Executive Summary** (200-300 words)
- **Methodology Section** (framework justification)
- **Critical Analysis** (separate from findings)
- **Synthesis & Discussion** (interdisciplinary integration)
- **Confidence Levels** (HIGH/MODERATE/LOW/SPECULATIVE)
- **Research Limitations** (transparent acknowledgment)
- **Recommendations** (stakeholder-specific actions)
- **Further Research Directions**
- **Glossary** (technical terms)
- **Supplementary Data** (tables, charts)

#### ✅ Enhanced Quality Standards
- Evidence mapping with strength ratings
- Bias and limitation assessment
- Confidence level assignment for all conclusions
- Proper academic-style citations
- Acknowledgment of uncertainty and knowledge boundaries

---

### Core Features (All Versions)
- 🛠️ **Direct Tool Access**: Call the `start_deep_research` tool directly from Claude Desktop
- 📊 **Structured Research Workflow**: Guided process from question elaboration to final report
- 🌐 **Web Search Integration**: Leverages Claude's built-in search capabilities
- 📝 **Professional Reports**: Generates well-formatted research reports as artifacts

## 🚀 Quick Start

### Prerequisites
- [Claude Desktop](https://claude.ai/download)
- Python 3.10 or higher
- `uv` package manager

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/lihongwen/deepresearch-mcpserver.git
   cd deepresearch-mcpserver
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure Claude Desktop**
   
   Edit your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   
   Add the following configuration:
   ```json
   {
     "mcpServers": {
       "deepresearch": {
         "command": "uvx",
         "args": [
           "--from",
           "deep-research-ai@latest",
           "deepresearch"
         ]
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Start Researching**
   - Use the prompt template: "Start deep research on [your question]"
   - Or call the `start_deep_research` tool directly
   - Watch as Claude conducts comprehensive research and generates a detailed report

## 🎯 Complete Research Workflow

The Deep Research MCP Server offers a sophisticated 5-phase research methodology:

### Phase 1: **Preliminary Analysis & Research Design**
   - **Conceptual Clarification**: Defines key terms with precision
   - **Domain Mapping**: Identifies primary knowledge domains and intersections
   - **Stakeholder Identification**: Maps who cares about this question and why
   - **Complexity Assessment**: Evaluates as Simple/Moderate/Complex/Highly Complex
   - **Strategy Selection**: Chooses appropriate analytical frameworks and research depth

### Phase 2: **Hierarchical Question Decomposition**
   - **Dynamic Subquestion Generation**: Creates 3-8 questions based on complexity
   - **Tree Structure**: Core questions with secondary deep-dive sub-questions
   - **Quality Criteria**: Specific, focused, collectively exhaustive, mutually exclusive
   - **Priority & Dependencies**: Tags questions with importance and relationships
   - **Interdisciplinary Tagging**: Labels questions with relevant disciplinary perspectives

### Phase 3: **Layered Information Gathering**
   - **Layer 1 (Overview)**: Broad searches, credibility assessment, evidence classification
   - **Layer 2 (Deep Dive)**: Focused searches, comparative analysis, pattern identification
   - **Layer 3 (Expert Analysis)**: Frontier research, expert discourse, future trajectories
   - **Source Credibility Ratings**: High/Medium/Low based on authority, recency, bias
   - **Evidence Classification**: Strong/Moderate/Weak/Speculative based on rigor

### Phase 4: **Critical Analysis & Synthesis**
   - **Evidence Mapping**: Central claims, supporting/contradicting evidence, gaps
   - **Logical Coherence Check**: Causation vs. correlation, reasoning validity
   - **Bias Assessment**: Selection, confirmation, temporal, publication bias
   - **Hypothesis Testing**: Formulate, evaluate, conclude (Supported/Partial/Not Supported)
   - **Confidence Levels**: Assign HIGH/MODERATE/LOW/SPECULATIVE to conclusions
   - **Interdisciplinary Synthesis**: Cross-perspective patterns, emergent insights, systems understanding

### Phase 5: **Comprehensive Report Generation**
   - **Executive Summary**: 200-300 word standalone overview
   - **Table of Contents**: Auto-generated navigation
   - **Introduction**: Context, importance, scope, key concepts
   - **Methodology**: Complexity rationale, framework selection, limitations
   - **Findings**: Detailed subsections per subquestion with evidence ratings
   - **Critical Analysis**: Evidence strength, contradictions, bias evaluation
   - **Synthesis & Discussion**: Integrated insights, patterns, contextual factors
   - **Conclusions**: Direct answers with confidence levels and implications
   - **Recommendations**: Stakeholder-specific actionable guidance
   - **Research Limitations**: Transparent acknowledgment of constraints
   - **Further Research**: Identified knowledge gaps and future directions
   - **References**: Comprehensive citations with proper formatting
   - **Appendices**: Glossary of terms, supplementary data

## 💡 Usage Examples

### Simple Question
```
User: "Start deep research on: What is the difference between REST and GraphQL APIs?"

Claude will:
1. Assess as SIMPLE complexity → Layer 1 research only
2. Generate 3-4 focused subquestions (characteristics, use cases, trade-offs)
3. Select Comparative Analysis framework
4. Perform targeted searches with credibility assessment
5. Generate concise report with comparison table
```

### Moderate Question
```
User: "Start deep research on: What are the applications and challenges of blockchain in supply chain management?"

Claude will:
1. Assess as MODERATE complexity → Layer 1 + Layer 2 research
2. Generate 5-6 core + 2-3 deep-dive subquestions
3. Select SWOT Analysis + Case Study Method + Trend Analysis
4. Perform overview AND focused deep-dive searches
5. Include critical analysis of evidence quality
6. Generate comprehensive report with multiple case studies and confidence levels
```

### Complex Question
```
User: "Start deep research on: How does climate change impact global food security, and what are effective adaptation strategies?"

Claude will:
1. Assess as COMPLEX → Layer 1 + Layer 2 + Layer 3 research
2. Generate 6-7 core + 3-5 deep-dive subquestions with dependencies
3. Select Systems Thinking + PEST + Stakeholder Analysis + Comparative Analysis
4. Tag with multiple disciplines: Scientific, Economic, Social, Political, Ethical
5. Perform overview + focused + expert-level research
6. Include hypothesis testing (e.g., "Climate-resilient crops maintain yields under 2°C warming")
7. Generate publication-quality report with executive summary, methodology justification, 
   critical analysis, interdisciplinary synthesis, stakeholder recommendations, 
   research limitations, and glossary
```

## 🔧 How It Works

1. **Call the Tool**: Invoke `start_deep_research` with your research question
2. **Follow the Workflow**: Claude follows a structured research process
3. **Review the Report**: Get a comprehensive report as an artifact
4. **Cite Sources**: All information is properly cited with source URLs

## 📦 Components

### Tools
- **start_deep_research**: Initiates a comprehensive research workflow on any topic
  - Input: `research_question` (string)
  - Output: Structured research guidance and workflow

### Prompts
- **deep-research**: Pre-configured prompt template for starting research tasks

### Resources
- Dynamic research state tracking
- Progress notes and findings storage

## ⚙️ Configuration

### Claude Desktop Config Locations
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Development Setup (Local)
```json
{
  "mcpServers": {
    "deepresearch": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourUsername\\path\\to\\deepresearch-mcpserver",
        "run",
        "deepresearch"
      ]
    }
  }
}
```

### Production Setup (Published)
If published to PyPI (recommended):
```json
{
  "mcpServers": {
    "deepresearch": {
      "command": "uvx",
      "args": [
        "--from",
        "deep-research-ai@latest",
        "deepresearch"
      ]
    }
  }
}
```

Note: Using `@latest` ensures you always get the newest version.

## 🛠️ Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/lihongwen/deepresearch-mcpserver.git
cd deepresearch-mcpserver

# Install dependencies
uv sync

# Run in development mode
uv run deepresearch
```

### Testing
```bash
# Install the MCP Inspector for testing
npx @modelcontextprotocol/inspector uv --directory . run deepresearch
```

### Building and Publishing
1. **Sync Dependencies**
   ```bash
   uv sync
   ```

2. **Build Distributions**
   ```bash
   uv build
   ```
   Generates source and wheel distributions in the `dist/` directory.

3. **Publish to PyPI** (if you have publishing rights)
   ```bash
   uv publish
   ```

### Project Structure
```
deepresearch-mcpserver/
├── src/
│   └── mcp_server_deep_research/
│       ├── __init__.py
│       └── server.py           # Main MCP server implementation
├── pyproject.toml              # Project configuration
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🐛 **Report Bugs**: Open an issue describing the bug
2. 💡 **Suggest Features**: Share your ideas for improvements
3. 🔧 **Submit Pull Requests**: Fix bugs or add features
4. 📖 **Improve Documentation**: Help make the docs better

### Contribution Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Write clear commit messages

## 📝 Changelog

### Version 1.0.1 (Latest) - Academic Citations Update

**📚 Enhanced Citation System**

- ✅ Academic-standard footnote citations with [1], [2], [3] format
- ✅ Numbered references in order of first appearance
- ✅ Organized REFERENCES section with corresponding numbers
- ✅ Enhanced citation examples and formatting guidelines
- ✅ Improved research report readability and professionalism

### Version 1.0.0 - Production Release

**🎉 Official Release - Ready for Production Use**

- ✅ Stable API and methodology proven in real-world research scenarios
- ✅ Complete documentation and CLAUDE.md for developer guidance
- ✅ Comprehensive test cases for all complexity levels
- ✅ Ready for enterprise deployment and integration
- ✅ Published to PyPI for easy installation via `uvx --from deep-research-ai deepresearch`

### Version 0.2.0 - Major Research Methodology Overhaul
- ✅ **Intelligent Complexity Assessment**: Automatic evaluation and adaptive methodology
- ✅ **Multi-Layer Progressive Research**: 3-tier depth system (Overview/Deep-Dive/Expert)
- ✅ **Dynamic Hierarchical Subquestions**: 3-8 questions based on complexity with tree structure
- ✅ **Critical Analysis Framework**: Source credibility, evidence grading, bias assessment, hypothesis testing
- ✅ **9+ Analytical Frameworks**: SWOT, PEST, 5W2H, Comparative, Trend, Case Study, Stakeholder, Evidence Pyramid, Systems Thinking
- ✅ **Interdisciplinary Synthesis**: Multi-perspective analysis with cross-domain insights
- ✅ **Publication-Quality Reports**: Executive summary, methodology, critical analysis, limitations, recommendations, glossary
- ✅ **Confidence Level System**: HIGH/MODERATE/LOW/SPECULATIVE ratings for all conclusions
- ✅ **Enhanced Evidence Standards**: Credibility ratings, evidence classification, citation requirements
- ✅ **Comprehensive Testing Guide**: Test cases for Simple/Moderate/Complex/Highly Complex questions

### Version 0.1.0 - Initial Release
- ✅ Added `start_deep_research` tool for direct invocation
- ✅ Enhanced research workflow with structured prompts
- ✅ Improved error handling and logging
- ✅ Updated documentation with examples

## 🙏 Acknowledgments

This project is based on the original [mcp-server-deep-research](https://github.com/reading-plus-ai/mcp-server-deep-research) by reading-plus-ai.

Special thanks to:
- Anthropic for the MCP protocol and Claude AI
- The open-source community for inspiration and support

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/lihongwen/deepresearch-mcpserver
- **Issues**: https://github.com/lihongwen/deepresearch-mcpserver/issues
- **MCP Protocol**: https://modelcontextprotocol.io
- **Claude Desktop**: https://claude.ai/download

---

**Made with ❤️ for better AI-powered research**
