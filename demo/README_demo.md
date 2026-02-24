# ContextWeave Coach - Demo Guide

## 5-Minute Demo Flow

This guide walks you through a complete demo of ContextWeave Coach's learning features.

### Prerequisites

1. **Backend Running**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

2. **Extension Installed**
   - Open `vscode-extension` folder in VS Code
   - Press `F5` to launch Extension Development Host
   - Or: `npm install && npm run compile` then install VSIX

3. **LLM Provider Configured**
   - **Option A (Local):** `ollama serve` + `ollama pull llama3`
   - **Option B (Cloud):** Add Groq API key to `backend/.env`

---

## Demo Script

### 1. Open Demo Workspace (30 seconds)

```bash
# In Extension Development Host window:
File → Open Folder → Select the demo/ folder
```

You should see:
- `lab1_binary_search.py`
- `rubric.json`

### 2. Progressive Hints (90 seconds)

**Action:** Open `lab1_binary_search.py`, select the `binary_search` function

**Command:** `Ctrl+Shift+P` → "ContextWeave: Explain Selection (Progressive Hints)"

**What happens:**
- Level 1 hint appears: "This implements binary search..."
- Click "Next Level Hint" → See logical breakdown
- Click again → See line-by-line explanation
- Notice mastery sidebar updates with "binary-search" topic

**Key point:** "See how hints progress from conceptual to detailed? This encourages active learning."

### 3. Mastery Tracking (60 seconds)

**Action:** Click on "Mastery Tracker" in the sidebar

**What to show:**
- Topic scores (0-5 scale)
- Progress bars with color coding
- "Review" badges on weak topics
- Exam readiness indicators

**Key point:** "The system tracks your learning. Using Level 3 hints lowers your score, solving without hints raises it."

### 4. Multilingual Support (30 seconds)

**Action:** 
1. Open Settings (`Ctrl+,`)
2. Search "ContextWeave"
3. Change `language` to `hi` (Hindi)
4. Run explain command again

**What happens:**
- Same code, but explanation in Hindi
- Technical terms stay in English
- Demonstrates India-first approach

**Key point:** "Students can learn in their native language while keeping code in English."

### 5. Lab Evaluation (90 seconds)

**Command:** `Ctrl+Shift+P` → "ContextWeave: Evaluate Current Lab"

**What happens:**
- System finds `rubric.json` and `lab1_binary_search.py`
- Evaluates against criteria
- Shows rubric table with:
  - Correctness: Partial (missing edge cases)
  - Style: Met (good naming)
  - Documentation: Not Met (no docstrings)
  - Overall: ~65%

**Key point:** "AI provides specific, actionable feedback. Not just 'wrong' but 'why' and 'how to improve'."

### 6. Spaced Repetition (30 seconds)

**Command:** `Ctrl+Shift+P` → "ContextWeave: What Should I Review Today?"

**What happens:**
- Shows topics due for review
- Based on mastery scores and time since last practice
- Weak topics (score < 3) appear daily
- Strong topics (score > 4) appear weekly

**Key point:** "The system schedules reviews like Duolingo. You don't forget what you learned."

### 7. Exam Mode (45 seconds)

**Action:** Click status bar item "Learning Mode" or run "Toggle Exam Mode"

**What happens:**
- Status bar shows "🔒 Exam Mode"
- Try to get hints → Only Level 1 available
- Chat refuses detailed solutions
- Ensures fair assessment

**Key point:** "During exams, the system restricts itself. Academic integrity built-in."

### 8. Tutor Chat (60 seconds)

**Command:** `Ctrl+Shift+P` → "ContextWeave: Open Tutor Chat"

**Try these:**
- "Explain this code" (with selection)
- "Why is binary search O(log n)?"
- "Write me the complete solution" → Refuses!

**What happens:**
- Context-aware responses
- Guides with questions, not answers
- Knows your mastery level
- Adapts explanations

**Key point:** "It's a tutor, not a solution generator. Teaches you to think."

---

## Key Talking Points

### For Judges

1. **Learning Loop:** Code → Hints → Mastery → Spaced Review → Exam Ready
2. **Explainable AI:** Every score has a reason, every decision cites evidence
3. **India-First:** Hindi support, works offline, optimized for learning
4. **Academic Integrity:** Exam mode, gentle nudges, encourages originality
5. **Measurable Impact:** Tracks growth, shows readiness, proves learning

### Differentiation

| Feature | ChatGPT | GitHub Copilot | ContextWeave Coach |
|---------|---------|----------------|-------------------|
| Progressive hints | ❌ | ❌ | ✅ |
| Mastery tracking | ❌ | ❌ | ✅ |
| Spaced repetition | ❌ | ❌ | ✅ |
| Exam mode | ❌ | ❌ | ✅ |
| Multilingual learning | ❌ | ❌ | ✅ |
| Rubric evaluation | ❌ | ❌ | ✅ |

### The Narrative

"Most AI tools give you fish. ContextWeave Coach teaches you to fish. It's Duolingo for code - progressive hints that scaffold learning, mastery tracking that shows growth, and spaced repetition that ensures you remember. Built for Indian students who need to learn, not just copy-paste."

---

## Troubleshooting

**Backend not responding:**
```bash
# Check if running
curl http://localhost:8000

# Restart
cd backend
python main.py
```

**Ollama not working:**
```bash
# Check status
ollama list

# Start server
ollama serve

# Pull model
ollama pull llama3
```

**Extension not loading:**
```bash
# Recompile
cd vscode-extension
npm run compile

# Check logs
View → Output → Select "ContextWeave"
```

---

## After Demo

**Next steps for judges:**
1. Try with their own code
2. Test different languages
3. Evaluate a real lab
4. Check mastery tracking over time

**Questions to ask:**
- "How would this help your students?"
- "What features would you add?"
- "How does this compare to existing tools?"

---

**Demo time: 5-7 minutes**  
**Setup time: 2-3 minutes**  
**Total: < 10 minutes**

Perfect for hackathon presentations!
