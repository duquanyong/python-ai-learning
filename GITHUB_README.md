# 🎓 Python & AI Learning Journey

## 📊 Progress Overview
- **Start Date**: April 27, 2026
- **Current Day**: Day 6
- **Phase**: Python Fundamentals
- **Status**: 🚀 In Progress

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

### 📅 Upcoming Days

| Day | Project | Status |
|-----|---------|--------|
| Day 7 | Finance Tracker | 📋 Planned |

---

## 🎯 30-Day Learning Roadmap

### Phase 1: Python Basics (Day 1-7) 🟢 Active
- [x] Day 1: Conversation Bot
- [x] Day 2: Todo List Manager
- [x] Day 3: Weather API Tool
- [x] Day 4: Data Analyzer
- [x] Day 5: Web Scraper
- [x] Day 6: Library Management System
- [ ] Day 7: Finance Tracker

### Phase 2: LangChain & LLMs (Day 8-14) ⚪ Upcoming
- OpenAI API Integration
- Prompt Engineering
- RAG Systems
- AI Agents

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
- ⏳ Comprehensive Project (Coming Day 7)

### Skills Developing
- ✅ API Integration
- ✅ Data Analysis
- 🔄 Prompt Engineering
- 🔄 LangChain Framework

---

## 🚀 Next Steps

**Tomorrow's Goal**: Comprehensive Project - Personal Finance Tracker

**Skills to Practice**:
- Apply all Phase 1 knowledge
- Complex data modeling
- Income/expense categorization
- Monthly/yearly reports

---

## 📝 Reflections

**Day 6 Thoughts**:
> Today I learned OOP advanced concepts like inheritance and class methods. The library management system is the most complex project so far, with 5 classes working together. I now understand how inheritance reduces code duplication - Reader and Librarian both inherit from Person, so I don't need to repeat name and id_card in each class.

**Challenges Faced**:
- Designing the class hierarchy (what goes in parent vs child classes)
- Understanding when to use @classmethod vs instance methods
- Implementing to_dict/from_dict for JSON serialization

**Breakthroughs**:
- Successfully designed a multi-class system with inheritance
- Implemented complete serialization/deserialization
- Understood the power of super() for code reuse

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
