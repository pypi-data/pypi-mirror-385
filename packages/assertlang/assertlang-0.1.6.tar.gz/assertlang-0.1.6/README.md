<p align="center">
  <img src=".github/assets/logo2.svg" alt="AssertLang Logo" width="200" height="200">
</p>

<h1 align="center">AssertLang</h1>

<p align="center">

[![PyPI](https://img.shields.io/pypi/v/assertlang?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/assertlang/)
[![Tests](https://github.com/AssertLang/AssertLang/actions/workflows/test.yml/badge.svg)](https://github.com/AssertLang/AssertLang/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)

</p>

<p align="center"><strong>Executable contracts for multi-agent systems.</strong> Define agent behavior once in AL, agents from different frameworks (CrewAI, LangGraph, AutoGen) execute identical logic. <strong>Deterministic coordination guaranteed.</strong></p>

<p align="center">
  <a href="https://assertlang.dev">Website</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#why-i-built-this">Why I Built This</a> •
  <a href="examples/agent_coordination/">Examples</a> •
  <a href="#contributing">Contribute</a>
</p>

---

## 👋 Hey there!

I'm David, and I built AssertLang. Full disclosure: **I'm not a "real" software engineer.** I'm a broadcast tech from Hamilton who saw a problem and decided to try building a solution.

**The honest truth:** I couldn't have built this alone. Claude Code helped massively. But that's kind of the point—if someone like me can build something that actually works, maybe we're onto something useful here.

**What I'm hoping for:** Genuine feedback. Does this solve a real problem for you? Is it useful? What's broken? What should I add? I'm not trying to build a unicorn startup—I'm trying to see if this idea is actually helpful to developers building multi-agent systems.

**Current status:** v0.0.3 - Core transpiler works (5 languages!), 134/134 stdlib tests passing, CLI functional. Some integration tests still need work. It's early, but it's real.

⭐ **If you find this interesting, please star the repo!** It helps me know I'm building something people actually want.

---

## The Problem

Multi-agent AI systems are growing fast ($5.25B → $52.62B by 2030), but agents can't reliably coordinate:

**What happens today:**

```python
# Agent A (Python/CrewAI) interprets "create user"
def create_user(name, email):
    if not name:  # Agent A's validation
        raise ValueError("Missing name")
    # ... creates user
```

```javascript
// Agent B (JavaScript/LangGraph) interprets same task differently
function createUser(name, email) {
    if (name === "")  // Agent B's validation (different!)
        throw new Error("Name is required");
    // ... creates user (differently)
}
```

**Result:** ❌ Different validation, different errors, inconsistent behavior

**Existing solutions:**
- **MCP, A2A, ACP** - Handle messaging, NOT semantic contracts
- **JSON Schema** - Types only, no business logic
- **Natural language** - Ambiguous, unreliable
- **LLM interpretation** - Non-deterministic

---

## The Solution: AssertLang Contracts

**Define behavior once, execute everywhere:**

```al
// user_service.al - Contract defines EXACT behavior
function createUser(name: string, email: string) -> User {
    // Deterministic validation (not just types!)
    if (str.length(name) < 1) {
        return ValidationError("name", "Name cannot be empty");
    }

    if (!str.contains(email, "@")) {
        return ValidationError("email", "Invalid email format");
    }

    // Deterministic ID generation
    let id = str.length(name) + str.length(email);

    return User(id, name, email, timestamp());
}
```

**Transpile to Agent A (Python/CrewAI):**
```bash
asl build user_service.al --lang python -o agent_a.py
```

**Transpile to Agent B (JavaScript/LangGraph):**
```bash
asl build user_service.al --lang javascript -o agent_b.js
```

**Result:** ✅ Both agents execute IDENTICAL logic

---

## Proof: 100% Identical Behavior

**Test Case:** `createUser("Alice Smith", "alice@example.com")`

**Agent A (Python) Output:**
```
✓ Success: User #28: Alice Smith <alice@example.com>
```

**Agent B (JavaScript) Output:**
```
✓ Success: User #28: Alice Smith <alice@example.com>
```

**Same ID, same format, same validation.** [See proof](examples/agent_coordination/PROOF_OF_DETERMINISM.md)

---

## 🚀 Quick Start (2 Minutes)

### 1. Install

```bash
pip install assertlang
```

### 2. Write a contract

```bash
cat > hello_contract.al << 'EOF'
function greet(name: string) -> string {
    if (str.length(name) < 1) {
        return "Hello, Guest!";
    }
    return "Hello, " + name + "!";
}
EOF
```

### 3. Generate for your framework

```bash
# For CrewAI (Python)
asl build hello_contract.al --lang python -o crewai_agent.py

# For LangGraph (JavaScript)
asl build hello_contract.al --lang javascript -o langgraph_agent.js

# For custom agents (Go, Rust, C#)
asl build hello_contract.al --lang go -o agent.go
```

### 4. Use in your agent framework

**CrewAI example:**
```python
from crewai import Agent
from crewai_agent import greet  # Uses AL contract

agent = Agent(
    role='Greeter',
    goal='Greet users consistently',
    backstory='I implement the AL greeting contract'
)

# Guaranteed to match other agents implementing same contract
result = greet("Alice")  # "Hello, Alice!"
```

---

## 💡 Why I Built This

I've been watching the multi-agent AI space explode. Everyone's building agents with CrewAI, LangGraph, AutoGen—but they can't talk to each other reliably.

When Agent A (Python) and Agent B (JavaScript) are supposed to do the same thing, they interpret it differently. Same task, different validation, different errors, chaos.

I thought: **What if agents could share executable contracts?** Not just type schemas, but actual behavior. Write it once, transpile to any language, guarantee identical execution.

So I built it. With a lot of help from Claude Code (seriously, this wouldn't exist without it).

**Is it useful?** That's what I'm trying to figure out. If you're building multi-agent systems and this solves a problem for you, I want to hear about it. If it doesn't, I want to hear that too.

---

## ✨ What Actually Works (v0.0.3)

I'm trying to be transparent about what's ready vs. what's still cooking:

### ✅ Production Ready:
- **5 Language Transpilation:** Python, JavaScript, Go, Rust, C# all compile successfully
- **Standard Library:** 134/134 tests passing (Option, Result, List, Map, Set)
- **CLI:** Full end-to-end workflow (`pip install` → `asl build` → working code)
- **Proof of Concept:** Real examples showing 100% identical behavior (not fake!)
- **Framework Integration:** CrewAI and LangGraph examples working

### 🚧 In Progress:
- Additional framework integrations (AutoGen, LangChain)
- VS Code extension improvements
- More comprehensive integration tests
- Performance optimizations

### 📊 Test Results (Verified):
```
✅ 134/134 stdlib tests passing (100%)
✅ 1457 total tests collected
✅ 5 languages verified working
✅ End-to-end CLI workflow tested
```

---

## 🎯 Use Cases

### 1. Multi-Framework Coordination

**Challenge:** CrewAI agent (Python) and LangGraph agent (JavaScript) need to coordinate

**Solution:**
```bash
# Define contract
cat > task_contract.al
# Both agents transpile from same contract
asl build task_contract.al --lang python
asl build task_contract.al --lang javascript
# Guaranteed coordination ✅
```

### 2. Framework Migration

**Challenge:** Migrating from CrewAI to LangGraph without breaking behavior

**Solution:**
- Extract CrewAI logic to AL contract
- Transpile to LangGraph
- Verify identical behavior
- Migrate incrementally

### 3. Cross-Team Collaboration

**Challenge:** Python team and JavaScript team can't share specifications

**Solution:** AL contracts as shared source of truth
- One contract file
- Each team generates their language
- Behavior guaranteed identical

---

## 🌍 Language Support

AL contracts transpile to:

| Language | Status | Use For |
|----------|--------|---------|
| **Python** | ✅ Production | CrewAI, AutoGen, LangChain |
| **JavaScript** | ✅ Production | LangGraph, Node.js agents |
| **Go** | ✅ Production | High-performance agents |
| **Rust** | ✅ Production | Performance-critical agents |
| **C#** | ✅ Production | Windows/enterprise agents |

**All languages:**
- 100% semantic equivalence
- Deterministic behavior
- Full type annotations
- Production-ready code generation

---

## 🤝 Contributing

**I need your help!** Here's the honest truth: this is a solo project (with AI assistance), and I'm figuring things out as I go.

### Ways You Can Help:

**1. Try it out and tell me what breaks**
```bash
pip install assertlang
asl build --help
# Then let me know what happened!
```

**2. Open issues for:**
- Bugs you find (there are definitely bugs!)
- Features you need (what's missing?)
- Documentation that's confusing (where did you get stuck?)
- Ideas for improvement (what would make this more useful?)

**3. Contribute code:**
- Fix bugs
- Add framework integrations
- Improve documentation
- Write examples

**4. Share feedback:**
- Does this solve a real problem for you?
- What frameworks do you use?
- What languages do you need?
- What's your multi-agent coordination pain point?

### I Promise:

- **Respond to all issues** (might take a day or two, but I'll respond)
- **Be open to feedback** (tell me what's wrong, I won't be offended)
- **Give credit** (every contributor gets recognized)
- **Keep it simple** (no corporate BS, just building something useful)

**Not sure where to start?** Look for issues tagged `good-first-issue` or just open an issue saying "I want to help!" and I'll find something.

---

## 📚 Real-World Example

See complete working example: [examples/agent_coordination/](examples/agent_coordination/)

**What's included:**
- User service contract (validation, creation, formatting)
- CrewAI agent (Python) implementation
- LangGraph agent (JavaScript) implementation
- Proof of identical behavior (100% match on all tests)
- Integration guides

**Run it yourself:**
```bash
cd examples/agent_coordination
python agent_a_crewai.py      # Agent A output
node agent_b_langgraph.js      # Agent B output
# Compare - they're identical!
```

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────┐
│           AL Contract (Source of Truth)         │
│   function createUser(name, email) -> User     │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────┴────────┐
         │  AssertLang     │
         │  Transpiler     │
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Python  │  │JavaScript│  │   Go    │
│ (CrewAI)│  │(LangGraph│  │ (Custom)│
└─────────┘  └─────────┘  └─────────┘

All execute IDENTICAL logic
```

**Under the hood:**
1. Parse AL contract
2. Extract semantic requirements
3. Generate idiomatic code for each language
4. Guarantee behavioral equivalence

---

## 💬 Get in Touch

**Want to chat about multi-agent systems?** I'm always happy to talk!

- **GitHub Issues:** [Open an issue](https://github.com/AssertLang/AssertLang/issues) (best way to reach me)
- **GitHub Discussions:** [Start a discussion](https://github.com/AssertLang/AssertLang/discussions)
- **Twitter/X:** [@davidhustler](https://twitter.com/davidhustler) (DMs open)
- **Email:** hello@assertlang.dev

**I'm especially interested in hearing from you if:**
- You're building multi-agent systems and hitting coordination problems
- You've tried AssertLang and have feedback (good or bad!)
- You want to contribute but aren't sure how
- You have ideas for making this more useful

---

## 📝 License

MIT © AssertLang Contributors

Built with ❤️ (and lots of Claude Code assistance) for the multi-agent AI community.

---

## 🙏 Acknowledgments

**Huge thanks to:**
- **Claude (Anthropic)** - for making it possible for non-"real" engineers to build real tools
- **The multi-agent AI community** - for inspiration and showing the need for this
- **Early testers** - for trying this out and giving honest feedback (you know who you are!)
- **Everyone who's starred the repo** - it genuinely motivates me to keep building

---

## 🎯 Current Status & Roadmap

### v0.0.4 (Current) ✅
- Core transpiler working (5 languages)
- 134/134 stdlib tests passing
- CLI functional end-to-end (fixed critical import bug!)
- CrewAI & LangGraph examples
- Proof of identical behavior verified

### v0.1.0 (Next) 🎯
- [ ] Fix remaining integration test issues
- [ ] Add AutoGen integration
- [ ] Improve VS Code extension
- [ ] Add more framework examples
- [ ] Performance benchmarking

### v0.2.0 (Future) 💭
- [ ] Contract testing framework
- [ ] Additional language targets (Java, PHP)
- [ ] Cloud-hosted transpilation service
- [ ] Enterprise support options

**Want to influence the roadmap?** [Open an issue](https://github.com/AssertLang/AssertLang/issues) and tell me what you need!

---

<p align="center">
  <strong>Built by one person, trying to solve a real problem.</strong><br>
  If this helps you, that makes it all worth it. ⭐
</p>

<p align="center">
  <a href="https://github.com/AssertLang/AssertLang/issues/new">Report Bug</a> •
  <a href="https://github.com/AssertLang/AssertLang/issues/new">Request Feature</a> •
  <a href="https://assertlang.dev">Visit Website</a>
</p>
