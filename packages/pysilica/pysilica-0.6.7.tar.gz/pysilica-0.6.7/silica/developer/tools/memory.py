import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from silica.developer.context import AgentContext
from silica.developer.tools import agent
from silica.developer.tools.framework import tool
from silica.developer.utils import render_tree


# Cache ripgrep availability check for efficiency (checked once per process startup)
_RIPGREP_AVAILABLE = None


def _has_ripgrep() -> bool:
    """Check if ripgrep (rg) is available on the system.

    This function caches the result to avoid repeated expensive shutil.which() calls
    since ripgrep availability is unlikely to change during process lifetime.
    """
    global _RIPGREP_AVAILABLE
    if _RIPGREP_AVAILABLE is None:
        _RIPGREP_AVAILABLE = shutil.which("rg") is not None
    return _RIPGREP_AVAILABLE


def _refresh_ripgrep_cache() -> None:
    """Refresh the cached ripgrep availability check.

    This can be called if ripgrep gets installed/uninstalled during runtime,
    though this is rare in practice.
    """
    global _RIPGREP_AVAILABLE
    _RIPGREP_AVAILABLE = None


@tool
def get_memory_tree(
    context: "AgentContext", prefix: Optional[str] = None, depth: int = -1
) -> str:
    """Get the memory tree structure starting from the given prefix.
    Returns a tree with only node names (no content) in a hierarchical structure,
    rendered using ASCII characters.

    Args:
        prefix: The prefix path to start from (None for root)
        depth: How deep to traverse (-1 for unlimited)
    """
    prefix_path = Path(prefix) if prefix else None
    result = context.memory_manager.get_tree(prefix_path, depth)

    if not result["success"]:
        return result["error"]

    # Render the tree using ASCII characters
    lines = []

    # Start rendering from the root
    render_tree(lines, result["items"], is_root=True)

    # If no items were rendered, return a message
    if not lines:
        return "Empty memory tree."

    # Convert lines to a single string
    return "\n".join(lines)


