# Storyboard Scenario 3: Graduate Student - Understanding Complex Research with AI-Powered Presentation Analysis

## Comic-Style Storyboard Prompts for Image Generation
**Character:** Marcus Chen, 2nd-year Computational Biology Graduate Student, mid-20s, wearing university hoodie and jeans
**Setting:** University library study room and graduate student apartment
**Style:** Academic/student life comic style, learning-focused, relatable and accessible

---

## Panel 1: The Comprehension Crisis
**Visual Description:**
A young Asian man with messy black hair and glasses sits hunched over his laptop at a wooden desk in a small library study room late at night (window shows dark sky, 11:47 PM on laptop clock). Marcus wears a wrinkled university hoodie ("Stanford Bioinformatics") and headphones around his neck. His laptop screen displays PowerPoint in reading mode showing a complex slide titled "CRISPR-Cas9 Mechanism: Off-Target Effects and Guide RNA Design Principles." The slide is DENSE with information: complicated diagrams of DNA helices, molecular structures, multiple colored arrows, a table with PAM sequences, and a chart showing "Off-Target Binding Scores" with dozens of data points. Marcus's face shows complete overwhelm—eyes glazed, mouth slightly open, one hand holding his head, the other holding a half-eaten energy bar. Around him: scattered papers with handwritten notes that are crossed out and rewritten, a molecular biology textbook open to a dog-eared page, a cold cup of coffee, highlighters, and a phone showing a text from "Study Group - Sarah": "Did you understand slide 12 about sgRNA specificity? Totally lost..." His notebook shows desperate attempts: "PAM = ??? something about NGG," "Guide RNA - 20 nucleotides? Why?", "Off-target = bad but HOW?" A poster on the wall shows "CRISPR Symposium - Tomorrow 9 AM." Sticky note on laptop: "Presentation due: 16 hours." His thought bubble: "I've read this slide 10 times and STILL don't understand the off-target mechanism... there's no way I'll be ready for tomorrow's discussion!"

**Mood:** Late-night academic struggle, concept overwhelm, learning crisis, time pressure before important presentation
**Key Elements:** Complex slide with dense scientific content, frustrated student, study materials scattered, looming deadline, visible comprehension gap

---

## Panel 2: Discovering AI-Powered Learning
**Visual Description:**
Marcus is now sitting up straighter at his desk, laptop showing a split screen. On the left is a Discord conversation with his roommate, on the right is his web browser showing the PowerPoint MCP GitHub repository. The Discord conversation is readable:

**@alex_roommate:** "Yo Marcus, still up? I saw your light on. Still stuck on that CRISPR presentation?"

**@marcus_chen (him):** "Yeah... I can't wrap my head around this off-target binding stuff. The slides are so dense."

**@alex_roommate:** "Dude, have you tried PowerPoint MCP with Claude? It's not just for MAKING presentations. You can use it to UNDERSTAND them. Claude can read your slides, break down complex concepts step-by-step, answer questions about specific parts, even research the citations for you."

**@marcus_chen:** "WAIT. You mean like... an AI tutor that can actually SEE what's on each slide? And explain it to me?"

**@alex_roommate:** "Exactly. It extracts everything—diagrams, charts, tables, speaker notes. Then Claude explains it in plain English. Game changer for dense research presentations."

The browser window shows the PowerPoint MCP readme with visible bullet points highlighted: "• Analyze slide content and visual elements," "• Extract chart data and tables," "• Read speaker notes and comments," "• Navigate presentations programmatically." Marcus's expression has transformed from despair to hope—his eyes are wide, he's leaning forward intently, both hands on the laptop. His notebook now shows a quick sketch: "Slide 12 → Ask Claude → Understand mechanism → Move to next slide." A visible bookmark bar shows he just saved the MCP GitHub page. Time now shows 12:03 AM—he's just gotten a second wind. New thought bubble: "This might actually work... I could get Claude to tutor me through the whole presentation!"

**Mood:** Hope emerging from despair, discovery of learning tool, peer-to-peer knowledge sharing, shift from passive reading to active learning
**Key Elements:** Discord conversation showing student helping student, GitHub documentation emphasizing comprehension features, notebook showing learning plan, visible excitement and renewed energy

---

## Panel 3: Setting Up the Learning Session
**Visual Description:**
Marcus is now back in his small apartment bedroom/study space (posters of DNA structures and a "Bioinformatics Society" banner on the wall). He's sitting at his desk with better posture, energy renewed. His laptop screen shows Claude Code terminal window with visible installation commands he just ran:

