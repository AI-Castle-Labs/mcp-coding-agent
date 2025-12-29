# MCP Coding Agent - VentureBot Integration

## Summary
Updated the MCP coding agent to use VentureBot repository instead of the music recommendation system for testing and analysis.

## Changes Made

### 1. Test File Updates (`test/test_second_builder.py`)
- **Changed default repository**: From `agentic-ai-music-recommendation-system` to `VentureBot`
- **Updated repository owner**: Set to `ashcastelinocs124` (VentureBot owner)
- **Updated test file paths**: Changed to match VentureBot structure:
  - `main.py`
  - `services/api_gateway/app/main.py`
  - `services/orchestrator/chat_orchestrator.py`
  - `crewai-agents/src/venturebot_crew/main.py`

### 2. Documentation Updates (`agents.md`)
- Updated test documentation to reflect VentureBot as the test repository
- Clarified repository owner and structure

## Repository Information
- **Repository**: VentureBot
- **Owner**: ashcastelinocs124
- **URL**: https://github.com/ashcastelinocs124/VentureBot.git
- **Description**: AI Entrepreneurship Coach - Multi-agent system powered by CrewAI

## Usage

### Running Tests
```bash
cd mcp-coding-agent
python test/test_second_builder.py
```

### Running Main Analysis
```bash
cd mcp-coding-agent/src
python main.py VentureBot --owner ashcastelinocs124
```

## Requirements
- `GITHUB_TOKEN` environment variable set
- `OPENAI_API_KEY` (optional, for LLM summarization)
- Network access to GitHub API

## VentureBot Structure
The repository contains:
- `services/` - FastAPI gateway + orchestrator + tools
- `crewai-agents/` - CrewAI blueprint (agents/tasks YAML)
- `frontend/` - React/Vite SPA
- `main.py` - Entry point
- Multiple Python files for analysis

