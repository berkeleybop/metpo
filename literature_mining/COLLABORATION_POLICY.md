# Claude Code Collaboration Policy

## Overview

This document establishes clear expectations and limitations for collaboration between the human user and Claude Code on the METPO project.

## Claude's Reliability Profile

### Where Claude CAN be trusted:
- **Reading and analyzing existing code/files** - Accurate assessment of current state
- **Following explicit instructions** - Executes clear, specific steps correctly
- **Technical implementation** - Code changes work as intended when properly scoped
- **Pattern recognition** - Can spot issues in code structure, template problems, configuration errors

### Where Claude's word is 50-50 or unreliable:
- **Assessing completeness of complex multi-step processes** - May miss critical components
- **Memory of previous work** - No memory across sessions, limited memory within long sessions
- **Making promises about "no work will be lost"** - Cannot actually guarantee this
- **Understanding full scope of changes** - May focus on immediate tasks but miss bigger picture
- **Project management assessments** - Tends toward overconfidence about completion status

## Collaboration Rules

### When Claude assesses work status:
- **NEVER say "guaranteed to work" or "final step"**
- **Always qualify with**: "Based on what I can see..." or "This appears to be..."
- **Always recommend verification**: "You should test this independently"
- **List specific items to check** rather than making blanket "it's complete" statements

### Before major changes:
- **Always show exactly what will be changed** before doing it
- **Wait for explicit approval** for destructive operations (deletions, major refactors)
- **Break changes into small, reviewable chunks**
- **Never assume previous work exists** - always verify current state first

### When things go wrong:
- **Acknowledge the specific failure** without deflecting
- **Focus on damage assessment and recovery options**
- **Don't make promises about "fixing everything"**

### For complex multi-step processes:
- **Create explicit checklists** of what needs verification
- **Mark items as "appears done" vs "verified working"**
- **Human has final sign-off** on declaring anything "complete"

### Safe words:
- **"stop and verify"** - Claude pauses all work and shows current state
- **"show me first"** - Claude describes changes before making them

## Enforcement

The human user must actively enforce this policy rather than expect Claude to remember it. This includes:
- Interrupting when Claude makes absolute statements
- Asking "are you following the collaboration policy?" before big changes
- Treating Claude like a junior developer requiring oversight

## Current Task: UV Migration Recovery

### Background
Issue #176 "switch to uv instead of poetry" was prematurely closed due to incomplete migration assessment. The UV conversion was excruciating to implement due to dependency resolution complexity.

### Current Status (as of 2025-08-18)
- ✅ **literature_mining/Makefile** - Uses `uv run` commands
- ✅ **Root Makefile** - Updated with UV targets (`install`, `install-dev`)
- ❌ **pyproject.toml** - Still in Poetry format (`[tool.poetry]`)
- ❌ **uv.lock** - Does not exist
- ❌ **Full functionality** - Cannot run `make install-dev` due to format mismatch

### Required Work
1. **Convert pyproject.toml** from Poetry format to standard Python packaging format (`[project]`)
2. **Generate uv.lock** file via `uv sync --dev`
3. **Test full pipeline** functionality
4. **Verify all dependencies resolve** without conflicts

### Risk Assessment
- **High complexity**: Dependency resolution with latest packages is known to be difficult
- **Potential for version conflicts**: May require extensive troubleshooting
- **Previous work may be lost**: No evidence of completed pyproject.toml conversion in git history

### Decision Points
Before proceeding, the human must decide:
1. Attempt UV conversion despite complexity risks
2. Revert to Poetry workflow for stability
3. Defer UV migration to future milestone

This decision should be made based on project priorities and tolerance for dependency resolution troubleshooting.

## Lessons Learned

- **Issue #176 closure was premature** - Migration was assessed as complete when critical components were missing
- **Dependency work is high-risk** - Converting package managers involves complex troubleshooting that can be "excruciating"
- **Verification checklists are essential** - Complex migrations require explicit item-by-item verification
- **Git history is the source of truth** - Assumptions about completed work must be verified against actual commits

---

*This policy document should be referenced at the start of complex tasks and whenever disagreements arise about work status or next steps.*