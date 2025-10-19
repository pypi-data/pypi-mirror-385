# Compaction CLI Commands

## Overview

Silica provides CLI commands to manually control conversation compaction. These commands give you fine-grained control over how your conversation history is managed.

## Commands

### `/compact` - Full Compaction

Explicitly trigger full conversation compaction, regardless of the current token usage.

**Usage:**
```
/compact
```

**What it does:**
- Summarizes the entire conversation
- Archives the original conversation to a timestamped file
- Replaces the conversation with a summary + the last 2 message exchanges
- Provides statistics about the compaction (compression ratio, token counts, etc.)

**Example output:**
```
✓ Conversation compacted successfully!

**Original:** 240 messages (85,000 tokens)

**Compacted:** 3 messages (1,500 tokens)

**Compression ratio:** 1.8%

**Archive:** pre-compaction-20251017_143022.json
```

**When to use:**
- When you want to reset the conversation context manually
- When you know the conversation has grown too large
- Before switching to a different topic or task
- When you want to archive the current conversation state

**Requirements:**
- Must have more than 2 messages in the conversation

---

### `/mc [N]` - Micro-Compact

Micro-compact the conversation by summarizing only the first N turns and keeping the rest of the conversation intact.

**Note on turns:** A turn must end with a user message (API requirement):
- Turn 1 = 1 message (user)
- Turn 2 = 3 messages (user, assistant, user)
- Turn 3 = 5 messages (user, assistant, user, assistant, user)
- Turn N = (2N - 1) messages

**Usage:**
```
/mc           # Summarizes first 3 turns (5 messages)
/mc 5         # Summarizes first 5 turns (9 messages)
/mc 10        # Summarizes first 10 turns (19 messages)
```

**What it does:**
- Takes the first N conversation turns ((2N-1) messages)
- Generates a summary of just those turns
- Keeps all remaining messages as-is
- Updates the conversation to start with the summary, followed by the remaining messages

**Example output:**
```
✓ Micro-compaction completed!

**Compacted:** First 3 turns (5 messages)

**Kept:** 9 messages from the rest of the conversation

**Final message count:** 10 (was 14)

**Estimated compression:** 5 messages → ~450 tokens
```

**When to use:**
- When early conversation is less relevant to current work
- When you want to reduce context size without losing recent details
- When building on top of earlier discussion but the details aren't needed anymore
- For incremental compaction during long-running conversations

**Benefits over full compaction:**
- Preserves recent conversation exactly as-is
- More surgical - only compacts what you specify
- Useful for maintaining flow while reducing early context
- Can be applied multiple times for progressive compaction

**Requirements:**
- Must have more messages than you're trying to compact
- Example: To compact 3 turns (5 messages), you need at least 6 messages total

---

## Comparison: `/compact` vs `/mc`

| Feature | `/compact` | `/mc [N]` |
|---------|-----------|-----------|
| **Scope** | Entire conversation | First N turns only |
| **What's kept** | Summary + last 2 turns | Summary of first N turns + all remaining messages |
| **Compression** | Maximum | Moderate (adjustable) |
| **Recent context** | Preserved | Fully preserved |
| **Use case** | Major reset/cleanup | Incremental optimization |
| **Archival** | Yes (full archive) | No archival |

## Best Practices

### When to use `/compact`:
1. **Topic transitions**: Before switching to a completely different task
2. **Session cleanup**: When wrapping up one phase of work and starting another
3. **Maximum compression**: When you need to free up the most token space
4. **Archiving**: When you want to preserve the full conversation history

### When to use `/mc`:
1. **Iterative work**: During long sessions where early setup is no longer relevant
2. **Progressive compaction**: Apply multiple times as conversation grows
3. **Preserving flow**: When you want to keep recent back-and-forth intact
4. **Fine-tuned control**: When you know exactly how much history to compress

### Recommended workflow:
```
1. Work on task A (20 exchanges)
   └─> /mc 5     # Compact early setup, keep recent 15 exchanges

2. Continue work (20 more exchanges, total 35)
   └─> /mc 10    # Compact first 10 turns, keep recent 25

3. Major topic shift
   └─> /compact  # Full reset before new topic
```

## Technical Details

### Token Counting
- Both commands use the Anthropic API to count tokens accurately
- Compaction includes the full API context (system prompt, tools, messages)
- Token counts are displayed before and after compaction

