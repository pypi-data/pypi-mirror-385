#!/usr/bin/env python3
"""
Manual integration testing tool for conversation compaction.

This script allows developers to test and debug compaction on existing
conversation streams from the history folder.

IMPORTANT: This tool creates a temporary copy of the session for testing
and does NOT modify the original history files. All compaction operations
are performed in a temporary directory to ensure data safety.

Usage:
    python scripts/compaction_tester.py --session-id <session_id>
    python scripts/compaction_tester.py --history-file <path_to_root.json>
    python scripts/compaction_tester.py --session-id <session_id> --dry-run
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from silica.developer.compacter import ConversationCompacter, CompactionMetadata
from silica.developer.compaction_validation import (
    validate_message_structure,
    validate_compacted_messages,
    validate_api_compatibility,
    ValidationReport,
)
from silica.developer.context import AgentContext
from silica.developer.sandbox import Sandbox, SandboxMode
from silica.developer.memory import MemoryManager


class CompactionTester:
    """Handles testing of conversation compaction."""

    def __init__(self, verbose: bool = False):
        """Initialize the compaction tester.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.compacter = ConversationCompacter()

    def load_session(self, session_path: Path) -> Optional[Dict[str, Any]]:
        """Load a session from a history file.

        Args:
            session_path: Path to the root.json file

        Returns:
            Session data dictionary or None if loading failed
        """
        if not session_path.exists():
            print(f"❌ Session file not found: {session_path}")
            return None

        try:
            with open(session_path, "r") as f:
                session_data = json.load(f)

            if self.verbose:
                print(f"✅ Loaded session from {session_path}")

            return session_data
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in session file: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return None

    def display_session_info(self, session_data: Dict[str, Any]):
        """Display information about a session.

        Args:
            session_data: Session data dictionary
        """
        print("\n" + "=" * 70)
        print("SESSION INFORMATION")
        print("=" * 70)

        session_id = session_data.get("session_id", "unknown")
        parent_id = session_data.get("parent_session_id")
        messages = session_data.get("messages", [])
        model_spec = session_data.get("model_spec", {})
        metadata = session_data.get("metadata", {})

        print(f"Session ID: {session_id}")
        if parent_id:
            print(f"Parent Session ID: {parent_id}")
        print(f"Model: {model_spec.get('title', 'unknown')}")
        print(f"Message Count: {len(messages)}")

        if metadata:
            print("\nMetadata:")
            print(f"  Created: {metadata.get('created_at', 'unknown')}")
            print(f"  Last Updated: {metadata.get('last_updated', 'unknown')}")
            print(f"  Root Dir: {metadata.get('root_dir', 'unknown')}")
            if metadata.get("cli_args"):
                print(f"  CLI Args: {metadata.get('cli_args')}")

        # Count message types
        user_msgs = sum(1 for m in messages if m.get("role") == "user")
        assistant_msgs = sum(1 for m in messages if m.get("role") == "assistant")
        print("\nMessage Breakdown:")
        print(f"  User messages: {user_msgs}")
        print(f"  Assistant messages: {assistant_msgs}")

        # Count tool use
        tool_use_count = 0
        tool_result_count = 0
        for msg in messages:
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_use":
                            tool_use_count += 1
                        elif block.get("type") == "tool_result":
                            tool_result_count += 1

        print(f"  Tool use blocks: {tool_use_count}")
        print(f"  Tool result blocks: {tool_result_count}")

    def validate_session(self, messages: list) -> ValidationReport:
        """Validate a session's message structure.

        Args:
            messages: List of message dictionaries

        Returns:
            ValidationReport
        """
        print("\n" + "=" * 70)
        print("VALIDATING ORIGINAL CONVERSATION")
        print("=" * 70)

        report = validate_message_structure(messages)

        print(report.detailed_report())

        return report

    def create_mock_context(
        self, session_data: Dict[str, Any], temp_base_dir: Path
    ) -> AgentContext:
        """Create a mock AgentContext for compaction.

        IMPORTANT: Uses a temporary directory for all file operations to avoid
        modifying the user's actual history files.

        Args:
            session_data: Session data dictionary
            temp_base_dir: Temporary base directory for history files

        Returns:
            AgentContext instance configured to use temp directory
        """
        # Create minimal mock objects
        sandbox = Sandbox(".", mode=SandboxMode.ALLOW_ALL)

        # Simple mock UI for testing
        class MockUI:
            def handle_system_message(self, msg, markdown=True):
                if self.verbose:
                    print(f"[UI] {msg}")

            def permission_callback(self, *args, **kwargs):
                return True

            def permission_rendering_callback(self, *args, **kwargs):
                pass

        mock_ui = MockUI()
        mock_ui.verbose = self.verbose

        memory_manager = MemoryManager()

        model_spec = session_data.get(
            "model_spec",
            {
                "title": "claude-3-5-sonnet-latest",
                "pricing": {"input": 3.0, "output": 15.0},
                "cache_pricing": {"write": 3.75, "read": 0.3},
                "context_window": 200000,
            },
        )

        context = AgentContext(
            session_id=session_data.get("session_id", str(uuid4())),
            parent_session_id=session_data.get("parent_session_id"),
            model_spec=model_spec,
            sandbox=sandbox,
            user_interface=mock_ui,
            usage=session_data.get("usage", []),
            memory_manager=memory_manager,
            thinking_mode=session_data.get("thinking_mode", "off"),
            history_base_dir=temp_base_dir,  # Use temp directory!
            _chat_history=session_data.get("messages", []),
        )

        return context

    def run_compaction(
        self, context: AgentContext, model: str, force: bool = False
    ) -> Optional[CompactionMetadata]:
        """Run compaction on a conversation.

        Note: This method mutates the context in place if compaction occurs.

        Args:
            context: AgentContext with conversation to compact (mutated in place)
            model: Model name to use for compaction
            force: If True, force compaction even if under threshold

        Returns:
            CompactionMetadata if compaction occurred, None otherwise
        """
        print("\n" + "=" * 70)
        print("RUNNING COMPACTION")
        print("=" * 70)

        # Check if compaction is needed
        should_compact = self.compacter.should_compact(context, model)
        print(f"Should compact: {should_compact}")

        # Count tokens
        token_count = self.compacter.count_tokens(context, model)
        context_window = self.compacter.model_context_windows.get(model, 200000)
        threshold = int(context_window * self.compacter.threshold_ratio)

        print("\nToken Analysis:")
        print(f"  Current tokens: {token_count:,}")
        print(f"  Context window: {context_window:,}")
        print(
            f"  Threshold ({int(self.compacter.threshold_ratio * 100)}%): {threshold:,}"
        )
        print(f"  Utilization: {(token_count / context_window * 100):.1f}%")

        if not should_compact:
            print("⚠️  Conversation does not need compaction (below threshold)")

            if not force:
                # Ask user if they want to force compaction
                response = (
                    input("Would you like to force compaction anyway? (y/N): ")
                    .strip()
                    .lower()
                )
                if response != "y":
                    print("ℹ️  Skipping compaction")
                    return context.chat_history, None
                print("✅ Forcing compaction as requested")
                force = True  # Set force to True since user confirmed
            else:
                print("✅ Forcing compaction (--force flag enabled)")

        # Perform compaction
        print("\n⏳ Generating compaction summary...")
        metadata = self.compacter.compact_conversation(context, model, force=force)

        if metadata:
            print("\n✅ Compaction complete!")
            print("\nCompaction Results:")
            print(f"  Archive name: {metadata.archive_name}")
            print(f"  Original messages: {metadata.original_message_count}")
            print(f"  Compacted messages: {metadata.compacted_message_count}")
            print(f"  Original tokens: {metadata.original_token_count:,}")
            print(f"  Summary tokens: {metadata.summary_token_count:,}")
            print(f"  Compression ratio: {metadata.compaction_ratio:.2%}")
            print(f"  Token reduction: {(1 - metadata.compaction_ratio) * 100:.1f}%")
            print(
                f"\n📁 Pre-compaction conversation archived to: {metadata.archive_name}"
            )

        return metadata

    def validate_compacted_result(
        self, compacted_messages: list, original_messages: list
    ) -> ValidationReport:
        """Validate the compacted conversation.

        Args:
            compacted_messages: Compacted message list
            original_messages: Original message list

        Returns:
            ValidationReport
        """
        print("\n" + "=" * 70)
        print("VALIDATING COMPACTED CONVERSATION")
        print("=" * 70)

        # Validate structure
        structure_report = validate_compacted_messages(
            compacted_messages, original_messages, preserved_turns=2
        )
        print(structure_report.detailed_report())

        # Validate API compatibility
        print("\n" + "=" * 70)
        print("VALIDATING API COMPATIBILITY")
        print("=" * 70)

        api_report = validate_api_compatibility(compacted_messages)
        print(api_report.detailed_report())

        return structure_report

    def save_compacted_session(
        self,
        compacted_messages: list,
        original_session_data: Dict[str, Any],
        metadata: CompactionMetadata,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Save the compacted session to a file.

        Note: With the new compaction behavior, the session ID remains constant.
        The original conversation is archived with a timestamped filename.

        Args:
            compacted_messages: Compacted message list
            original_session_data: Original session data
            metadata: CompactionMetadata from compaction
            output_dir: Optional output directory (default: create in same location)

        Returns:
            Path to the saved file
        """
        print("\n" + "=" * 70)
        print("SAVING COMPACTED SESSION")
        print("=" * 70)

        # Session ID remains the same after compaction
        session_id = original_session_data.get("session_id")

        # Create new session data with compaction metadata
        new_session_data = {
            "session_id": session_id,
            "parent_session_id": original_session_data.get("parent_session_id"),
            "model_spec": original_session_data.get("model_spec"),
            "usage": [],  # Reset usage for compacted session
            "messages": compacted_messages,
            "thinking_mode": original_session_data.get("thinking_mode", "off"),
            "metadata": original_session_data.get("metadata", {}),
            "compaction": {
                "is_compacted": True,
                "pre_compaction_archive": metadata.archive_name,
                "original_message_count": metadata.original_message_count,
                "compacted_message_count": metadata.compacted_message_count,
                "original_token_count": metadata.original_token_count,
                "summary_token_count": metadata.summary_token_count,
                "compaction_ratio": metadata.compaction_ratio,
            },
        }

        # Determine output location
        if output_dir:
            output_path = output_dir / f"{session_id}_compacted.json"
        else:
            # Save in .agent-scratchpad
            output_path = Path(".agent-scratchpad") / f"{session_id}_compacted.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        with open(output_path, "w") as f:
            json.dump(new_session_data, f, indent=2)

        print(f"✅ Saved compacted session to: {output_path}")
        print(f"   Session ID: {session_id} (unchanged)")

        return output_path

    def test_session(
        self,
        session_path: Path,
        dry_run: bool = False,
        save_output: bool = True,
        force: bool = False,
        auto_confirm: bool = False,
    ) -> bool:
        """Test compaction on a session.

        IMPORTANT: This method creates a temporary copy of the session for testing
        and does NOT modify the original history files. All compaction operations
        are performed in a temporary directory.

        Args:
            session_path: Path to session root.json
            dry_run: If True, don't actually call the API for compaction
            save_output: If True, save the compacted session
            force: If True, force compaction even if under threshold
            auto_confirm: If True, automatically confirm all prompts

        Returns:
            True if test passed, False otherwise
        """
        # Load session
        session_data = self.load_session(session_path)
        if not session_data:
            return False

        # Display session info
        self.display_session_info(session_data)

        messages = session_data.get("messages", [])
        if not messages:
            print("❌ No messages in session")
            return False

        # Validate original conversation
        original_report = self.validate_session(messages)
        if original_report.has_errors():
            print("\n⚠️  Original conversation has validation errors!")
            if not auto_confirm:
                response = input("Continue anyway? (y/N): ").strip().lower()
                if response != "y":
                    return False
            else:
                print("✅ Auto-confirming (--yes flag enabled)")

        # Prompt user before compaction
        if not dry_run:
            print("\n" + "=" * 70)
            if not auto_confirm:
                response = (
                    input(
                        "Proceed with compaction? This will call the Anthropic API. (y/N): "
                    )
                    .strip()
                    .lower()
                )
                if response != "y":
                    print("❌ Compaction cancelled by user")
                    return False
            else:
                print("✅ Proceeding with compaction (--yes flag enabled)")
                print("=" * 70)

        # Run compaction (or simulate if dry run)
        if dry_run:
            print("\n🔍 DRY RUN - Skipping actual compaction")
            # In dry run, just validate what we have
            return not original_report.has_errors()

        # Create a temporary directory for testing
        # This ensures we don't modify the user's actual history files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_base = Path(temp_dir)
            session_id = session_data.get("session_id", str(uuid4()))

            print("\n🔒 Using temporary directory for safe testing:")
            print(f"   {temp_base}")
            print("   (Original files will NOT be modified)")

            # Create the session directory structure in temp
            session_dir = temp_base / "history" / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Write the original session to the temp directory
            temp_root_file = session_dir / "root.json"
            with open(temp_root_file, "w") as f:
                json.dump(session_data, f, indent=2)

            # Create mock context with temp directory
            context = self.create_mock_context(session_data, temp_base)
            model = session_data.get("model_spec", {}).get(
                "title", "claude-3-5-sonnet-latest"
            )

            # Run compaction (this will create archive in temp directory)
            metadata = self.run_compaction(context, model, force=force)

            if not metadata:
                print("ℹ️  No compaction performed")
                return True

            # Get compacted messages from context (which was mutated in place)
            compacted_messages = context.chat_history

            # Validate compacted result
            validation_report = self.validate_compacted_result(
                compacted_messages, messages
            )

            # Check that archive was created in temp directory
            archive_file = session_dir / metadata.archive_name
            if archive_file.exists():
                print(f"\n✅ Archive created: {archive_file}")
                archive_size = archive_file.stat().st_size
                print(f"   Size: {archive_size:,} bytes")
            else:
                print(f"\n⚠️  Archive file not found: {archive_file}")

            # Save if requested (to .agent-scratchpad, not temp)
            if save_output:
                self.save_compacted_session(compacted_messages, session_data, metadata)

            # Final summary
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)

            success = not validation_report.has_errors()
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"Status: {status}")

            if validation_report.has_errors():
                print(
                    "\n⚠️  Validation errors found - compacted conversation may not be API compatible"
                )
            elif validation_report.has_warnings():
                print("\n⚠️  Validation warnings found - review recommended")
            else:
                print(
                    "\n✅ All validations passed - compacted conversation is API compatible"
                )

            return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test conversation compaction on existing sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test compaction on a session by ID
  python scripts/compaction_tester.py --session-id abc-123-def
  
  # Test compaction on a specific history file
  python scripts/compaction_tester.py --history-file ~/.hdev/history/abc-123/root.json
  
  # Dry run (validate only, no API calls)
  python scripts/compaction_tester.py --session-id abc-123-def --dry-run
  
  # Force compaction even if under threshold
  python scripts/compaction_tester.py --session-id abc-123-def --force
  
  # Test with verbose output
  python scripts/compaction_tester.py --session-id abc-123-def --verbose
        """,
    )

    parser.add_argument(
        "--session-id",
        help="Session ID to test (loads from ~/.hdev/history/<session-id>/root.json)",
    )
    parser.add_argument(
        "--history-file", type=Path, help="Path to specific root.json file to test"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only, don't perform actual compaction (no API calls)",
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save the compacted session"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force compaction even if under threshold (skip confirmation)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Auto-confirm all prompts (non-interactive mode)",
    )

    args = parser.parse_args()

    # Determine session path
    if args.session_id:
        session_path = Path.home() / ".hdev" / "history" / args.session_id / "root.json"
    elif args.history_file:
        session_path = args.history_file
    else:
        parser.error("Either --session-id or --history-file must be provided")

    # Create tester and run
    tester = CompactionTester(verbose=args.verbose)

    try:
        success = tester.test_session(
            session_path=session_path,
            dry_run=args.dry_run,
            save_output=not args.no_save,
            force=args.force,
            auto_confirm=args.yes,
        )

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
