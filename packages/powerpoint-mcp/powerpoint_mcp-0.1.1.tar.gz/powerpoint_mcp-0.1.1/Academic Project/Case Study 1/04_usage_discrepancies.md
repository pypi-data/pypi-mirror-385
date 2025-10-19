# Expected vs. Actual Usage: Anticipating Divergence

## Discrepancies in System Usage Patterns

While our storyboard outlines the intended use cases for PowerPoint MCP—automated report generation, data extraction, and AI-assisted content creation—the reality of deploying powerful automation tools reveals potential divergences between expected and actual usage patterns. Understanding these discrepancies is critical for designing appropriate safeguards and governance mechanisms.

## Expected Usage: Legitimate Automation Workflows

Our design anticipates users employing PowerPoint MCP for productivity-enhancing automation:

**Template-Based Generation:** Business analysts updating quarterly reports with new data while maintaining consistent formatting and structure. The AI reads the template, identifies data placeholders, applies new values from CSV files, and regenerates charts—saving hours of manual work while preserving presentation quality.

**Data Extraction for Analysis:** Researchers systematically extracting chart values and table data from historical presentations to conduct meta-analyses. The `slide_snapshot` tool enables mining presentation archives for analytical datasets previously locked in slide format.

**Educational Content Creation:** Educators generating lecture slides with professionally formatted LaTeX equations and matplotlib visualizations, focusing their time on pedagogical content while delegating formatting mechanics to AI assistance.

**Incremental Refinement:** Users engaging in conversational back-and-forth with Claude to iteratively improve presentations—"adjust the chart colors," "add speaker notes summarizing key points," "duplicate slide 5 and modify the title"—leveraging the persistent context and granular tool control that distinguishes our MCP approach.

## Actual Usage: Potential Misuse and Unintended Patterns

However, several discrepancies between expected and actual usage could emerge, each presenting risks that require mitigation:

### Security and Privacy Discrepancies

**Expected:** Users process presentations containing non-sensitive business data on their local machines, with COM automation staying within the user's security perimeter.

**Actual Risk:** Users might inadvertently or intentionally process presentations containing confidential information—trade secrets, personal data subject to GDPR, financial data under SOX compliance—without proper authorization workflows. The `powerpoint_evaluate` tool, which executes arbitrary Python code with COM access, could be exploited to exfiltrate data if a malicious prompt injection occurs or if users unknowingly paste untrusted prompts. While processing stays local, the outputs could be shared inappropriately, and the evaluate tool could access system files beyond PowerPoint if not properly sandboxed.

**Mitigation Consideration:** This discrepancy highlights the critical need for sandboxing the evaluate tool (blocking libraries like `os`, `subprocess`, `socket`), implementing audit logging for all operations, and potentially requiring user approval before executing any code via the evaluate tool. Privacy and security remain paramount "always-on" topics.

### Over-Reliance and Quality Control Discrepancies

**Expected:** Users employ PowerPoint MCP as an assistant—AI handles mechanical tasks while humans maintain creative control and verify outputs before distribution.

**Actual Risk:** Users might over-rely on automation, treating AI-generated presentations as final products without adequate review. This could manifest as: (1) distributing presentations with hallucinated data or incorrect chart values to executives or clients, (2) accepting AI-generated content that violates brand guidelines or messaging policies, (3) losing the skills to manually create presentations, creating dependency and vulnerability when systems fail. The conversational ease of natural language commands might paradoxically reduce scrutiny—"Claude, make it better" becomes a black box rather than a transparent operation.

**Mitigation Consideration:** This points to the importance of preview mechanisms, verification prompts for high-stakes operations, and educational resources emphasizing human-in-the-loop verification. The "human safety" always-on topic encompasses not just physical safety but cognitive safety—ensuring users remain engaged and critical rather than passive consumers of AI outputs.

### Malicious Code Execution Discrepancies

**Expected:** The `powerpoint_evaluate` tool enables sophisticated users to perform geometric calculations, batch operations, and complex automation workflows using Python with PowerPoint COM access.

**Actual Risk:** This tool could be weaponized for malicious purposes if inadequate sandboxing exists. Scenarios include: (1) Users inadvertently running malicious code from untrusted sources (prompt injection attacks where slide content or external inputs manipulate the AI into executing harmful code), (2) Deliberate misuse to access system resources, modify files outside PowerPoint scope, or establish network connections for data exfiltration, (3) Cryptocurrency mining or resource consumption attacks using the evaluate tool's computational access. Even without malicious intent, poorly written code could corrupt presentations, crash PowerPoint, or consume excessive system resources.

**Mitigation Consideration:** This represents the highest-severity security discrepancy and underscores why sandboxing must be Priority 1. Allowlist-based restrictions (only permitting safe libraries like `math`, `numpy`), execution timeouts, memory limits, and comprehensive audit trails are essential. The "governance and political risks" always-on topic applies here—organizational policies might require approval workflows for code execution operations.

### Societal and Misinformation Discrepancies

**Expected:** Users create presentations with factually accurate content, using AI to handle formatting and data visualization while maintaining content integrity.

