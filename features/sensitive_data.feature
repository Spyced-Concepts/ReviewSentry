Feature: Sensitive data detection
  ReviewSentry must detect credentials, personal identifiers, and
  user-defined sensitive patterns in pull request diffs. Sensitive data
  findings must appear before all other findings in the review output.

  Background:
    Given the action is configured with a valid API key
    And the action is configured with a valid model identifier
    And the provider is set to "anthropic"

  Scenario: API key pattern in diff is flagged as Critical before other findings
    Given the pull request diff contains a line matching an API key pattern
    When the pull request workflow triggers
    Then a review comment is posted
    And the first finding in the review is classified as Critical
    And the finding references sensitive data or credential exposure
    And the finding appears before any other criterion findings

  Scenario: Personal file system path is flagged as High severity
    Given the pull request diff contains a hardcoded file system path revealing a machine username
    When the pull request workflow triggers
    Then a review comment is posted
    And a finding is raised for the personal identifier
    And the finding is classified as High severity

  Scenario: Clean diff produces no sensitive data finding
    Given the pull request diff contains no credentials or personal identifiers
    When the pull request workflow triggers
    Then a review comment is posted
    And the review contains no sensitive data finding under criterion 1

  Scenario: Custom sensitive pattern is detected when added via custom_rules input
    Given a custom rule "ACME_INTERNAL" is configured via the custom_rules input
    And the pull request diff contains the string "ACME_INTERNAL"
    When the pull request workflow triggers
    Then a review comment is posted
    And the string "ACME_INTERNAL" is flagged as a finding
    And the finding appears in the sensitive data section

  Scenario: Custom sensitive pattern does not fire when absent from diff
    Given a custom rule "ACME_INTERNAL" is configured via the custom_rules input
    And the pull request diff does not contain the string "ACME_INTERNAL"
    When the pull request workflow triggers
    Then a review comment is posted
    And no finding references "ACME_INTERNAL"
