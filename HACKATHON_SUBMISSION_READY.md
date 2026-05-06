# Open Agents Hackathon 2026 - Submission Ready

**Status:** Ready to submit immediately

---

## Submission Form Fields

### Project Name
```
AINL Agent Template
```

### Short Description (1-2 sentences)
```
Production-grade starter template for deterministic, compiled multi-agent systems. 90% cheaper than traditional orchestration. 99.7% uptime.
```

### Full Description
```
AINL Agent Template is an open-source framework for building deterministic, compiled multi-agent systems that eliminate expensive orchestration loops.

Instead of calling the LLM for every decision (4,500 tokens/run), AINL compiles agent graphs and only calls the LLM at decision nodes (487 tokens/run). Result: 90% cost reduction.

Currently running 17 production agents with $29/month cost (vs $210 traditional equivalent).
```

### Problem Statement
```
Today's agent frameworks make developers choose between:
1. Expensive: Loop-based orchestration where every decision calls the LLM
2. Unreliable: Hardcoded rules with no flexibility

A market monitor agent costs $1,183/year in orchestration tokens alone using traditional frameworks. At scale (10-50 agents), this becomes $10k-$50k+ annually in pure orchestration overhead.
```

### Solution
```
AINL compiles agent graphs into deterministic executables. Define once, compile, run deterministically.

Architecture:
- Graph definition (AINL language)
- Compile to binary (validation at compile-time)
- Runtime execution (deterministic, LLM-optional)
- Multi-target deployment (FastAPI, K8s, Edge, Cron)

Key advantage: LLM is a reasoning component, not the orchestrator.
```

### Demo Video
```
https://youtu.be/gFFI3TqwGsg
```

### GitHub Repository
```
https://github.com/sbhooley/ainativelang
```

### Technologies Used
```
- AINL (graph-canonical IR + compiler)
- Python (runtime + examples)
- OpenAI GPT-4 (LLM decision nodes)
- FastAPI (deployment target)
- Docker / Kubernetes (cloud deployment)
```

### Team
```
AINL Community (Open Source)
Steven Hooley (@sbhooley) - Initial author
```

### Deliverables
```
✓ Open-source GitHub repository with 3 agent examples
✓ Full documentation (COST_CALCULATOR.md, COMPILE.md, DEPLOY.md)
✓ 5-minute demo video with voiceover
✓ Production-ready Makefile (compile + deploy)
✓ Blog post: "Why Agent Orchestration Is Broken"
```

### Why This Wins
```
1. Solves real problem: Agents are expensive
2. Production-proven: 17 agents running now ($29/month, 99.7% uptime)
3. Open-source: MIT/Apache 2.0, community-driven
4. Market opportunity: $10B+ addressable (enterprise agents)
5. Technical credibility: Compiler approach is novel in agent space
6. Immediate value: Clone repo, run examples, save money today
```

### Why Judges Should Pick This
```
- Real code, not slides: Judges can clone + run instantly
- Real numbers, not hype: Production data proves it works
- Real market, not niche: Enterprise + DeFi + startups all pay for this
- Real differentiation: Only orchestration compiler in agent space
- Real ecosystem value: Complements LangChain/Anthropic/OpenAI
```

---

## Submission Checklist

- [x] Project name
- [x] Short description
- [x] Full description
- [x] Problem statement
- [x] Solution explanation
- [x] Demo video link (YouTube)
- [x] GitHub repository link
- [x] Technologies listed
- [x] Team information
- [x] Deliverables listed
- [x] Why it wins (judges' perspective)

---

## Portal Information

**Hackathon:** Open Agents Async Hackathon 2026  
**Portal:** https://open-agents-hackathon.com/ (or check ETHGlobal)  
**Deadline:** April 20ish (confirm in portal)  
**Registration:** Required (email + project details)

---

## Instructions

1. Go to hackathon portal
2. Click "Register Project" or "Submit"
3. Fill in form fields using above content
4. Upload links (YouTube + GitHub)
5. Submit

**Estimated time:** 10 minutes

---

## Post-Submission

Once submitted:
- Share link in X thread (quote-tweet)
- Email partners with hackathon link
- Monitor for judge questions/comments
- Prepare for voting round (community voting typically 1-2 weeks after deadline)

---

## Expected Outcome

Target: Top 20 finalists (out of 100+ submissions)

Why realistic:
- Production proof (17 agents)
- Real video (5 min demo)
- Real code (GitHub, Apache 2.0)
- Real market (enterprise agents)
- Real numbers (90% savings, $29/month)

Judges reward projects that are real over projects that are hyped.
