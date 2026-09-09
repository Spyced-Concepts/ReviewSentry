Feature: Output completeness — never clip on egress, warn honestly on incomplete reviews

  When the AI review runs out of `max_tokens` mid-response, the emitted text is
  missing its trailing verdict. The tool must detect this and append an
  incomplete-review warning whose stated cause is derived from measured values
  (diff size vs `diff_lines`, output size vs `max_tokens`), not asserted
  unconditionally. Closes #177 (verdict-extraction warning misdiagnoses cause).

  Background:
    Given the review-discipline post-processing hook is available

  Scenario: A review that ends with a valid verdict passes through unchanged
    Given a review body ending with the verdict line
    When the discipline hook runs with any measured values
    Then no incomplete-review warning is appended

  Scenario: A review with a verdict-shaped string mid-body but not at the end is flagged as incomplete
    Given a review body containing a verdict-shaped string in the middle but no trailing verdict
    When the discipline hook runs with any measured values
    Then an incomplete-review warning is appended

  Scenario Outline: A review whose verdict line was truncated mid-asterisks is still recognised as complete
    Given a review body ending with a verdict line where trailing asterisks are truncated to <trailing>
    When the discipline hook runs with any measured values
    Then no incomplete-review warning is appended

    Examples:
      | trailing |
      | zero     |
      | one      |

  Scenario: A review without a verdict and diff at the limit is flagged as diff-too-large
    Given a review body with no verdict line
    And the measured diff filled the diff_lines limit
    When the discipline hook runs
    Then an incomplete-review warning is appended
    And the warning states "diff too large"
    And the warning includes the measured DIFF_LINES over DIFF_LIMIT

  Scenario: A review without a verdict but output near max_tokens is flagged as output-limit
    Given a review body with no verdict line
    And the review body is close to the max_tokens ceiling in characters
    And the measured diff is well under the diff_lines limit
    When the discipline hook runs
    Then an incomplete-review warning is appended
    And the warning states "output limit reached"
    And the warning instructs the reader to raise max_tokens

  Scenario: A review without a verdict and both budgets clean is flagged as cause-undetermined
    Given a review body with no verdict line
    And the measured diff is well under the diff_lines limit
    And the review body is well under the max_tokens ceiling
    When the discipline hook runs
    Then an incomplete-review warning is appended
    And the warning states "cause undetermined"
    And the warning names the measured DIFF_LINES and output_chars for the reader

  Scenario: The discipline hook still applies colour semantics before the incomplete-review check
    Given a review body with a mis-marked section header and no verdict line
    When the discipline hook runs
    Then the section header is corrected by colour-semantics enforcement
    And an incomplete-review warning is also appended