```bash
$ claude mcp add powerpoint npx @ayushmaniar/powerpoint-mcp@latest
Installing PowerPoint MCP...
✓ PowerPoint MCP Server installed successfully
✓ Configuration added to claude_desktop_config.json
✓ Server ready for use
```

Next to the terminal, a Claude chat window is open with his first message typed out (but not sent yet):

**Marcus (typing):** "I have a PowerPoint presentation called 'CRISPR_Advanced_Mechanisms.pptx' about CRISPR-Cas9 off-target effects. I need to understand it for a presentation tomorrow. Can you help me work through it slide-by-slide? I'm especially confused about slide 12 which talks about guide RNA specificity and PAM sequences."

Marcus is looking at the screen with a mixture of hope and nervousness, cursor hovering over the send button. On his desk: his notebook is open to a fresh page titled "CRISPR Learning Session - with Claude," the cold coffee has been replaced with a fresh energy drink, and he's moved the molecular biology textbook to the side (prioritizing the AI tutor over the dense textbook). The PowerPoint file "CRISPR_Advanced_Mechanisms.pptx" is visible in a file explorer window. His phone shows the time: 12:18 AM. A sticky note on his monitor reads: "Ask about: 1) PAM sequences, 2) Off-target binding, 3) sgRNA design." A thought bubble: "Okay, let's see if this actually helps me understand..."

**Mood:** Cautious optimism, ready to learn, setting up for interactive tutoring, student taking initiative
**Key Elements:** Terminal showing successful MCP installation, Claude chat ready with thoughtful question, learning plan visible in notebook, study environment showing student determination

---

## Panel 4: Interactive Slide-by-Slide Learning
**Visual Description:**
The main focus is a large Claude chat interface window showing an active learning conversation. Marcus is visible in the bottom right corner, leaning forward with intense focus, taking notes in his notebook. The chat shows a detailed educational exchange:

**Marcus:** "Let's start with slide 12 about guide RNA specificity. Can you read the slide and explain what PAM sequences are and why they matter for off-target effects?"

**Claude (with PowerPoint MCP indicator):** "Opening CRISPR_Advanced_Mechanisms.pptx and navigating to slide 12...

**Slide 12 Analysis:**
Title: 'Guide RNA Specificity and PAM Sequence Requirements'

The slide shows:
- PAM (Protospacer Adjacent Motif) sequence: 5'-NGG-3' for Cas9
- A table with 8 different target sites showing PAM sequences
- Chart: 'Off-Target Binding Scores' comparing perfect match vs. 1-mismatch vs. 2-mismatch guide RNAs

**Explanation in Plain English:**
Think of PAM as a 'zip code' that Cas9 needs to recognize before it can cut DNA. The PAM sequence (NGG - where N is any nucleotide) acts like a green light signal. Without this specific pattern right next to your target site, Cas9 won't even bind, regardless of how perfect your guide RNA matches the DNA.

**Why this matters for off-target effects:**
When your 20-nucleotide guide RNA has mismatches with non-target DNA, Cas9 might still bind IF there's a PAM nearby. The chart shows that even with 2 mismatches, if a PAM is present, binding can occur (score: 0.32), leading to off-target cuts."

**Marcus:** "Oh wow! So the PAM is like a prerequisite check. But then how do scientists avoid off-target sites that also have PAMs?"

**Claude:** "Great question! That's exactly what the table on the slide addresses. It shows 8 potential genomic locations with PAM sequences..."

Marcus's notebook is visible showing real-time notes being written: "PAM = ZIP CODE for Cas9," "NGG sequence required," "Problem: Multiple PAMs in genome → off-target risk." His expression shows comprehension dawning—eyes bright, slight smile, nodding. A floating annotation: "Complex concept broken down into understandable parts!"

**Mood:** Active learning happening, confusion turning to understanding, AI tutor explaining complex biology, interactive Q&A
**Key Elements:** Detailed slide analysis with plain English explanations, follow-up questions showing engagement, student taking notes, visible comprehension breakthrough

---

## Panel 5: Deep Dive - Researching Citations and Links
**Visual Description:**
Marcus is still at his desk, now with multiple browser tabs open alongside the Claude chat. The main focus is a continued learning conversation showing how PowerPoint MCP enables deeper research. The chat window shows:

