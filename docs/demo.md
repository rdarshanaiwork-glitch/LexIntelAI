# LexIntel AI: 5-Minute Presentation & Demo Walkthrough Script

This script guides the presenter through an impressive, academically rigorous, 5-minute live demonstration of LexIntel AI during a project defense or presentation.

---

## Demo Preparation Checklist
- [ ] Backend running: `http://127.0.0.1:8000` (Health: `http://127.0.0.1:8000/api/health`)
- [ ] Frontend running: `http://localhost:5173`
- [ ] Browser open at `http://localhost:5173`
- [ ] Demo credentials: `counsel@lexintel.ai` / `LexIntel2026!`

---

## Scene-by-Scene Demo Script

### Minute 1: The Landing Page & Problem Statement (0:00 - 1:00)
1. **Visual**: Show the Landing Page (`http://localhost:5173/`).
2. **Narration**:
   > *"Good morning committee members. Current legal AI tools are predominantly basic chatbots. They suffer from high hallucination rates, fabricate case citations, and lack strategic reasoning. We built LexIntel AI—an autonomous multi-agent legal intelligence platform that replaces single-pass chat with a 10-agent LangGraph cognitive workflow."*
3. **Action**: Scroll to the **Interactive 10-Agent Pipeline** showcase. Hover over `CoordinatorAgent`, `OpponentAgent`, `JudgeAgent`, and `CriticAgent` to highlight their roles.
4. **Action**: Click **"VIEW BENCHMARKS"** or navigate to the Evaluation tab.

---

### Minute 2: The Empirical Benchmark Suite (1:00 - 2:00)
1. **Visual**: Show the Evaluation Dashboard (`/evaluation`).
2. **Narration**:
   > *"Rather than relying on ungrounded qualitative claims, LexIntel AI is backed by an automated empirical evaluation harness. Across 4 benchmark scenarios covering whistleblower protection, trade secrets, commercial contracts, and statutory inquiries, the platform achieves 100% workflow completion, 100% legal retrieval precision, and 100% citation validity with zero hallucinations."*
3. **Action**: Point out the **Agent Reliability Matrix** (34/34 successful node executions) and click **"Re-Run Evaluation Harness"** to demonstrate live execution.

---

### Minute 3: Case Workspace & Launching Analysis (2:00 - 3:00)
1. **Action**: Click **"Cases"** in the sidebar. Select **"Apex Logistics Solutions LLC v. Horizon Retail Enterprise Inc."**.
2. **Visual**: The Case Workspace with uploaded contract exhibits, force majeure notices, and port congestion logs.
3. **Narration**:
   > *"Here is a complex commercial dispute involving severe supply chain delays, force majeure clauses under UCC § 2-615, and disputed liquidated damages under Restatement (Second) of Contracts § 356. Let's initiate a full multi-agent litigation analysis."*
4. **Action**: Click **"Analyze Matter"**. The system transitions to the live execution view showing each agent persona performing its task.

---

### Minute 4: Deep Dive into the 18-Section Dossier (3:00 - 4:15)
1. **Visual**: Open the completed **Strategic Legal Intelligence Dossier**.
2. **Highlight Feature 1: Tri-Tier Grounding Badges**:
   - Scroll through Section 4 (Statutory Foundation) and Section 5 (Precedent Analysis).
   - Point out `[SUPPORTED BY SOURCE]` badges on UCC § 2-615 and `[MODEL INFERENCE]` badges on strategic recommendations.
3. **Highlight Feature 2: Argument Battle ("Our Position vs Opposing Position")**:
   - Switch to the **Argument Battle** tab.
   - Show how the **Opponent Agent** proactively identified that the client's force majeure notice was sent 14 days late, creating a waiver vulnerability.
4. **Highlight Feature 3: Precedent Comparison Matrix**:
   - Switch to the **Precedent Matrix** tab.
   - Show the 9-column comparative table distinguishing *Hadley v. Baxendale* and Restatement § 356.
5. **Highlight Feature 4: Simulated Judicial Perspective & Critic Self-Correction**:
   - Switch to the **Judicial Perspective** tab showing the evidentiary strength gauge and judicial inquiries.
   - Point out the statutory ethical disclaimer emphasizing human decision-support.

---

### Minute 5: Architecture Defense & Academic Summary (4:15 - 5:00)
1. **Visual**: Switch to the **Architecture** tab in the sidebar.
2. **Narration**:
   > *"Under the hood, this is governed by LangGraph. If the Critic Agent flags an unsupported assertion or weak counterargument defense, the graph automatically loops back to the Strategy Agent for iterative revision before final report generation. LexIntel AI bridges the gap between theoretical multi-agent research and practical, high-stakes legal decision-making."*
3. **Concluding Statement**:
   > *"Thank you. We welcome your questions."*\n