**Actual Risk:** The combination of PowerPoint MCP and LLM capabilities (especially when MCP clients have WebSearch access) could scale misinformation. Scenarios include: (1) Generating presentations with fabricated statistics that appear credible due to professional formatting—"hallucinated" chart data visualized beautifully but factually wrong, (2) Creating deepfake-style business reports or research presentations with plausible but entirely false data, (3) Using WebSearch to pull information from unreliable sources and integrating it into authoritative-looking presentations without verification, (4) Automating the creation of misleading marketing materials or propaganda at scale. The professional appearance enabled by our tools could lend false credibility to inaccurate content.

**Mitigation Consideration:** This highlights the "societal risks" always-on topic. Potential mitigations include watermarking AI-generated content, requiring source attribution for data-driven charts, implementing fact-check prompts, and educating users about verification responsibilities. We might display warnings: "This chart was generated from AI-provided data—verify accuracy before distribution."

### Scale and Resource Consumption Discrepancies

**Expected:** Users perform reasonable automation tasks—updating dozens of presentations, extracting data from manageable archives, generating reports at human-appropriate scales.

**Actual Risk:** Users might push the system to extreme scales that create resource and sustainability issues: (1) Attempting to process thousands of presentations simultaneously, overwhelming system resources and causing crashes, (2) Running inefficient evaluate tool code that consumes excessive CPU/memory (nested loops, memory leaks, poorly optimized matplotlib rendering), (3) Creating runaway automation that continues operating unintended—"update all presentations in this directory" applied to a network share with thousands of files, (4) Energy waste from redundant operations or inefficient LLM API calls during trial-and-error workflows. The ease of natural language commands might obscure the computational cost of operations.

**Mitigation Consideration:** This connects to the "sustainability" always-on topic. Mitigations include resource limits (timeouts, memory caps), rate limiting for bulk operations, efficient caching to minimize redundant processing, and cost monitoring for API usage. Preview mechanisms showing "this operation will affect 500 files—continue?" help users understand scale implications.

### Legal and Compliance Discrepancies

**Expected:** Users operate within their organizational policies, respecting intellectual property, data protection regulations, and access controls.

**Actual Risk:** Automation could inadvertently violate legal and compliance requirements: (1) Copyright infringement through automated image insertion from web sources without license verification, (2) GDPR/CCPA violations by processing presentations containing personal data without proper legal basis or data subject consent, (3) Bypassing organizational approval workflows—presentations that normally require management review get auto-generated and distributed, (4) Export control violations if presentations containing technical data get automatically shared beyond authorized jurisdictions, (5) Unauthorized access to shared network drives or cloud-synced files that the user has technical access to but shouldn't be processing programmatically. The COM automation runs with full user privileges, accessing any file the user can access—but "can" doesn't mean "should."

**Mitigation Consideration:** This encompasses "legal risks" and "governance and political risks" always-on topics. Solutions include respecting file permissions, integrating with organizational DLP systems, implementing approval workflows for sensitive operations, comprehensive audit logging for compliance, and clear terms of service defining user responsibilities. We might need "read-only mode" options that disable all write operations for auditing scenarios.

### Financial Impact Discrepancies

**Expected:** PowerPoint MCP reduces costs by improving productivity—professionals spend less time on repetitive tasks, enabling higher-value work.

**Actual Risk:** The tool could paradoxically create financial losses: (1) Data corruption from buggy automation destroying valuable presentation assets representing thousands in design work, (2) Unexpected API costs from excessive LLM calls during inefficient workflows or trial-and-error experimentation, (3) Erroneous outputs causing business damage—incorrect financial projections in investor decks, wrong data in regulatory reports, (4) Productivity loss from tool failures during deadline-critical work, where reliance on automation becomes a single point of failure. The "last mile" we aim to automate might become a failure point rather than an efficiency gain.

**Mitigation Consideration:** This addresses "financial risks" through automated backups (version control before modifications), cost monitoring and usage limits, validation checks for numerical data (especially financial content), graceful degradation (failing safely without corrupting files), and testing environments where users can validate workflows before production use.

## Reflections on Design Implications

These discrepancies reveal that powerful automation tools require equally powerful safeguards. Our initial design focused on capability—enabling bidirectional PowerPoint manipulation through conversational AI. However, anticipating actual usage patterns highlights the necessity of layered security, governance mechanisms, and user education.

The most critical discrepancy centers on the `powerpoint_evaluate` tool: our most powerful capability is also our highest risk. This suggests a defense-in-depth approach: sandboxing as the technical foundation, user consent as the procedural layer, audit logging for accountability, and potentially role-based access control where organizations can disable evaluate for standard users while enabling it for power users with appropriate training.

Furthermore, the misinformation and quality control discrepancies suggest that AI-assisted automation must maintain human agency. Our design should make operations transparent (showing what will be changed before changing it), reversible (undo mechanisms), and verifiable (read back what was written). The goal is augmentation, not replacement—keeping humans in the loop while eliminating mechanical drudgery.

These expected vs. actual usage considerations inform our ongoing development priorities: sandboxing implementation, preview/approval workflows, comprehensive logging, and user education are not optional features but core requirements for responsible deployment of powerful automation capabilities.