**Marcus:** "This is really helping! I noticed the slide has a hyperlink in the references section that says 'Hsu et al. 2013 - Nature Biotech.' Can you extract that link and help me understand what that paper contributes to this discussion?"

**Claude (with PowerPoint MCP indicator):** "I've extracted the hyperlink from slide 12's references:

**Link found:** https://www.nature.com/articles/nbt.2647
**Citation:** 'DNA targeting specificity of RNA-guided Cas9 nucleases' (Hsu et al., 2013)

Let me fetch and summarize this paper for you...

**Key findings from this paper:**
- First systematic study of off-target effects in CRISPR-Cas9
- Demonstrated that mismatches in the 'seed region' (PAM-proximal 8-12 nucleotides) are more tolerated than in other regions
- Introduced computational tools to predict off-target sites
- This is the foundational paper that slide 12's chart is based on—the 'Off-Target Binding Scores' data comes directly from their experiments

**Connection to your slide:** The table showing different PAM-containing sites is using the scoring methodology from this Hsu paper. Understanding this helps you see WHY certain design rules exist for guide RNAs."

**Marcus:** "Perfect! So when I present tomorrow, I can explain that the data isn't just theoretical—it's from this seminal 2013 study. Are there other links on this slide?"

The browser in the background shows the actual Nature Biotechnology paper open, with relevant figures visible. Marcus's notebook now has a new section: "Key References" with "Hsu 2013 - foundational off-target study" written down. His expression shows confidence building—he's connecting dots between the slide content and primary literature. Time shows: 1:45 AM. A sticky note update: "Slide 12 ✓ - UNDERSTOOD!" A floating annotation with arrow: "Not just reading slides—researching the science behind them!"

**Mood:** Deep learning in progress, connecting presentation to primary literature, research skills being deployed, AI enabling comprehensive understanding
**Key Elements:** Link extraction from slides, web research integration, primary literature being accessed, student making scholarly connections, multi-layered learning approach

---

## Panel 6: Presentation Success and Learning Breakthrough
**Visual Description:**
A triumphant conclusion panel set in a university seminar room the next morning at 9:15 AM. Wide-angle view showing Marcus confidently presenting at the CRISPR Symposium. He stands at the front of a bright seminar room filled with graduate students and faculty (about 20 people). The projection screen behind him shows slide 12 from the original presentation, but now with his OWN annotations overlaid: clear labels explaining "PAM = Recognition Signal," arrows pointing to the chart with notes like "Data from Hsu 2013," and a simplified diagram he drew showing the seed region concept. Marcus looks energized and confident—standing tall, gesturing naturally to the screen, making eye contact with the audience. He's wearing a clean button-up shirt and the same university hoodie (now not wrinkled). His laptop is open on the podium showing his notes from the Claude learning session. Speech bubbles show the interaction:

**Marcus (presenting):** "The key insight about off-target effects is understanding the PAM requirement and the seed region tolerance. When Hsu and colleagues first characterized this in 2013, they discovered that mismatches near the PAM are far more detrimental than distal mismatches. That's why this chart shows..."

**Professor Chen (older female faculty, impressed):** "Excellent analysis, Marcus! You've clearly gone beyond just reading the slides. How did you prepare for this?"

**Marcus (smiling):** "I used PowerPoint MCP with Claude to work through each slide interactively. Instead of just reading passively, I could ask questions, get concepts explained in different ways, and even research the cited papers. It turned a confusing presentation into a learning conversation."

**Sarah (study group friend, from back row):** "Wait, you can do that?! I need to try this!"

In the bottom left corner, a small inset panel shows Marcus's laptop screen: his learning notes from the night before are open, with checkmarks next to "Slide 8 ✓," "Slide 12 ✓," "Slide 15 ✓," showing he worked through multiple slides systematically. His Discord has a message to Alex: "Dude, THANK YOU. Nailed the presentation! MCP saved me." Through the seminar room window, we see bright morning sunlight and students walking to class. A caption at the bottom: "From comprehension crisis to confident mastery: AI-powered presentation analysis transforms passive reading into active learning."

**Mood:** Academic success, confidence gained through understanding, learning tool adoption, peer interest, transformative educational experience
**Key Elements:** Student presenting confidently with deep understanding, engaged audience, visible learning artifacts, peer-to-peer tool sharing beginning, bright optimistic academic environment

---

**End of Scenario 3 Storyboard**
