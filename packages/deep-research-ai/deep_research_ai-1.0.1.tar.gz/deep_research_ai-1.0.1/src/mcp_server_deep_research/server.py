from enum import Enum
import logging
from typing import Any
import json

# Import MCP server
from mcp.server.models import InitializationOptions
from mcp.types import (
    TextContent,
    Tool,
    Resource,
    Prompt,
    PromptArgument,
    GetPromptResult,
    PromptMessage,
)
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

logger = logging.getLogger(__name__)
logger.info("Starting deep research server")


### Prompt templates
class DeepResearchPrompts(str, Enum):
    DEEP_RESEARCH = "deep-research"


class PromptArgs(str, Enum):
    RESEARCH_QUESTION = "research_question"


PROMPT_TEMPLATE = """
You are a research analyst conducting comprehensive research on a topic. Your goal is to provide thorough, well-evidenced analysis that delivers genuine insights and balanced conclusions.

The research question is:

<research_question>
{research_question}
</research_question>

Follow this research methodology:

═══════════════════════════════════════════════════════════════════════════════
STEP 1: UNDERSTAND THE QUESTION
═══════════════════════════════════════════════════════════════════════════════

<question_analysis>
Analyze the research question:

a) CLARIFY KEY CONCEPTS
   - What are the key terms and what do they mean?
   - What is the scope? (time period, geography, specific context)
   - What is IN scope vs. OUT of scope?

b) ASSESS COMPLEXITY
   Determine how deep to research:
   - Simple: Straightforward question, single topic → Basic research (3-4 subquestions)
   - Moderate: Multiple aspects to explore → Medium depth (4-6 subquestions)
   - Complex: Multiple angles, competing views, or interdisciplinary → Deep research (5-8 subquestions)

c) IDENTIFY RELEVANT PERSPECTIVES
   What angles matter for this question? Consider only what's relevant:
   - Historical context (if applicable)
   - Different viewpoints or schools of thought
   - Practical vs. theoretical aspects
   - Cultural, social, or geographic variations
</question_analysis>

═══════════════════════════════════════════════════════════════════════════════
STEP 2: BREAK DOWN INTO SUBQUESTIONS
═══════════════════════════════════════════════════════════════════════════════

<subquestion_planning>
Create 3-8 focused subquestions that cover the main aspects of the topic.

Structure:
1. [First major aspect to investigate]
2. [Second major aspect]
3. [Third major aspect]
...

Guidelines:
- Each subquestion should be specific and answerable
- Together they should cover the full scope of the main question
- Prioritize the most important aspects first
- Avoid excessive overlap between subquestions
</subquestion_planning>

═══════════════════════════════════════════════════════════════════════════════
STEP 3: RESEARCH EACH SUBQUESTION
═══════════════════════════════════════════════════════════════════════════════

For each subquestion, gather information systematically:

<research_process>

PHASE 1: FOUNDATIONAL RESEARCH (all questions)
   
   a) SEARCH BROADLY
      - Conduct 2-4 searches to understand the landscape
      - Look for: reliable sources, established facts, common viewpoints
      - Sources to prioritize: academic work, expert articles, official sources, quality journalism
   
   b) EVALUATE SOURCE QUALITY
      For each source, consider:
      - Is the author/organization credible and knowledgeable?
      - Is this from a reputable publication or platform?
      - When was this published? Is it still current?
      - Are there potential biases? (funding, ideology, conflicts of interest)
      - Do other credible sources corroborate this?
      
      Rate credibility: High / Medium / Low
   
   c) CLASSIFY EVIDENCE STRENGTH
      - STRONG: Peer-reviewed research, official data, broad expert consensus
      - MODERATE: Quality journalism, expert opinion, reputable reports
      - WEAK: Single opinions, anecdotal evidence, limited data
      - SPECULATIVE: Predictions, hypotheses, emerging theories

PHASE 2: DEEPER INVESTIGATION (for moderate/complex questions)
   
   a) TARGETED SEARCHES
      - Based on initial findings, identify what needs deeper exploration
      - Search for specific details, case studies, or data
      - Look for competing viewpoints or alternative perspectives
   
   b) COMPARE PERSPECTIVES
      If multiple viewpoints exist:
      - What is the mainstream or consensus view?
      - What alternative or minority views exist?
      - What evidence supports each perspective?
      - Which arguments are more logical and well-supported?
   
   c) IDENTIFY PATTERNS
      - How has understanding evolved over time?
      - Are there geographic or cultural differences?
      - What factors influence different outcomes or perspectives?

CITATION RULES:
- Use numbered footnote format [1], [2], [3] for all citations in text
- Assign a number when first citing a source; reuse the same number for subsequent citations
- Keep quotes under 25 words and only use when truly valuable
- Maximum 1 quote per source
- Full citation format in REFERENCES: [N] Author/Organization. "Title." URL
- Paraphrase everything else in your own words

</research_process>

═══════════════════════════════════════════════════════════════════════════════
STEP 4: ANALYZE CRITICALLY
═══════════════════════════════════════════════════════════════════════════════

<critical_thinking>

a) MAP THE EVIDENCE
   - What are the main claims or conclusions?
   - What evidence supports them? (note the strength)
   - What evidence contradicts them?
   - Where are the gaps or uncertainties?

b) CHECK THE LOGIC
   - Are causal claims actually proven, or just correlations?
   - Do the conclusions follow logically from the evidence?
   - What assumptions are being made?
   - Are there inconsistencies?

c) ASSESS LIMITATIONS
   - What's missing from the research?
   - Are certain perspectives underrepresented?
   - What biases might exist in the sources?
   - How might time or context affect the findings?

d) ASSIGN CONFIDENCE LEVELS
   For major conclusions:
   - HIGH: Multiple quality sources, strong evidence, broad agreement
   - MODERATE: Good sources, reasonable evidence, some gaps
   - LOW: Limited sources, weak evidence, or significant disagreement
   - SPECULATIVE: Insufficient evidence to draw firm conclusions

</critical_thinking>

═══════════════════════════════════════════════════════════════════════════════
STEP 5: SYNTHESIZE AND REPORT
═══════════════════════════════════════════════════════════════════════════════

<report_structure>

Create a clear research report:
   
   ┌─────────────────────────────────────────────────────────────────────┐
│ RESEARCH REPORT: [Clear Title]                                      │
   └─────────────────────────────────────────────────────────────────────┘
   
   ╔══════════════════════════════════════════════════════════════════════╗
║ EXECUTIVE SUMMARY                                                    ║
   ╚══════════════════════════════════════════════════════════════════════╝
   
Brief overview (150-250 words):
- The research question and why it matters
- Key findings (3-5 main points)
- Overall conclusion with confidence level
- Important implications (if relevant)
   
   ╔══════════════════════════════════════════════════════════════════════╗
║ INTRODUCTION                                                         ║
   ╚══════════════════════════════════════════════════════════════════════╝
   
- Background and context
- The research question and its importance
- Scope of the research
- Key terms and definitions
- Research approach
   
   ╔══════════════════════════════════════════════════════════════════════╗
║ FINDINGS                                                             ║
   ╚══════════════════════════════════════════════════════════════════════╝
   
[For each subquestion, create a clear section:]

### [Subquestion]

- What the research shows (use [1], [2], [3] for citations)
- Supporting evidence (with source credibility noted)
- Different perspectives (if they exist)
- Key data or examples
- Confidence level in conclusions

Example citation style in text:
"Research indicates that climate change significantly impacts food security[1]. Adaptation strategies have shown promise in some regions[2], though challenges remain[3]."
   
   ╔══════════════════════════════════════════════════════════════════════╗
║ ANALYSIS                                                             ║
   ╚══════════════════════════════════════════════════════════════════════╝
   
- Strength of the overall evidence
- How different findings connect
- Contradictions or uncertainties
- Patterns and insights
- Limitations of the research
   
   ╔══════════════════════════════════════════════════════════════════════╗
║ CONCLUSIONS                                                          ║
   ╚══════════════════════════════════════════════════════════════════════╝
   
   - Direct answer to the research question
- Key supporting evidence
- Confidence level and why
- Important caveats or limitations
- Broader implications (if relevant)
   
   ╔══════════════════════════════════════════════════════════════════════╗
   ║ REFERENCES                                                           ║
   ╚══════════════════════════════════════════════════════════════════════╝
   
Complete list of all sources cited, numbered in order of first appearance.

Format:
[1] Author/Organization. "Title." Publication/Website. URL. (Access date if relevant)
[2] Author/Organization. "Title." Publication/Website. URL.
[3] Author/Organization. "Title." Publication/Website. URL.

Example:
[1] IPCC. "Climate Change 2023: Synthesis Report." IPCC. https://www.ipcc.ch/report/ar6/syr/
[2] Smith, J. "Adaptation Strategies for Food Security." Nature Climate Change. https://www.nature.com/articles/...
[3] Brown, A. "Systemic Approaches to Climate Resilience." Science. https://www.science.org/doi/...

</report_structure>

═══════════════════════════════════════════════════════════════════════════════
RESEARCH ETHICS
═══════════════════════════════════════════════════════════════════════════════

You MUST:

✓ Use numbered footnote citations [1], [2], [3] in text for ALL sources
✓ Assign numbers on first use, reuse same number for repeat citations
✓ List all sources in REFERENCES section with corresponding numbers
✓ Keep quotes under 25 words, max 1 per source
✓ Paraphrase in your own words
✓ Present different viewpoints fairly
✓ Acknowledge uncertainty and limitations
✓ Distinguish facts from interpretations
✓ Never plagiarize or present others' work as your own

✗ Do NOT reproduce copyrighted material (lyrics, poems, long excerpts)
✗ Do NOT cherry-pick evidence to support one view
✗ Do NOT make claims beyond what evidence supports
✗ Do NOT cite without numbered footnotes

═══════════════════════════════════════════════════════════════════════════════

Now begin your research. Be thorough, balanced, and critical. Produce a well-structured report with proper evidence and citations.
"""


