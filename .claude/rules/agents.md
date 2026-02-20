# Agent Orchestration

## Available Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| planner | Implementation planning | Complex features, refactoring |
| tdd-guide | Test-driven development | New features, bug fixes |
| code-reviewer | Code review | After writing code |
| security-reviewer | Security analysis | Before commits, handling user data |
| build-error-resolver | Fix build errors | When pytest/uvicorn fails |

## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Bug fix or new feature - Use **tdd-guide** agent

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of new endpoint
2. Agent 2: Test writing for calculator change
3. Agent 3: Code review of service layer

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```