@tool
async def search_memory(
    context: "AgentContext", query: str, prefix: Optional[str] = None
) -> str:
    """Search memory entries for content matching the given query using intelligent text search.

    This tool performs semantic and text-based search across all memory entries using ripgrep
    (if available) or grep as fallback, returning relevant matches with context about why they match.

    Args:
        query: Search terms or phrases to find in memory content
        prefix: Optional path to limit search to a specific memory subtree

    Returns:
        Formatted search results showing:
        - Memory paths that contain matching content
        - Brief explanations of why each entry matches
        - Context snippets around matches
        - "No matching memory entries found" if no results

    Search Tips:
        - Use specific keywords from the content you're looking for
        - Try different variations (e.g., "React" vs "react component")
        - Search is case-insensitive and supports partial matches
        - Uses ripgrep (rg) when available for faster, more accurate results
    """
    memory_dir = context.memory_manager.base_dir
    search_path = memory_dir

    if prefix:
        search_path = memory_dir / prefix
        if not search_path.exists() or not search_path.is_dir():
            return f"Error: Path {prefix} does not exist or is not a directory"

    try:
        # Use the agent tool to kick off an agentic search using ripgrep or grep
        from silica.developer.tools.subagent import agent

        has_rg = _has_ripgrep()

        if has_rg:
            search_tool_intro = "You have ripgrep (rg) available."
            search_commands = """
        Use these ripgrep command patterns:
        - `rg "SEARCH_TERM" /path/to/search --type md` (search in .md files)
        - `rg -i "SEARCH_TERM" /path/to/search --type md` (case insensitive search)
        - `rg -l "SEARCH_TERM" /path/to/search --type md` (just list matching files)
        - `rg -n "SEARCH_TERM" /path/to/search --type md` (show line numbers)
        - `rg -C 2 "SEARCH_TERM" /path/to/search --type md` (show 2 lines of context around matches)
        - `rg "TERM1|TERM2" /path/to/search --type md` (search for multiple terms with OR)
        - `rg "TERM1.*TERM2" /path/to/search --type md` (search for terms in sequence)
        """
        else:
            search_tool_intro = "Ripgrep is not available, using grep."
            search_commands = """
        Use these grep command patterns:
        - `grep -r --include="*.md" "SEARCH_TERM" /path/to/search`
        - `grep -r --include="*.md" -i "SEARCH_TERM" /path/to/search` (case insensitive)
        - `grep -r --include="*.md" -l "SEARCH_TERM" /path/to/search` (just list files)
        - `grep -r --include="*.md" -n "SEARCH_TERM" /path/to/search` (show line numbers)
        - `grep -r --include="*.md" -A 2 -B 2 "SEARCH_TERM" /path/to/search` (show 2 lines of context)
        - `grep -r --include="*.md" -E "TERM1|TERM2" /path/to/search` (search for multiple terms with OR)
        - `grep -r --include="*.md" "TERM1.*TERM2" /path/to/search` (search for terms in sequence)
        """

        prompt = f"""
        You are an expert in file searching and memory system navigation.
        
        SEARCH TOOL STATUS: {search_tool_intro}
        
        The memory system stores entries as:
        1. .md files for content (search these)
        2. .metadata.json files for metadata (usually skip these unless specifically needed)
        
        {search_commands}
        
        IMPORTANT SEARCH FORMATTING RULES:
        - Format queries for grep/ripgrep pattern matching (not generic text search)
        - Use exact word matching when appropriate: "\\\\bword\\\\b" 
        - Use case-insensitive search (-i) for better recall
        - For multiple terms, use OR patterns: "term1|term2"
        - For phrase matching, use exact quotes: "exact phrase"
        - For wildcard matching, use appropriate regex: "term.*pattern"
        
        SEARCH STRATEGY (MAXIMUM 2 ATTEMPTS):
        1. First attempt: Use the most specific, well-formatted search terms
        2. If no results, make ONE more attempt with broader/alternative terms
        3. After 2 attempts with no results, stop and report failure
        
        YOUR TASK: Search for information relevant to this query and path:
        - Search Query: {query}
        - Search Path: {search_path}
        
        After finding matches, examine the matching files to provide context. Format your results as:
        
        ## Search Results
        
        1. **[memory/path]**: Brief explanation of why this matches and what it contains
        2. **[memory/path]**: Brief explanation of why this matches and what it contains
        
        For the paths, strip off the .md extension and the base directory path to present clean memory paths that can be used with read_memory_entry.
        
        If no results match after 2 attempts, say "No matching memory entries found." and suggest trying different search terms.
        """

        # Use the subagent tool to perform the search with shell_execute tool
        result = await agent(
            context=context,
            prompt=prompt,
            tool_names="shell_execute",  # Allow ripgrep/grep commands
            model="smart",
        )

        return result
    except Exception as e:
        return f"Error searching memory: {str(e)}"


def _format_entry_as_markdown(entry_data: Dict[str, Any]) -> str:
    """Format a file entry as markdown.

    Args:
        entry_data: The structured entry data

    Returns:
        A markdown-formatted string representation
    """
    if not entry_data["success"]:
        return f"Error: {entry_data['error']}"

    if entry_data["type"] == "file":
        result = f"Memory entry: {entry_data['path']}\n\n"
        result += f"Content:\n{entry_data['content']}\n\n"
        result += "Metadata:\n"
        for key, value in entry_data["metadata"].items():
            result += f"- {key}: {value}\n"
    elif entry_data["type"] == "directory":
        result = f"Directory: {entry_data['path']}\n\nContained paths:\n"

        if not entry_data["items"]:
            result += "  (empty directory)"
        else:
            for item in entry_data["items"]:
                if item["type"] == "node":
                    result += f"- [NODE] {item['path']}\n"
                else:
                    result += f"- [LEAF] {item['path']}\n"
    else:
        result = f"Unknown entry type: {entry_data['type']}"

    return result


