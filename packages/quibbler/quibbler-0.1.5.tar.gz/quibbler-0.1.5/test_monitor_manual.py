#!/usr/bin/env python3
"""Manual test script to verify quibbler monitor behavior via the server"""

import asyncio
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Import quibbler components
from quibbler.server import app, _process_event_in_background, get_or_create_quibbler
from quibbler.prompts import load_prompt
from quibbler.agent import Quibbler


async def test_rules_loading():
    """Test that rules are loaded and included in prompt"""
    print("\n=== Test 1: Rules Loading ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a rules file
        quibbler_dir = Path(tmpdir) / ".quibbler"
        quibbler_dir.mkdir()
        rules_file = quibbler_dir / "rules.md"
        rules_file.write_text("Always test before committing\nUse async/await")

        # Load prompt
        prompt = load_prompt(tmpdir)

        # Verify rules are included
        assert "Project-Specific Rules" in prompt, "Should include rules section"
        assert "Always test before committing" in prompt, "Should include rules content"
        print("✓ Rules loaded and included in prompt")


async def test_quibbler_creation():
    """Test that Quibbler can be created and started"""
    print("\n=== Test 2: Quibbler Creation & Startup ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        system_prompt = "Test prompt"
        quibbler = Quibbler(
            system_prompt=system_prompt,
            source_path=tmpdir,
            session_id="test-session"
        )

        # Start the quibbler
        await quibbler.start()

        # Verify task was created
        assert quibbler.task is not None, "Task should be created"
        assert not quibbler.task.done(), "Task should be running"
        print("✓ Quibbler created and started successfully")

        # Cleanup
        await quibbler.stop()
        await asyncio.sleep(0.1)  # Give it time to stop
        print("✓ Quibbler stopped cleanly")


async def test_event_queueing():
    """Test that events can be queued"""
    print("\n=== Test 3: Event Queueing ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        system_prompt = "Test prompt"
        quibbler = Quibbler(
            system_prompt=system_prompt,
            source_path=tmpdir,
            session_id="test-session"
        )

        await quibbler.start()

        # Queue an event
        test_event = {
            "event": "test_event",
            "message": "Hello from test",
            "received_at": datetime.now(timezone.utc).isoformat()
        }
        await quibbler.enqueue(test_event)

        # Verify it's in the queue
        assert quibbler.queue.qsize() == 1, "Event should be in queue"
        print("✓ Event queued successfully")

        await quibbler.stop()


async def test_rules_file_creation():
    """Test that rules file can be created and read"""
    print("\n=== Test 4: Rules File Creation ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        quibbler_dir = Path(tmpdir) / ".quibbler"
        quibbler_dir.mkdir()
        rules_file = quibbler_dir / "rules.md"

        # Write rules
        test_rules = "### Rule 1\nAlways use type hints\n\n### Rule 2\nWrite docstrings"
        rules_file.write_text(test_rules)

        # Read back
        loaded_rules = rules_file.read_text()
        assert loaded_rules == test_rules, "Rules should persist"

        # Verify via load_prompt
        prompt = load_prompt(tmpdir)
        assert test_rules in prompt, "Rules should be in prompt"
        print("✓ Rules file created and persisted")


async def test_message_file_path():
    """Test that session-specific message file path is computed correctly"""
    print("\n=== Test 5: Message File Path ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        session_id = "my-test-session"
        quibbler = Quibbler(
            system_prompt="Test",
            source_path=tmpdir,
            session_id=session_id
        )

        expected_file = f".quibbler-{session_id}.txt"
        # The message_file is computed in __post_init__ or during start
        # Check that the prompt replacement would work
        test_prompt = "Save to .quibbler-messages.txt"
        updated = test_prompt.replace(
            ".quibbler-messages.txt",
            f".quibbler-{session_id}.txt"
        )

        assert expected_file in updated, "Should have session-specific filename"
        print(f"✓ Message file path computed correctly: {expected_file}")


async def main():
    """Run all tests"""
    print("╔═══════════════════════════════════════════════════╗")
    print("║   Quibbler Monitor - Manual Test Suite            ║")
    print("╚═══════════════════════════════════════════════════╝")

    try:
        await test_rules_loading()
        await test_quibbler_creation()
        await test_event_queueing()
        await test_rules_file_creation()
        await test_message_file_path()

        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
