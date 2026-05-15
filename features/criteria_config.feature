Feature: Extensible criteria configuration
  ReviewSentry ships with default review criteria. Users must be able to
  disable criteria that do not apply, add custom criteria, and see exactly
  which criteria are active. Core security criteria cannot be silently
  disabled — doing so requires explicit acknowledgement.

  Background:
    Given the action is configured with a valid API key
    And the action is configured with a valid model identifier
    And the provider is set to "anthropic"

  Scenario: All default criteria are applied when no config file is present
    Given no ".github/reviewsentry.yml" file exists in the repository
    When the pull request workflow triggers
    Then the review applies all default criteria including sensitive data and correctness

  Scenario: Additional criteria are appended via the review_criteria input
    Given the review_criteria input is set to "Flag any use of console.log in production code"
    When the pull request workflow triggers
    Then the review comment includes the custom criterion in its output

  Scenario: Optional criterion is disabled via config file
    Given a ".github/reviewsentry.yml" file exists with "cross_platform: false"
    When the pull request workflow triggers
    Then the review comment does not include a cross-platform finding
    And the review still applies all other default criteria

  Scenario: Optional bash quality criterion is disabled via config file
    Given a ".github/reviewsentry.yml" file exists with "bash_quality: false"
    When the pull request workflow triggers
    Then the review comment does not include bash quality findings

  Scenario: Custom criteria are added via config file
    Given a ".github/reviewsentry.yml" file exists with a custom criterion "Verify all async functions have error handling"
    When the pull request workflow triggers
    Then the review comment includes a finding or note referencing the custom criterion

  Scenario: Disabling a core criterion without acknowledgement is rejected
    Given a ".github/reviewsentry.yml" file exists with "sensitive_data: false" but no acknowledgement
    When the pull request workflow triggers
    Then the workflow fails or warns that disabling a core criterion requires explicit acknowledgement
    And the sensitive data criterion is still applied

  Scenario: Core criterion disabled with explicit acknowledgement is skipped with notice
    Given a ".github/reviewsentry.yml" exists with "sensitive_data: false" and "acknowledge_disabled_core: true"
    When the pull request workflow triggers
    Then the review comment notes the sensitive data criterion was explicitly disabled
    And no sensitive data scan is performed