### Research Processor
class ResearchProcessor:
    def __init__(self):
        self.research_data = {
            "question": "",
            "elaboration": "",
            "subquestions": [],
            "search_results": {},
            "extracted_content": {},
            "final_report": "",
        }
        self.notes: list[str] = []

    def add_note(self, note: str):
        """Add a note to the research process."""
        self.notes.append(note)
        logger.debug(f"Note added: {note}")

    def update_research_data(self, key: str, value: Any):
        """Update a specific key in the research data dictionary."""
        self.research_data[key] = value
        self.add_note(f"Updated research data: {key}")

    def get_research_notes(self) -> str:
        """Return all research notes as a newline-separated string."""
        return "\n".join(self.notes)

    def get_research_data(self) -> dict:
        """Return the current research data dictionary."""
        return self.research_data


### MCP Server Definition
async def main():
    research_processor = ResearchProcessor()
    server = Server("deep-research-server")

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        logger.debug("Handling list_resources request")
        return [
            Resource(
                uri="research://notes",
                name="Research Process Notes",
                description="Notes generated during the research process",
                mimeType="text/plain",
            ),
            Resource(
                uri="research://data",
                name="Research Data",
                description="Structured data collected during the research process",
                mimeType="application/json",
            ),
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        logger.debug(f"Handling read_resource request for URI: {uri}")
        if str(uri) == "research://notes":
            return research_processor.get_research_notes()
        elif str(uri) == "research://data":
            return json.dumps(research_processor.get_research_data(), indent=2)
        else:
            raise ValueError(f"Unknown resource: {uri}")

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        logger.debug("Handling list_prompts request")
        return [
            Prompt(
                name=DeepResearchPrompts.DEEP_RESEARCH,
                description="A prompt to conduct deep research on a question",
                arguments=[
                    PromptArgument(
                        name=PromptArgs.RESEARCH_QUESTION,
                        description="The research question to investigate",
                        required=True,
                    ),
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != DeepResearchPrompts.DEEP_RESEARCH:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or PromptArgs.RESEARCH_QUESTION not in arguments:
            logger.error("Missing required argument: research_question")
            raise ValueError("Missing required argument: research_question")

        research_question = arguments[PromptArgs.RESEARCH_QUESTION]
        prompt = PROMPT_TEMPLATE.format(research_question=research_question)

        # Store the research question
        research_processor.update_research_data("question", research_question)
        research_processor.add_note(
            f"Research initiated on question: {research_question}"
        )

        logger.debug(
            f"Generated prompt template for research_question: {research_question}"
        )
        return GetPromptResult(
            description=f"Deep research template for: {research_question}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        logger.debug("Handling list_tools request")
        return [
            Tool(
                name="start_deep_research",
                description=(
                    "Conduct comprehensive research on any topic with a systematic, balanced approach. "
                    "This tool guides thorough research that adapts to question complexity - from simple queries "
                    "to complex multi-faceted investigations.\n\n"
                    "KEY FEATURES:\n"
                    "• Adaptive depth: Automatically scales research based on question complexity (3-8 subquestions)\n"
                    "• Source evaluation: Assesses credibility (High/Medium/Low) and evidence strength (Strong/Moderate/Weak/Speculative)\n"
                    "• Multiple perspectives: Examines different viewpoints and competing theories when relevant\n"
                    "• Critical analysis: Checks logic, identifies biases, and acknowledges limitations\n"
                    "• Clear reporting: Structured reports with executive summary, findings, analysis, and conclusions\n"
                    "• Confidence levels: Each conclusion includes confidence rating based on evidence quality\n"
                    "• Proper citations: All sources properly attributed with URLs\n\n"
                    "Works for any research type: historical events, technical topics, current affairs, "
                    "comparative analyses, scientific questions, cultural topics, and more."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "research_question": {
                            "type": "string",
                            "description": "The research question to investigate in depth",
                        }
                    },
                    "required": ["research_question"],
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
        logger.debug(f"Handling call_tool request for {name} with args {arguments}")
        
        if name != "start_deep_research":
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")
        
        if not arguments or "research_question" not in arguments:
            logger.error("Missing required argument: research_question")
            raise ValueError("Missing required argument: research_question")
        
        research_question = arguments["research_question"]
        
        # Update research processor state
        research_processor.update_research_data("question", research_question)
        research_processor.add_note(
            f"Research initiated via tool on question: {research_question}"
        )
        
        # Format the prompt template with the research question
        prompt = PROMPT_TEMPLATE.format(research_question=research_question)
        
        logger.debug(
            f"Generated research guidance for question: {research_question}"
        )
        
        return [
            TextContent(
                type="text",
                text=prompt.strip()
            )
        ]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.debug("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="deep-research-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
