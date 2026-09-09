Feature: Honest colour semantics — section headers derive from actual findings
  Established by RS-E-188-F-191 (sub-feature C of the review-reliability epic).

  Section headers must not contradict their own findings. A ⚠️ header requires
  at least one actionable finding (🔴 / 🟠 / 🟡) in its body; a ✅ header
  requires none. Where the emitted header disagrees with its body, the
  post-processing hook rewrites the header and appends a machine note so the
  fix is visible in the review output.

  This closes #171 (section severity marker can contradict section content).

  Background:
    Given the review-discipline post-processing hook is available

  Scenario: A ✅ header over an all-accepted section passes through unchanged
    Given a review with section header "✅ Correctness"
    And the section body contains only "✓ Accepted" findings
    When the discipline hook runs
    Then the section header remains "✅ Correctness"
    And no machine note is appended to the header

  Scenario: A ✅ header over an informational-only section passes through unchanged
    Given a review with section header "✅ Code Quality"
    And the section body contains only "🔵 Informational" findings
    When the discipline hook runs
    Then the section header remains "✅ Code Quality"
    And no machine note is appended to the header

  Scenario: A ⚠️ header over an all-accepted section is downgraded to ✅
    Given a review with section header "⚠️ Correctness"
    And the section body contains only "✓ Accepted" findings
    When the discipline hook runs
    Then the section header is rewritten to "✅ Correctness"
    And a machine note is appended recording "no actionable"

  Scenario: A ✅ header over a section containing a 🟡 Moderate finding is upgraded to ⚠️
    Given a review with section header "✅ Correctness"
    And the section body contains a "🟡 Moderate" finding
    When the discipline hook runs
    Then the section header is rewritten to "⚠️ Correctness"
    And a machine note is appended recording "an actionable"

  Scenario: A ✅ header over a section containing a 🔴 Critical finding is upgraded to ⚠️
    Given a review with section header "✅ Security"
    And the section body contains a "🔴 Critical" finding
    When the discipline hook runs
    Then the section header is rewritten to "⚠️ Security"
    And a machine note is appended recording "an actionable"

  Scenario: A ⚠️ header over a section containing a 🟠 High finding passes through unchanged
    Given a review with section header "⚠️ Security"
    And the section body contains a "🟠 High" finding
    When the discipline hook runs
    Then the section header remains "⚠️ Security"
    And no machine note is appended to the header

  Scenario: A section header using the ⚠ single-codepoint form is normalised to ⚠️
    Given a review with section header "⚠ Correctness"
    And the section body contains a "🟡 Moderate" finding
    When the discipline hook runs
    Then the section header is emitted as "⚠️ Correctness"

  Scenario: Findings rendered as list items are recognised
    Given a review with section header "✅ Correctness"
    And the section body contains a list-item finding "- 🟡 fix this"
    When the discipline hook runs
    Then the section header is rewritten to "⚠️ Correctness"

  Scenario: A well-formed review with multiple correct sections round-trips unchanged
    Given a review with two sections
    And the first section is "✅ Correctness" with only "✓ Accepted" findings
    And the second section is "⚠️ Security" with a "🔴 Critical" finding
    When the discipline hook runs
    Then both section headers are preserved
    And no machine notes are appended

  Scenario: A finding using 🔵 Informational does not elevate the section header
    Given a review with section header "✅ Documentation"
    And the section body contains only "🔵 Informational" findings
    When the discipline hook runs
    Then the section header remains "✅ Documentation"
