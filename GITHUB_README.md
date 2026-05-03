# 🎓 Python & AI Learning Journey

## 📊 Progress Overview
- **Start Date**: April 27, 2026
- **Current Day**: Day 9
- **Phase**: Phase 2 - LangChain & LLMs
- **Status**: 🟢 Phase 2 Active - Prompt Engineering Complete

---

## 🗓️ Daily Projects

### ✅ Day 1: Smart Conversation Bot
**Date**: 2026-04-27  
**Technologies**: Python, OOP  
**Files**: [`day01_conversation_bot.py`](./day01_conversation_bot.py)

**What I Learned**:
- Python class design
- Function definition and usage
- User input/output handling
- List operations for conversation history

**Features**:
- Interactive conversation
- Response based on keywords
- Conversation history tracking
- Clean user interface

**Run It**:
```bash
python day01_conversation_bot.py
```

---

### ✅ Day 2: Todo List Manager
**Date**: 2026-04-28  
**Technologies**: Python, JSON, File I/O  
**Files**: [`day02_todo_manager.py`](./day02_todo_manager.py)

**What I Learned**:
- JSON data format and serialization
- File read/write operations with `with`
- List comprehensions for filtering
- Dictionary operations and CRUD patterns

**Features**:
- Add, view, complete, delete todos
- Priority levels (high/medium/low)
- Auto-save to JSON file
- Statistics dashboard

**Run It**:
```bash
python day02_todo_manager.py
```

---

### ✅ Day 3: Weather API Tool
**Date**: 2026-04-29  
**Technologies**: Python, requests, API, JSON  
**Files**: [`day03_weather_checker.py`](./day03_weather_checker.py)

**What I Learned**:
- HTTP GET requests with requests library
- API key authentication
- Nested JSON parsing
- Network error handling (timeout, connection errors)
- Demo mode design for offline usage

**Features**:
- Query real-time weather via OpenWeatherMap API
- Demo mode with mock data (no API key needed)
- Formatted weather output (temperature, humidity, wind, etc.)
- Graceful error handling for network issues

**Run It**:
```bash
python day03_weather_checker.py
```

---

### ✅ Day 4: Data Analyzer
**Date**: 2026-04-30  
**Technologies**: Python, CSV, Data Analysis  
**Files**: [`day04_data_analyzer.py`](./day04_data_analyzer.py)

**What I Learned**:
- CSV file reading and writing with csv module
- DictReader for column-based data access
- Data statistics (sum, average, sorting, grouping)
- Counter for frequency analysis
- String formatting for reports

**Features**:
- Auto-generate sample data if CSV doesn't exist
- Data preview with customizable row count
- Comprehensive statistics (total sales, product ranking, region distribution, monthly trends)
- ASCII bar charts for visualization
- Export reports to text files

**Run It**:
```bash
python day04_data_analyzer.py
```

---

### ✅ Day 5: Web Scraper
**Date**: 2026-05-01  
**Technologies**: Python, requests, BeautifulSoup, logging  
**Files**: [`day05_web_scraper.py`](./day05_web_scraper.py)

**What I Learned**:
- try-except-else-finally complete error handling
- Custom exception classes
- logging module configuration and usage
- Retry mechanism with exponential backoff
- BeautifulSoup HTML parsing

**Features**:
- Fetch web pages with retry logic (3 attempts)
- Parse HTML to extract title, paragraphs, links, images
- Custom exceptions for network and parse errors
- Comprehensive logging to file and console
- Demo mode for offline testing

**Run It**:
```bash
python day05_web_scraper.py
```

---

### ✅ Day 6: Library Management System
**Date**: 2026-05-02  
**Technologies**: Python, OOP (Inheritance, Class Methods), JSON  
**Files**: [`day06_library_system.py`](./day06_library_system.py)

**What I Learned**:
- Class inheritance with `super()`
- `@classmethod` for factory methods
- Object serialization with `to_dict()` / `from_dict()`
- Complex system design with multiple classes
- `__str__` magic method for readable output

**Features**:
- Book management (add, remove, list, search)
- Reader management with borrow limits
- Borrow/return system with due dates
- Borrow records tracking
- Statistics dashboard (books, categories, borrowed copies)
- Auto-save to JSON file
- Inheritance design: Person → Reader / Librarian

**Run It**:
```bash
python day06_library_system.py
```

---

### ✅ Day 7: Finance Tracker
**Date**: 2026-05-03  
**Technologies**: Python, OOP, JSON, Data Analysis  
**Files**: [`day07_finance_tracker.py`](./day07_finance_tracker.py)

**What I Learned**:
- Comprehensive application of all Phase 1 knowledge
- `defaultdict` with lambda for complex structures
- `datetime` for date manipulation and filtering
- Budget tracking system design
- Monthly/yearly report generation
- Progress bar visualization with ASCII characters

**Features**:
- Record income and expenses with categories
- Predefined income/expense categories
- Transaction filtering by type and date range
- Monthly reports with category breakdown and charts
- Yearly reports with monthly summary table
- Budget management with spending tracking and alerts
- Asset overview with recent transactions
- Auto-save to JSON file

**Run It**:
```bash
python day07_finance_tracker.py
```

---

### ✅ Day 8: AI Chat Assistant (DashScope)
**Date**: 2026-05-04  
**Technologies**: Python, DashScope API, python-dotenv  
**Files**: [`day08_openai_chat.py`](./day08_openai_chat.py)

**What I Learned**:
- DashScope (Alibaba Bailian) API basics
- OpenAI-compatible API format
- Chat completions with message roles
- Conversation history management
- Environment variable management
- Demo mode design

**Features**:
- Free-form conversation with context memory
- Translation, summarization, article writing, code explanation
- Demo mode when no API key

**Run It**:
```bash
python day08_openai_chat.py
```

