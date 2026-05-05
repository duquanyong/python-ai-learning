# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal Python & AI learning journey repo (30-day curriculum). Each day adds a new self-contained Python project demonstrating specific concepts. The repo is used for learning Python fundamentals, API integration, data analysis, LangChain, and AI agent development.

- **Language**: Python 3.12
- **Learning start date**: April 27, 2026
- **Current progress**: Day 12 (Phase 2: LangChain & LLMs)

## Running Code

### Virtual Environment
A virtual environment exists at `.venv/`. On Windows (bash shell), activate it with:
```bash
source .venv/Scripts/activate
```

### Run a Daily Project
Each day is a standalone script. Run directly with Python:
```bash
python day01_conversation_bot.py
python day02_todo_manager.py
python day03_weather_checker.py
python day04_data_analyzer.py
python day05_web_scraper.py
python day06_library_system.py
python day07_finance_tracker.py
python day08_openai_chat.py
python day09_prompt_engineering.py
python day10_rag_system.py
python day11_langchain_basics.py
python day12_memory_system.py
```

### Install Dependencies
```bash
# Already installed: requests, pandas, matplotlib, beautifulsoup4
# Phase 1 complete (Day 1-7)

# Phase 2-3 (LangChain & AI)
pip install langchain langchain-openai openai python-dotenv

# Phase 3-4 (Web apps)
pip install fastapi streamlit python-dotenv
```

## Project Structure & Conventions

### Naming Pattern
Daily projects follow the naming convention `dayNN_<descriptive_name>.py` (e.g., `day01_conversation_bot.py`). Each file is self-contained with:
- A module docstring describing the day's learning goal
- A main class encapsulating the day's feature
- A `main()` function for interactive CLI usage
- `if __name__ == "__main__": main()` guard

### Data Persistence
- Day 2+ projects use JSON files for local data storage (e.g., `todos.json`). These are committed to git as sample data.

### API Keys
- Day 3 (weather) uses OpenWeatherMap API. The script supports a demo mode (no API key required) and accepts API keys via interactive input at runtime.
- Day 8+ (LangChain/OpenAI) uses OpenAI API. These scripts require an API key via environment variable (`OPENAI_API_KEY`) or interactive input. Do not hardcode API keys in source files.

### Learning Notes
Each day has an accompanying `dayNN学习笔记.md` file with study notes in Chinese. When adding new days, follow this pattern and update `GITHUB_README.md` progress tracking.

## Curriculum Roadmap

| Phase | Days | Focus |
|-------|------|-------|
| Phase 1 | Day 1-7 | Python basics (OOP, file I/O, APIs, pandas, error handling) |
| Phase 2 | Day 8-14 | LangChain & LLMs (OpenAI API, prompts, RAG, memory, tools) |
| Phase 3 | Day 15-21 | AI Agents (ReAct, multi-agent, web automation, DB queries) |
| Phase 4 | Day 22-30 | Real projects (knowledge base, AI content platform, portfolio) |

Reference `LEARNING_PATH.md` for the full curriculum and `GITHUB_README.md` for current progress.
