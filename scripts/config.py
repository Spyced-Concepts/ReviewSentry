"""
ReviewSentry criteria configuration loader.

Reads .github/reviewsentry.yml from REVIEWSENTRY_CONFIG env var (set by
action.yml via the GitHub API). Parses a limited YAML subset — no external
dependencies, stdlib only.

Config file schema (.github/reviewsentry.yml):
    # Disable optional criteria
    cross_platform: false
    bash_quality: false

    # Disable a core criterion — requires explicit acknowledgement
    sensitive_data: false
    acknowledge_disabled_core: true

    # Add custom criteria (appended after defaults)
    custom:
      - "Verify all async functions include error handling"
      - "Check for hardcoded TODO comments without an owner"
"""

import os
import re

# Core criteria cannot be silently disabled — they protect against critical issues.
# To disable one, the config must include acknowledge_disabled_core: true.
CORE_CRITERIA = {"sensitive_data", "merge_conflicts"}

# Optional criteria can be disabled freely.
OPTIONAL_CRITERIA = {
    "correctness", "cross_platform", "bash_quality",
    "security", "code_quality", "dependencies", "documentation", "pr_scope",
}

ALL_CRITERIA = CORE_CRITERIA | OPTIONAL_CRITERIA


def _parse(text):
    """Parse the limited YAML subset used in reviewsentry.yml."""
    result = {}
    current_list_key = None

    for line in text.splitlines():
        stripped = re.sub(r"#.*$", "", line).rstrip()
        if not stripped:
            continue

        if re.match(r"^\s+-\s+", stripped):
            if current_list_key is not None:
                item = re.sub(r"^\s+-\s+", "", stripped).strip().strip("\"'")
                result.setdefault(current_list_key, []).append(item)
            continue

        m = re.match(r"^(\w+):\s*(.*)", stripped)
        if m:
            current_list_key = None
            key, value = m.group(1), m.group(2).strip()
            if value == "":
                current_list_key = key
                result[key] = []
            elif value.lower() == "true":
                result[key] = True
            elif value.lower() == "false":
                result[key] = False
            else:
                result[key] = value.strip("\"'")

    return result


def load():
    """
    Load and validate reviewsentry.yml from REVIEWSENTRY_CONFIG env var.

    Returns (overrides, custom_criteria, warnings):
        overrides       — dict of criterion_name -> bool (True=enabled, False=disabled)
        custom_criteria — list of additional criterion strings
        warnings        — list of warning messages to surface in the review
    """
    content = os.environ.get("REVIEWSENTRY_CONFIG", "").strip()
    if not content:
        return {}, [], []

    try:
        data = _parse(content)
    except Exception as e:
        return {}, [], [f"reviewsentry.yml could not be parsed: {e} — using defaults"]

    warnings = []
    overrides = {}
    custom_criteria = []

    # Check for disabled core criteria without acknowledgement
    disabled_core = [k for k in CORE_CRITERIA if data.get(k) is False]
    if disabled_core:
        if not data.get("acknowledge_disabled_core"):
            warnings.append(
                f"reviewsentry.yml disables core criteria {disabled_core} without "
                f"'acknowledge_disabled_core: true' — these criteria will still run. "
                f"Add 'acknowledge_disabled_core: true' to explicitly suppress them."
            )
            # Protective default: remove the attempted disable
            for k in disabled_core:
                data.pop(k)
        else:
            warnings.append(
                f"Core criteria {disabled_core} explicitly disabled via "
                f"acknowledge_disabled_core. Sensitive data scan will not run."
            )

    # Collect criterion overrides
    for key in ALL_CRITERIA:
        if key in data and isinstance(data[key], bool):
            overrides[key] = data[key]

    # Collect custom criteria
    if "custom" in data and isinstance(data["custom"], list):
        custom_criteria = [str(c).strip() for c in data["custom"] if str(c).strip()]

    return overrides, custom_criteria, warnings
