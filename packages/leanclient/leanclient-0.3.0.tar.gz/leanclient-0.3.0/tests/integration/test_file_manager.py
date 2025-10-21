"""Integration tests for LSPFileManager."""

import os
import random
import time

import pytest

from leanclient import DocumentContentChange
from leanclient.base_client import BaseLeanLSPClient
from leanclient.file_manager import LSPFileManager
from leanclient.utils import apply_changes_to_text


class WrappedFileManager(LSPFileManager, BaseLeanLSPClient):
    """Test wrapper combining FileManager and BaseClient."""

    def __init__(self, *args, **kwargs):
        BaseLeanLSPClient.__init__(self, *args, **kwargs)
        LSPFileManager.__init__(self)


@pytest.fixture
def file_manager(test_project_dir):
    """Create WrappedFileManager for testing.

    Yields:
        WrappedFileManager: Test file manager instance.
    """
    manager = WrappedFileManager(test_project_dir, initial_build=False)
    yield manager
    manager.close()


# ============================================================================
# File opening tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.mathlib
@pytest.mark.slow
def test_open_files(file_manager, random_fast_mathlib_files):
    """Test opening files with caching."""
    paths = random_fast_mathlib_files(1)
    file_manager.open_file(paths[0])
    diag = file_manager.get_diagnostics(paths[0])
    diag2 = file_manager.get_diagnostics(paths[0])
    assert diag == diag2


@pytest.mark.integration
@pytest.mark.mathlib
def test_open_file_receives_diagnostics_without_wait(file_manager, test_file_path):
    """Ensure diagnostics arrive without explicitly waiting."""
    file_manager.open_file(test_file_path)

    deadline = time.time() + 10.0
    diagnostics = []
    error = None
    fatal_error = False

    while time.time() < deadline:
        with file_manager._opened_files_lock:
            state = file_manager.opened_files[test_file_path]
            diagnostics = list(state.diagnostics)
            error = state.error
            fatal_error = state.fatal_error
        if diagnostics or error or fatal_error:
            break
        time.sleep(0.1)

    try:
        assert fatal_error is False, (
            "Unexpected fatal error while waiting for diagnostics"
        )
        assert error is None, f"Unexpected error while waiting for diagnostics: {error}"
        assert diagnostics, "Expected diagnostics to arrive without waitForDiagnostics"
    finally:
        file_manager.close_files([test_file_path])


# ============================================================================
# File update tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.mathlib
def test_file_update(file_manager, random_fast_mathlib_files, test_env_dir):
    """Test updating file with multiple changes."""
    path = random_fast_mathlib_files(1, 42)[0]
    file_manager.open_file(path)
    diags = file_manager.get_diagnostics(path)
    assert len(diags) <= 1, f"Expected 0 or 1 diagnostics, got {len(diags)}"

    NUM_CHANGES = 16
    changes = []
    t0 = time.time()
    text = file_manager.get_file_content(path)
    for _ in range(NUM_CHANGES):
        line = random.randint(10, 50)
        d = DocumentContentChange(
            "inv#lid\n", [line, random.randint(0, 4)], [line, random.randint(4, 8)]
        )
        changes.append(d)
        text = apply_changes_to_text(text, [d])
    file_manager.update_file(path, changes)
    diags2 = file_manager.get_diagnostics(path)

    if len(diags2) == 1:
        assert diags2[0]["message"] == "unterminated comment"
    else:
        assert len(diags2) >= NUM_CHANGES // 2, (
            f"Expected {NUM_CHANGES // 2} diagnostics got {len(diags2)}:\n\n{diags2}\n\n"
        )

    duration = time.time() - t0
    print(f"Updated {len(changes)} changes in one call: {duration:.2f} s")

    new_text = file_manager.get_file_content(path)
    assert text == new_text

    # Note: We intentionally do NOT compare diagnostics from incremental updates
    # vs opening a fresh file. The LSP server's incremental processing can stop
    # at different error points than processing a fresh file, leading to
    # different diagnostic line numbers even with identical final content.

    file_manager.close_files([path])