@tool
def read_memory_entry(context: "AgentContext", path: str) -> str:
    """Read a memory entry.

    Args:
        path: Path to the memory entry

    Returns:
        The memory entry content or a list of contained memory paths if it's a directory,
        indicating whether each path is a node (directory) or leaf (entry)
    """
    result = context.memory_manager.read_entry(path)
    return _format_entry_as_markdown(result)


def _format_write_result_as_markdown(result: Dict[str, Any]) -> str:
    """Format a write operation result as markdown.

    Args:
        result: The structured result data

    Returns:
        A markdown-formatted string representation
    """
    if not result["success"]:
        return f"Error: {result['error']}"
    return result["message"]


async def _determine_memory_path_and_summary(
    context: "AgentContext", content: str
) -> dict:
    """Use an agent to determine the best path for storing memory content and generate a summary.

    Args:
        context: Agent context
        content: Content to be stored

    Returns:
        Dictionary with 'path', 'action' ('create' or 'update'), 'reasoning', 'summary', and 'success' (bool)

    Raises:
        Exception: When unable to determine a suitable path due to system errors
    """
    # Get current memory tree structure
    tree_result = context.memory_manager.get_tree(prefix=None, depth=-1)
    if not tree_result["success"]:
        # Surface the error instead of using fallback
        raise Exception(f"Could not analyze memory tree: {tree_result['error']}")

    user_prompt = f"""Please analyze this content and determine the best memory placement:

=== CONTENT TO PLACE ===
{content}
=== END CONTENT ===

Current memory tree structure:
{json.dumps(tree_result["items"], indent=2)}

You are an expert memory organizer. Your task is to determine the optimal placement for new content in a hierarchical memory system.

You have access to these tools:
- get_memory_tree: Get the current memory structure
- read_memory_entry: Read existing memory entries to check for similarity
- search_memory: Search for related content

Your goal is to analyze the provided content and determine:
1. Whether this content should UPDATE an existing memory entry or CREATE a new one
2. If creating new, what is the best hierarchical path for organization
3. Create a concise summary of the content for metadata storage (unless it's a README file)

Consider:
- Semantic similarity to existing content
- Logical hierarchical organization
- Consistency with existing naming patterns
- Whether content is better as an update vs. separate entry
- README files should NOT have summaries generated

Return your decision in this exact format:
```
DECISION: [CREATE|UPDATE]
PATH: [the/memory/path]
SUMMARY: [concise 1-2 sentence summary of the content, or "N/A" if this is a README file]
REASONING: [brief explanation of your decision]
```

Analyze the content, search for similar entries if needed, and provide your placement decision and summary.
"""

    try:
        from silica.developer.tools.subagent import agent

        result = await agent(
            context=context,
            prompt=user_prompt,
            tool_names="get_memory_tree,read_memory_entry,search_memory",
            model="smart",
        )

        # Parse the agent's response
        lines = result.strip().split("\n")
        decision_info = {
            "action": "create",
            "path": None,
            "summary": None,
            "reasoning": None,
            "success": False,
        }

        for line in lines:
            line = line.strip()
            if line.startswith("DECISION:"):
                action = line.replace("DECISION:", "").strip().lower()
                decision_info["action"] = "update" if action == "update" else "create"
            elif line.startswith("PATH:"):
                path = line.replace("PATH:", "").strip()
                decision_info["path"] = path
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
                decision_info["summary"] = summary
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
                decision_info["reasoning"] = reasoning

        # Validate that we got the required information
        if decision_info["path"] is None:
            raise Exception(f"Agent did not provide a valid path. Response: {result}")

        # Only require summary for files that should have summaries
        if (
            _should_generate_summary(decision_info["path"])
            and decision_info["summary"] is None
        ):
            raise Exception(
                f"Agent did not provide a valid summary for non-README file. Response: {result}"
            )

        # Clear summary for README files regardless of what agent provided
        if not _should_generate_summary(decision_info["path"]):
            decision_info["summary"] = None

        decision_info["success"] = True
        return decision_info

    except Exception as e:
        # Re-raise the exception instead of falling back
        raise Exception(f"Error during agent analysis: {str(e)}")


