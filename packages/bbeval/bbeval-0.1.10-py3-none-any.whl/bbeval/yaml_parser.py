"""
YAML Parser for Test Cases

Parses .test.yaml files and extracts TestCase objects with user segments
and expected assistant responses, ensuring no leakage of ground truth
into model prompts.
"""

import re
import yaml
from pathlib import Path
from typing import List
from . import TestCase, TestMessage


def is_guideline_file(file_path: str) -> bool:
    """Determine if a file is a guideline file (instructions or prompts)."""
    return (file_path.endswith('.instructions.md') or '/instructions/' in file_path or
        file_path.endswith('.prompt.md') or '/prompts/' in file_path)


def extract_code_blocks(segments: List[dict]) -> List[str]:
    """Extract fenced code blocks from text segments."""
    code_blocks = []
    
    for segment in segments:
        if segment.get('type') == 'text':
            text = segment.get('value', '')
            # Find fenced code blocks (```...```)
            pattern = r'```[\s\S]*?```'
            matches = re.findall(pattern, text, re.MULTILINE)
            code_blocks.extend(matches)
    
    return code_blocks


def load_testcases(test_file_path: str, repo_root: Path, verbose: bool = False) -> List[TestCase]:
    """
    Load test cases from a YAML file.
    
    Args:
        test_file_path: Path to the .test.yaml file
        repo_root: Root directory of the repository for resolving file paths
        verbose: Whether to print verbose logging about file resolution
    
    Returns:
        List of TestCase objects
    """
    test_path = Path(test_file_path)
    if not test_path.exists():
        raise FileNotFoundError(f"Test file not found: {test_file_path}")
    # Work with absolute paths for consistent resolution
    test_path = test_path.resolve()
    repo_root = repo_root.resolve()
    cwd_path = Path.cwd().resolve()

    # Build a search order for resolving relative file references. We start from the
    # directory containing the test file, walk up towards the repository root, and
    # finally fall back to the current working directory for backwards compatibility.
    search_roots = []
    current_dir = test_path.parent
    while True:
        if current_dir not in search_roots:
            search_roots.append(current_dir)
        if current_dir == repo_root or current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent

    if repo_root not in search_roots:
        search_roots.append(repo_root)
    if cwd_path not in search_roots:
        search_roots.append(cwd_path)
    
    with open(test_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data or 'testcases' not in data:
        raise ValueError(f"Invalid test file format: {test_file_path}")
    
    # Get the global grader setting (default to 'llm_judge' if not specified)
    global_grader = data.get('grader', 'llm_judge')
    
    test_cases = []
    
    for raw_test in data.get('testcases', []):
        if 'id' not in raw_test or 'outcome' not in raw_test or 'messages' not in raw_test:
            print(f"\033[33mWarning: Skipping incomplete test case: {raw_test.get('id', 'unknown')}\033[0m")
            continue
        
        # Separate user and assistant messages
        user_msgs = [msg for msg in raw_test['messages'] if msg.get('role') == 'user']
        assistant_msgs = [msg for msg in raw_test['messages'] if msg.get('role') == 'assistant']
        
        if not assistant_msgs:
            print(f"\033[33mWarning: No assistant message found for test case: {raw_test['id']}\033[0m")
            continue
        
        if len(assistant_msgs) > 1:
            print(f"\033[33mWarning: Multiple assistant messages found for test case: {raw_test['id']}, using first\033[0m")
        # Process user segments
        user_segments = []
        guideline_paths = []
        user_text_parts = []

        for msg in user_msgs:
            content = msg.get('content', [])
            if isinstance(content, str):
                # Handle simple string content
                user_segments.append({'type': 'text', 'value': content})
                user_text_parts.append(content)
            elif isinstance(content, list):
                for segment in content:
                    if segment.get('type') == 'file':
                        raw_value = segment.get('value')
                        if not raw_value:
                            continue

                        file_path_display = raw_value.lstrip('/\\') or raw_value
                        original_path = Path(raw_value)
                        relative_path = Path(file_path_display)

                        # Assemble candidate locations in priority order.
                        potential_paths = []
                        if original_path.is_absolute():
                            potential_paths.append(original_path)

                        for base_dir in search_roots:
                            potential_paths.append(base_dir / relative_path)

                        full_path = None
                        attempted_paths = []
                        seen_candidates = set()

                        for candidate in potential_paths:
                            try:
                                resolved_candidate = candidate.resolve(strict=False)
                            except Exception:
                                resolved_candidate = candidate

                            if resolved_candidate in seen_candidates:
                                continue
                            seen_candidates.add(resolved_candidate)
                            attempted_paths.append(resolved_candidate)

                            if resolved_candidate.exists():
                                full_path = resolved_candidate
                                break

                        if full_path:
                            try:
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                
                                # Check if this is an instruction or prompt file
                                if is_guideline_file(file_path_display):
                                    # This is a guideline file - add to guideline paths but not to user segments
                                    # Store the absolute path to avoid resolution issues later
                                    guideline_paths.append(str(full_path.resolve()))
                                    if verbose:
                                        print(f"  [Guideline] Found: {file_path_display}")
                                        print(f"    Resolved to: {full_path}")
                                else:
                                    # This is a regular file - add to user segments
                                    user_segments.append({
                                        'type': 'file',
                                        'path': file_path_display,
                                        'text': file_content
                                    })
                                    if verbose:
                                        print(f"  [File] Found: {file_path_display}")
                                        print(f"    Resolved to: {full_path}")
                            except Exception as e:
                                print(f"\033[33mWarning: Could not read file {full_path}: {e}\033[0m")
                        else:
                            # Show all attempted paths for better debugging
                            attempted = "\n    ".join(str(p) for p in attempted_paths)
                            print(f"\033[33mWarning: File not found: {file_path_display}")
                            print(f"  Tried:\n    {attempted}\033[0m")
                    else:
                        # Handle text or other segment types
                        user_segments.append(segment)
                        # Capture any inline text value if present
                        if 'value' in segment and isinstance(segment['value'], str):
                            user_text_parts.append(segment['value'])
        
        # Extract code snippets from segments
        code_snippets = extract_code_blocks(user_segments)
        
        # Get expected assistant response
        expected_assistant = assistant_msgs[0]['content']
        if isinstance(expected_assistant, list):
            # If content is structured, join text parts
            expected_assistant = ' '.join([
                item.get('text', '') if isinstance(item, dict) else str(item)
                for item in expected_assistant
            ])
        
        # Build a minimal user prompt (one sentence) from user text parts, without leaking expected answer
        user_text_prompt = ' '.join([p.strip() for p in user_text_parts if p and isinstance(p, str)]).strip()

        test_case = TestCase(
            id=raw_test['id'],
            # Use the user's text as the task to avoid leaking 'outcome' details
            task=user_text_prompt or '',
            user_segments=user_segments,
            expected_assistant_raw=expected_assistant,
            guideline_paths=guideline_paths,
            code_snippets=code_snippets,
            outcome=raw_test['outcome'],
            grader=raw_test.get('grader', global_grader)  # Use test-specific grader or global default
        )
        
        if verbose:
            print(f"\n[Test Case: {raw_test['id']}]")
            if guideline_paths:
                print(f"  Guidelines used: {len(guideline_paths)}")
                for gp in guideline_paths:
                    print(f"    - {gp}")
            else:
                print(f"  No guidelines found")
        
        test_cases.append(test_case)
    
    return test_cases


def build_prompt_inputs(test_case: TestCase, repo_root: Path) -> dict:
    """Build consolidated prompt inputs for the new QuerySignature.

    Returns a dictionary with:
      - request: A single string concatenating all user-facing text, file contents, and fenced code blocks.
      - guidelines: Concatenated content of guideline files only.
    """
    # Gather guidelines content
    guideline_contents = []
    for path in test_case.guideline_paths:
        # Guideline paths are now stored as absolute paths, use them directly
        full_path = Path(path)
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    # Use just the filename for the header
                    guideline_contents.append(f"=== {full_path.name} ===\n{f.read()}")
            except Exception as e:
                print(f"\033[33mWarning: Could not read guideline file {full_path}: {e}\033[0m")

    # Build request from user segments (text + file contents) and extracted code blocks
    request_parts = []
    for segment in test_case.user_segments:
        if segment.get('type') == 'file':
            # Include file path header for clarity
            request_parts.append(f"=== {segment.get('path', 'file')} ===\n{segment.get('text', '')}")
        elif segment.get('type') == 'text':
            request_parts.append(segment.get('value', ''))
        else:
            # Generic handling for any other segment types with a value field
            if 'value' in segment:
                request_parts.append(str(segment['value']))

    # Append fenced code blocks extracted earlier
    if test_case.code_snippets:
        request_parts.append("\n".join(test_case.code_snippets))

    return {
        'request': '\n\n'.join([p for p in request_parts if p.strip()]),
        'guidelines': '\n\n'.join(guideline_contents)
    }