@pytest.mark.integration
@pytest.mark.mathlib
@pytest.mark.slow
def test_file_update_line_by_line(file_manager, test_env_dir):
    """Test updating file line by line."""
    NUM_LINES = 12
    path = ".lake/packages/mathlib/Mathlib/NumberTheory/FLT/Basic.lean"

    with open(test_env_dir + path, "r") as f:
        lines = f.readlines()
    START = len(lines) - NUM_LINES

    fantasy = "Fantasy.lean"
    fantasy_path = test_env_dir + fantasy
    text = "".join(lines[:START])
    with open(fantasy_path, "w") as f:
        f.write(text)

    try:
        file_manager.open_file(fantasy)

        lines = lines[-NUM_LINES:]
        t0 = time.time()
        diagnostics = []
        for i, line in enumerate(lines):
            text += line
            file_manager.update_file(
                fantasy,
                [DocumentContentChange(line, [i + START, 0], [i + START, len(line)])],
            )
            content = file_manager.get_file_content(fantasy)
            assert content == text
            diag = file_manager.get_diagnostics(fantasy)
            diagnostics.extend(diag)

        assert len(diagnostics) > NUM_LINES / 2
        speed = len(lines) / (time.time() - t0)
        print(f"Updated {len(lines)} lines one by one: {speed:.2f} lines/s")
    finally:
        if os.path.exists(fantasy_path):
            os.remove(fantasy_path)
        file_manager.close_files([fantasy])


@pytest.mark.integration
@pytest.mark.mathlib
@pytest.mark.slow
def test_update_file_mathlib(file_manager, test_env_dir):
    """Test that update_file correctly applies changes matching server behavior."""
    files = [
        ".lake/packages/mathlib/Mathlib/Data/Num/Prime.lean",
        ".lake/packages/mathlib/Mathlib/Data/Finset/SDiff.lean",
    ]

    for file in files:
        # Open the file and get initial content
        file_manager.open_file(file)
        diag = file_manager.get_diagnostics(file)
        assert diag == [], f"Expected no diagnostics for {file}, got {diag}"

        original_text = file_manager.get_file_content(file)

        # Apply changes with extreme character positions to test UTF-16 handling
        changes = [
            DocumentContentChange("--", [42, 20], [42, 30]),
            DocumentContentChange("/a/b/c\\", [89, 20], [93, 20]),
            DocumentContentChange("\n\n\n\n\n\n\n\n\n", [95, 100000], [105, 100000]),
        ]

        # Apply changes locally to predict expected result
        expected_text = original_text
        for change in changes:
            expected_text = apply_changes_to_text(expected_text, [change])

        # Apply changes via LSP server
        file_manager.update_file(file, changes)

        # Get server's version and compare
        server_text = file_manager.get_file_content(file)
        assert server_text == expected_text, (
            f"Server text doesn't match expected for {file}\n"
            f"Length diff: {len(server_text)} vs {len(expected_text)}"
        )

        # Should get diagnostics since we broke the code
        diag_updated = file_manager.get_diagnostics(file)
        assert len(diag_updated) > 0, f"Expected diagnostics after breaking {file}"

        # Clean up
        file_manager.close_files([file])


@pytest.mark.integration
@pytest.mark.mathlib
@pytest.mark.slow
def test_update_try_tactics(file_manager):
    """Test updating file to try different tactics."""
    file_path = ".lake/packages/mathlib/Mathlib/MeasureTheory/Covering/OneDim.lean"
    file_manager.open_file(file_path)
    diag_init = file_manager.get_diagnostics(file_path)
    assert diag_init == [], f"Expected no diagnostics, got {diag_init}"

    line, character = (26, 61)
    tactics = ["simp", "aesop", "norm_num", "omega", "linarith"]
    l_tactic = len("linarith")
    messages = {}
    for tactic in tactics:
        change = DocumentContentChange(
            start=[line, character],
            end=[line, character + l_tactic],
            text=tactic,
        )
        l_tactic = len(tactic)
        file_manager.update_file(
            file_path,
            [change],
        )
        messages[tactic] = file_manager.get_diagnostics(file_path)

    exp_len = {
        "aesop": 0,
        "linarith": 0,
        "ring": 1,
        "norm_num": 1,
        "omega": 1,
        "simp": 1,
    }

    for tactic in tactics:
        assert len(messages[tactic]) == exp_len[tactic], f"{messages}"


# ============================================================================
# File close tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.mathlib
def test_close(file_manager):
    """Test closing file and terminating process."""
    # Open large file, then close: Expecting process kill
    fpath = ".lake/packages/mathlib/Mathlib/MeasureTheory/Covering/OneDim.lean"
    file_manager.open_file(fpath)
    file_manager.close_files([fpath], blocking=False)
    file_manager.close(timeout=0.01)
    assert file_manager.process.poll() == -15  # SIGTERM despite kill?
