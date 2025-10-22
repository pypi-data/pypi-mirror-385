# Changelog

All notable changes to the MCP Server Deep Research project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-10-21

### Changed
- **Citation Format**: Updated to academic footnote system with numbered references
  - Citations in text now use [1], [2], [3] format
  - Sources numbered in order of first appearance
  - Full citations listed in REFERENCES section with corresponding numbers
  - Enhanced citation examples and formatting guidelines in prompt template

### Improved
- Research reports now follow academic standard with proper footnote citations
- Better readability with inline numeric references
- Clearer separation between text content and source attribution
- Consistent citation numbering throughout the report

## [0.2.0] - 2025-10-21

### Added - Major Research Methodology Overhaul

#### Intelligence & Adaptability
- **Complexity Assessment System**: Automatic evaluation of questions as Simple/Moderate/Complex/Highly Complex
- **Adaptive Methodology**: Research depth and structure dynamically adjust based on complexity
- **Domain Mapping**: Identifies primary knowledge domains and cross-disciplinary intersections
- **Stakeholder Identification**: Maps who cares about the question and why

#### Research Depth Enhancement
- **Three-Layer Progressive Research**:
  - Layer 1 (Overview): Foundational understanding - always applied
  - Layer 2 (Deep Dive): Focused investigation - for Moderate+ complexity
  - Layer 3 (Expert Analysis): Cutting-edge insights - for Complex+ questions
- **Source Credibility Assessment**: High/Medium/Low ratings based on authority, recency, and bias
- **Evidence Classification**: Strong/Moderate/Weak/Speculative based on research rigor

#### Question Decomposition
- **Dynamic Subquestion Generation**: 3-8 questions based on complexity (was fixed 3-5)
- **Hierarchical Tree Structure**: Core questions with secondary deep-dive sub-questions
- **Priority Tagging**: High/Medium/Low importance levels
- **Dependency Mapping**: Identifies which questions build on others
- **Interdisciplinary Tagging**: Labels questions with relevant disciplines (Technical, Economic, Social, Ethical, Legal, Scientific, Historical)

#### Critical Analysis Framework
- **Evidence Mapping**: Central claims, supporting evidence, contradicting evidence, gaps
- **Logical Coherence Checking**: 
  - Causation vs. correlation analysis
  - Internal consistency evaluation
  - Reasoning validity assessment
  - Assumption identification
- **Bias Assessment**: Selection, confirmation, temporal, publication bias evaluation
- **Hypothesis Testing**: Formulate → Evaluate → Conclude (Supported/Partial/Not Supported/Insufficient Evidence)
- **Confidence Level System**: HIGH/MODERATE/LOW/SPECULATIVE ratings for all major conclusions

#### Professional Analysis Frameworks (9+ options)
- SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
- PEST/PESTEL Analysis (Political, Economic, Social, Technological, Environmental, Legal)
- 5W2H Framework (What, Why, When, Where, Who, How, How Much)
- Comparative Analysis (multi-dimensional comparison)
- Trend Analysis (historical evolution → present → future trajectories)
- Case Study Method (deep-dive into specific examples)
- Stakeholder Analysis (perspective and interest mapping)
- Evidence Pyramid (medical/scientific evidence hierarchy)
- Systems Thinking (interconnections, feedback loops, leverage points)

#### Interdisciplinary Synthesis
- **Cross-Perspective Patterns**: Identifies where different disciplines align or diverge
- **Emergent Insights**: Discovers insights visible only when combining multiple perspectives
- **Systems-Level Understanding**: Maps interactions, feedback loops, cascading effects

