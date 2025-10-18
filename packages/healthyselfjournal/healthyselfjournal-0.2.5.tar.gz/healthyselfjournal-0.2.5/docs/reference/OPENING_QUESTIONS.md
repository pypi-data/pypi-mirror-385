# Opening Questions

## Overview

Default opener with embedded example questions for variety and inspiration.

## See also

- `LLM_PROMPT_TEMPLATES.md` - How questions are selected
- `DIALOGUE_FLOW.md` - Question progression strategy
- `../conversations/250916a_journaling_app_dialogue_design.md` - Hybrid adaptive model

## Default Opener

"What's on your mind right now?" - consistent entry point unless overridden.

## Embedded Example Questions

Maintained directly inside the `question.prompt.md.jinja` template. Used by the model when the user asks "give me a question" (or similar) and as inspiration for variety.
- Concrete/specific questions for clarity
- Open/exploratory questions for discovery
- Pattern-interrupting questions to shift perspective

User can request variety: "Give me a question" (model selects from embedded examples)

## Adaptive Approach

Questions adapt based on:
- First-time topics: Socratic exploration
- Recurring themes: Change talk amplification
- High emotion: Validation with gentle challenges