### Archives
- `/compact` creates timestamped archives in `~/.hdev/history/{session_id}/`
- Archives are JSON files with the full conversation state before compaction
- Format: `pre-compaction-YYYYMMDD_HHMMSS.json`
- `/mc` does not create archives (use `/compact` if you need archival)

### Session Continuity
- Both commands preserve the session ID
- Compacted conversations remain in the same session
- Usage tracking and cost calculations continue uninterrupted
- The conversation naturally flows from summary to new content

## Environment Variables

These commands respect the same environment variables as automatic compaction:

- `SILICA_COMPACTION_THRESHOLD`: Affects automatic compaction threshold (doesn't affect manual commands)
- `SILICA_DEBUG_COMPACTION`: Shows detailed debug information when using `/compact` or `/mc`

## Examples

### Example 1: Simple Compaction
```
User: /compact
System: Compacting conversation (this may take a moment)...

✓ Conversation compacted successfully!
**Original:** 120 messages (42,000 tokens)
**Compacted:** 3 messages (1,200 tokens)
**Compression ratio:** 2.9%
**Archive:** pre-compaction-20251017_150045.json
```

### Example 2: Micro-Compact with Default
```
User: /mc
System: Micro-compacting first 3 turns (this may take a moment)...

✓ Micro-compaction completed!
**Compacted:** First 3 turns (5 messages)
**Kept:** 15 messages from the rest of the conversation
**Final message count:** 16 (was 20)
**Estimated compression:** 5 messages → ~400 tokens
```

### Example 3: Micro-Compact with Custom Amount
```
User: /mc 8
System: Micro-compacting first 8 turns (this may take a moment)...

✓ Micro-compaction completed!
**Compacted:** First 8 turns (15 messages)
**Kept:** 25 messages from the rest of the conversation
**Final message count:** 26 (was 40)
**Estimated compression:** 15 messages → ~1,100 tokens
```

## Error Handling

### Not Enough Messages
```
User: /compact
Error: Not enough conversation history to compact (need more than 2 messages)
```

### Invalid Input for `/mc`
```
User: /mc abc
Error: Invalid number 'abc'. Please provide an integer.

User: /mc 0
Error: Number of turns must be at least 1
```

### Insufficient History for `/mc`
```
User: /mc 10
Error: Not enough conversation history to micro-compact 10 turns 
(need more than 19 messages, have 12)
```

## See Also

- [Compaction Improvements](compaction_improvements.md) - Details on automatic compaction
- [Session Management](session_management.md) - Managing and resuming sessions
- `/help` command - List all available CLI commands

#### `/mc [N]` Command
```python
def _micro_compact(self, user_interface, sandbox, user_input, *args, **kwargs):
    """Micro-compact: summarize first N turns and keep the rest."""
```

Features:
- Compacts only the first N conversation turns (default 3)
- A turn must end with a user message (API requirement)
  - Turn 1 = 1 message (user)
  - Turn 2 = 3 messages (user, assistant, user)
  - Turn 3 = 5 messages (user, assistant, user, assistant, user)
  - Turn N = (2N - 1) messages
- Generates summary of compacted portion only
#### Micro-Compaction (Default)
```bash
> /mc
Micro-compacting first 3 turns (this may take a moment)...

✓ Micro-compaction completed!
**Compacted:** First 3 turns (5 messages)
**Kept:** 9 messages from the rest of the conversation
**Final message count:** 10 (was 14)
```

Note: Turn N = (2N - 1) messages because:
- Turn 1 = 1 message (user)
- Turn 2 = 3 messages (user, assistant, user)
- Turn 3 = 5 messages (user, assistant, user, assistant, user)

#### Micro-Compaction (Custom)
```bash
> /mc 5
Micro-compacting first 5 turns (this may take a moment)...

✓ Micro-compaction completed!
**Compacted:** First 5 turns (9 messages)
**Kept:** 21 messages from the rest of the conversation
**Final message count:** 22 (was 30)
```
| Aspect | `/compact` | `/mc [N]` |
|--------|-----------|-----------|
| **Scope** | Entire conversation | First N turns only |
| **Archives** | Yes (timestamped) | No |
| **Recent Context** | Last 2 turns preserved | All remaining messages preserved |
| **Use Case** | Major reset/topic change | Incremental optimization |
| **Compression** | Maximum | Moderate (adjustable) |
| **API Calls** | 1 (full summary) | 1 (partial summary) |
| **Turn Definition** | - | Turn N = (2N-1) messages |