def _should_generate_summary(path: str) -> bool:
    """Determine if a memory entry should have an automatic summary generated.

    Args:
        path: The memory entry path

    Returns:
        False if the entry should not be summarized, True otherwise
    """
    # Extract the filename from the path
    filename = Path(path).name.lower()

    # Skip summarization for README files
    if filename == "readme":
        return False

    return True


async def _generate_content_summary(context: "AgentContext", content: str) -> str:
    """Generate a concise summary of memory content.

    Args:
        context: Agent context
        content: Content to summarize

    Returns:
        A concise 1-2 sentence summary of the content

    Raises:
        Exception: When unable to generate summary
    """
    user_prompt = f"""Please create a concise summary of this content:

=== CONTENT TO SUMMARIZE ===
{content}
=== END CONTENT ===

Create a clear, concise 1-2 sentence summary that captures the main topic and key points of this content. 
The summary will be stored as metadata alongside the content for quick reference.

Return only the summary, nothing else."""

    try:
        from silica.developer.tools.subagent import agent

        result = await agent(
            context=context,
            prompt=user_prompt,
            model="smart",
        )

        # Clean up the result in case agent added extra formatting
        summary = result.strip().strip('"').strip("'")
        if not summary:
            raise Exception("Agent returned empty summary")

        return summary

    except Exception as e:
        raise Exception(f"Error generating content summary: {str(e)}")


@tool
async def write_memory_entry(
    context: "AgentContext", content: str, path: str = None
) -> str:
    """Write a memory entry with intelligent placement.

    This tool can operate in two modes:
    1. Manual placement: When path is provided, content is written to that exact location (backward compatible)
    2. Agentic placement: When path is omitted, an AI agent analyzes the content and existing memory
       structure to determine the optimal placement, considering semantic similarity and organization

    Args:
        content: Content to write to memory
        path: Optional path to the memory entry. If not provided, an agent will determine the best
              placement by analyzing the content and existing memory structure.

    Returns:
        Status message including placement reasoning when using agentic placement
    """
    if path is None:
        # Use agent to determine the best path and generate summary
        try:
            placement_info = await _determine_memory_path_and_summary(context, content)
            path = placement_info["path"]

            # Include the summary in metadata (unless it's a README file)
            metadata = {}
            if _should_generate_summary(path) and placement_info.get("summary"):
                metadata["summary"] = placement_info["summary"]

            result = context.memory_manager.write_entry(path, content, metadata)

            # Include placement reasoning and summary in the response
            if result["success"]:
                response = f"Memory entry {placement_info['action']}d successfully at `{path}`\n\n"

                if _should_generate_summary(path) and placement_info.get("summary"):
                    response += f"**Content Summary:** {placement_info['summary']}\n\n"
                else:
                    response += "**Note:** No summary generated (README file)\n\n"

                response += (
                    f"**Placement Reasoning:** {placement_info['reasoning']}\n\n"
                )
                response += f"{result['message']}"
                return response
            else:
                return _format_write_result_as_markdown(result)

        except Exception as e:
            return f"Error: Could not determine memory placement: {str(e)}"
    else:
        # Use the provided path and generate summary for explicit updates (if appropriate)
        try:
            metadata = {}

            # Only generate summary if appropriate for this file type
            if _should_generate_summary(path):
                summary = await _generate_content_summary(context, content)
                metadata["summary"] = summary

            # Write the entry with metadata (may include summary)
            result = context.memory_manager.write_entry(path, content, metadata)

            if result["success"]:
                if "summary" in metadata:
                    return (
                        f"{result['message']}\n\n"
                        f"**Content Summary:** {metadata['summary']}"
                    )
                else:
                    return f"{result['message']}\n\n**Note:** No summary generated (README file)"
            else:
                return _format_write_result_as_markdown(result)

        except Exception as e:
            # Fall back to writing without summary if summarization fails
            result = context.memory_manager.write_entry(path, content)
            if result["success"]:
                return f"{result['message']}\n\n**Note:** Could not generate summary: {str(e)}"
            else:
                return _format_write_result_as_markdown(result)