---

### ✅ Day 9: Prompt Engineering
**Date**: 2026-05-05  
**Technologies**: Python, Prompt Engineering Techniques  
**Files**: [`day09_prompt_engineering.py`](./day09_prompt_engineering.py)

**What I Learned**:
- Role prompting for specialized responses
- Few-shot learning with examples
- Chain-of-thought reasoning
- Structured output (JSON/Markdown)
- Tree of thoughts for multi-solution exploration
- Self-consistency through multiple sampling
- Reflection and self-improvement
- Prompt templates and comparison

**Features**:
- 8 prompt engineering techniques in one tool
- Side-by-side prompt comparison
- Few-shot classification and extraction
- Structured JSON/Markdown generation
- Multi-solution analysis with Tree of Thoughts
- Self-consistency verification
- Reflection-based improvement

**Run It**:
```bash
python day09_prompt_engineering.py
```

---

### 📅 Upcoming Days

| Day | Project | Status |
|-----|---------|--------|
| Day 10 | RAG Systems | 📋 Planned |

---

## 🎯 30-Day Learning Roadmap

### Phase 1: Python Basics (Day 1-7) ✅ Complete
- [x] Day 1: Conversation Bot
- [x] Day 2: Todo List Manager
- [x] Day 3: Weather API Tool
- [x] Day 4: Data Analyzer
- [x] Day 5: Web Scraper
- [x] Day 6: Library Management System
- [x] Day 7: Finance Tracker

### Phase 2: LangChain & LLMs (Day 8-14) 🟢 Active
- [x] Day 8: DashScope API Integration
- [x] Day 9: Prompt Engineering
- [ ] Day 10: RAG Systems
- [ ] Day 11-14: AI Agents

### Phase 3: Advanced Agents (Day 15-21) ⚪ Upcoming
- ReAct Pattern
- Multi-Agent Systems
- Web Automation
- Database Queries

### Phase 4: Real Projects (Day 22-30) ⚪ Upcoming
- Knowledge Base System
- AI Content Platform
- Portfolio Optimization

---

## 💡 Key Learnings

### Python Concepts Mastered
- ✅ Classes and Objects
- ✅ Functions
- ✅ Lists and Dictionaries
- ✅ File Operations (JSON read/write)
- ✅ API Integration (requests, HTTP)
- ✅ Data Analysis (CSV processing, statistics)
- ✅ Error Handling (try-except, logging, retry)
- ✅ OOP Advanced (inheritance, class methods, serialization)
- ✅ Comprehensive Project (finance tracker with all Phase 1 skills)

### Skills Developing
- ✅ API Integration
- ✅ Data Analysis
- ✅ Python Fundamentals (Complete)
- ✅ DashScope API Integration
- ✅ Prompt Engineering
- 🔄 RAG Systems
- 🔄 LangChain Framework

---

## 🚀 Next Steps

**Tomorrow's Goal**: RAG Systems - Build document-based Q&A

**Skills to Practice**:
- Vector databases
- Document retrieval
- Embedding vectors
- Knowledge base Q&A

---

## 📝 Reflections

**Day 9 Thoughts**:
> Today I learned that talking to AI is itself a skill! Prompt Engineering completely changed how I think about AI interactions. The biggest insight: AI isn't mind-reading - the clearer your prompt, the better the output. I practiced 8 different techniques and was amazed how much difference a well-crafted prompt makes. Few-shot learning is like teaching by example, and Chain-of-Thought makes the AI actually "think" step by step instead of jumping to conclusions.

**Challenges Faced**:
- Designing effective few-shot examples
- Balancing temperature for different tasks
- Getting consistent structured JSON output
- Understanding when to use each technique

**Breakthroughs**:
- Mastered 8 core prompt engineering techniques
- Built a comprehensive prompt testing tool
- Understood the power of role prompting
- Learned to design prompts for structured output

---

**Day 8 Thoughts**:
> Today I built my first real AI application using OpenAI API! It's amazing how simple the API is - just `client.chat.completions.create()` with the right messages. The key insight is that AI has no memory, so I need to manually maintain and send conversation history. I also learned about System Prompts which act like the AI's "personality setting" - different prompts make the AI behave completely differently (translator vs writer vs code expert).

**Challenges Faced**:
- Understanding that AI is stateless and needs full context each time
- Managing API keys securely with environment variables
- Designing a demo mode for users without API keys

**Breakthroughs**:
- Successfully called OpenAI API and got intelligent responses
- Built a multi-functional AI assistant (chat, translate, summarize, write, explain code)
- Understood the power of System Prompts for controlling AI behavior

---

## 🎉 Phase 1 Complete!

**What I've Built**:
1. Conversation Bot - Python basics
2. Todo Manager - File I/O and JSON
3. Weather Tool - API integration
4. Data Analyzer - CSV processing
5. Web Scraper - Error handling and logging
6. Library System - OOP inheritance
7. Finance Tracker - Comprehensive project
8. AI Chat Assistant - DashScope API integration
9. Prompt Engineering - 8 prompt techniques

**Skills Mastered**:
- Python syntax and data structures
- Object-oriented programming
- File operations and JSON
- API calls and HTTP
- Error handling and logging
- Data analysis and visualization

---

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **IDE**: VS Code / PyCharm
- **Libraries**: Built-in Python modules
- **Version Control**: Git & GitHub

---

## 📫 Connect With Me

- GitHub: [@YourUsername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)
- Blog: [Your Blog](https://yourblog.com)

---

## 📜 License

This learning journey is open source. Feel free to learn alongside me!

---

<div align="center">
  <strong>⭐ Star this repo to follow my learning journey! ⭐</strong>
</div>

<div align="center">
  <em>"AI won't replace you, but someone who uses AI will."</em>
</div>