#### Enhanced Report Structure
- **Executive Summary**: 200-300 word standalone overview with key findings
- **Table of Contents**: Auto-generated navigation
- **Methodology Section**: Complexity assessment rationale, framework selection justification, limitations
- **Critical Analysis Section**: Separate from findings, evaluates evidence strength and contradictions
- **Synthesis & Discussion**: Interdisciplinary integration, emergent patterns, contextual factors
- **Confidence Levels**: Explicitly stated for all conclusions
- **Recommendations**: Stakeholder-specific actionable guidance
- **Research Limitations**: Transparent acknowledgment of scope constraints, methodological limitations, biases
- **Further Research Directions**: Identified knowledge gaps and promising investigation areas
- **Glossary**: Technical and specialized term definitions
- **Supplementary Data Appendix**: Additional tables, charts, detailed data

### Changed

#### Quality Standards
- **Citation Requirements**: More rigorous attribution of all facts, data, and ideas
- **Quotation Limits**: Stricter enforcement (max 25 words per quote, 1 quote per source)
- **Evidence Standards**: All claims now require evidence strength ratings
- **Transparency**: Uncertainty and knowledge boundaries must be explicitly acknowledged

#### Research Process
- **From Linear to Phased**: 1-step process → structured 5-phase methodology
- **From Fixed to Adaptive**: Same approach for all → complexity-adjusted strategy
- **From Surface to Depth**: Single-layer search → progressive 3-layer investigation
- **From Descriptive to Critical**: Basic analysis → systematic evidence evaluation

### Improved

- **Research Depth**: Significantly deeper analysis with multi-layer investigation
- **Analytical Rigor**: Systematic evidence evaluation vs. ad-hoc analysis
- **Adaptability**: Scales from simple comparisons to complex multi-disciplinary research
- **Report Quality**: Blog-post level → Publication/academic-quality reports
- **Transparency**: Implicit assumptions → Explicit confidence levels and limitations
- **Actionability**: Descriptive findings → Stakeholder-specific recommendations

### Documentation

- **TESTING.md**: Comprehensive testing guide with 4 complexity levels and success criteria
- **README.md**: Extensively updated with feature descriptions, examples, and workflow details
- **CHANGELOG.md**: This file for version tracking

### Technical

- **Prompt Template**: Complete rewrite from 60 lines to 470+ lines of structured guidance
- **No Breaking Changes**: Tool interface remains compatible with v0.1.0

---

## [0.1.0] - 2024 (Approximate)

### Added
- Initial release of MCP Server for Deep Research
- `start_deep_research` tool for direct invocation from Claude Desktop
- Basic structured research workflow
- Web search integration leveraging Claude's capabilities
- Research report generation as artifacts
- Question elaboration phase
- Subquestion generation (3-5 fixed questions)
- Citation requirements and copyright guidelines
- Research processor for state tracking
- MCP server implementation with stdio transport

### Features
- Question elaboration and clarification
- 3-5 subquestion generation
- Web search for each subquestion
- Source credibility basic assessment
- Report generation with:
  - Introduction
  - Findings sections
  - Conclusion
  - References
- Proper citation formatting

---

## Version Comparison Summary

| Feature | v0.1.0 | v0.2.0 |
|---------|--------|--------|
| **Complexity Assessment** | None | 4-level automatic |
| **Research Layers** | 1 | 1-3 adaptive |
| **Subquestions** | 3-5 fixed | 3-8 dynamic + hierarchical |
| **Analytical Frameworks** | None | 9+ options |
| **Disciplinary Perspectives** | Implicit | 7+ explicit |
| **Evidence Quality** | Basic | 4-level classification |
| **Confidence Levels** | None | 4-level system |
| **Critical Analysis** | Basic | Comprehensive |
| **Hypothesis Testing** | No | Yes |
| **Report Sections** | 4 basic | 11+ comprehensive |
| **Prompt Length** | ~60 lines | ~470 lines |

---

## Future Considerations

Potential enhancements for future versions:
- Meta-analysis capability for synthesizing across studies
- Automated fact-checking against known databases
- Visualization generation for data-heavy topics
- Domain-specific prompt variants (medical, legal, technical, business)
- Iterative refinement based on user feedback
- Multi-language research support
- Cross-cultural perspective analysis

---

**Note**: This project is under active development. Feedback and contributions are welcome!