@tool
async def critique_memory(context: "AgentContext", prefix: str | None = None) -> str:
    """Generate a critique of the current memory organization.

    This tool analyzes the current memory structure and provides recommendations
    for improving organization, reducing redundancy, and identifying gaps.
    It also analyzes summaries and suggests updates or moves as appropriate.
    """
    # First get the tree structure for organization analysis
    tree_result = context.memory_manager.get_tree(prefix, -1)  # Get full tree

    if not tree_result["success"]:
        return f"Error getting memory tree: {tree_result['error']}"

    tree = tree_result["items"]

    # Get all memory entries for content and metadata analysis
    memory_files = list(context.memory_manager.base_dir.glob("**/*.md"))
    if not memory_files:
        return "No memory entries found to critique."

    # Build memory structure with metadata information
    memory_structure = []
    summary_analysis = []

    for file in memory_files:
        try:
            # Skip metadata files
            if ".metadata." in file.name:
                continue
            relative_path = file.relative_to(context.memory_manager.base_dir)
            path_without_md = str(relative_path).replace(".md", "")
            memory_structure.append(path_without_md)

            # Check if this entry has a summary in its metadata
            metadata_path = file.parent / f"{file.stem}.metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    has_summary = "summary" in metadata
                    should_have_summary = _should_generate_summary(path_without_md)

                    summary_info = {
                        "path": path_without_md,
                        "has_summary": has_summary,
                        "should_have_summary": should_have_summary,
                        "summary": metadata.get("summary", ""),
                        "last_updated": metadata.get("updated", "unknown"),
                    }
                    summary_analysis.append(summary_info)

                except Exception as e:
                    print(f"Error reading metadata for {file}: {e}")

        except Exception as e:
            print(f"Error processing memory file {file}: {e}")

    system_prompt = """You are a memory organization expert. Your task is to analyze 
            the current organization of memory entries and provide constructive feedback.

            Focus on:
            1. Identifying redundancies or duplications in the structure
            2. Suggesting better organization or hierarchies
            3. Pointing out inconsistencies in naming or categorization
            4. Recommending consolidation where appropriate
            5. Identifying gaps in knowledge or categories that should be created
            6. Analyzing summary quality and completeness
            7. Suggesting when entries should be moved and their summaries updated
            
            For summary analysis, consider:
            - Entries that should have summaries but don't
            - Entries that have summaries but shouldn't (like README files)
            - Summaries that may be outdated or inaccurate
            - Opportunities to move entries to better locations (and update summaries accordingly)

            Be specific and actionable in your recommendations."""

    user_prompt = f"""
            Here is the current memory organization tree:
            
            {json.dumps(tree, indent=2)}
            
            Here are all the memory entry paths:
            
            {json.dumps(memory_structure, indent=2)}
            
            Here is the summary analysis for all entries:
            
            {json.dumps(summary_analysis, indent=2)}
            
            Please analyze this memory organization and provide:

            1. An overall assessment of the current organization
            2. Specific issues you've identified in the structure
            3. Concrete recommendations for improving the organization
            4. Suggestions for any new categories that should be created
            5. Summary quality analysis and recommendations:
               - Entries missing summaries that should have them
               - Entries with summaries that shouldn't have them
               - Entries that should be moved to better locations (with summary updates)
               - Outdated or inaccurate summaries that need refreshing
            
            When suggesting moves, explain why the new location is better and note that 
            the summary should be updated to reflect the new context.
            """

    try:
        result = await agent(
            context=context,
            prompt=system_prompt + "\n\n" + user_prompt,
            model="smart",
        )
        return result
    except Exception as e:
        return f"Error generating critique: {str(e)}"


@tool
def delete_memory_entry(context: "AgentContext", path: str) -> str:
    """Delete a memory entry.

    Args:
        path: Path to the memory entry to delete

    Returns:
        Status message indicating success or failure
    """
    result = context.memory_manager.delete_entry(path)
    if not result["success"]:
        return f"Error: {result['error']}"
    return result["message"]
