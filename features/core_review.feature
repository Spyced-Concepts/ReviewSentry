Feature: Core review operation
  ReviewSentry posts a structured AI code review comment on every pull request.
  The review must complete cleanly across all supported providers and handle
  error conditions with clear, actionable messages.

  Background:
    Given the action is configured with a valid API key
    And the action is configured with a valid model identifier
    And the test repository has an open pull request with a non-empty diff

  Scenario: Anthropic provider posts a review comment
    Given the provider is set to "anthropic"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a comment is posted on the pull request
    And the comment contains the header "## AI Code Review"
    And the comment ends with exactly one of "APPROVE", "APPROVE WITH NOTES", or "REQUEST CHANGES"
    And the comment contains the footer "Automated review. Maintainer approval required."

  Scenario: OpenAI provider posts a review comment
    Given the provider is set to "openai"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a comment is posted on the pull request
    And the comment contains the header "## AI Code Review"
    And the comment ends with exactly one of "APPROVE", "APPROVE WITH NOTES", or "REQUEST CHANGES"

  Scenario: OpenAI-compatible endpoint posts a review comment
    Given the provider is set to "openai"
    And a custom base URL is configured pointing to an OpenAI-compatible endpoint
    When the pull request workflow triggers
    Then the workflow completes without error
    And a comment is posted on the pull request

  Scenario: GitHub Models provider posts a review comment at zero external cost
    Given the provider is set to "github-models"
    And the API key is set to the GITHUB_TOKEN
    When the pull request workflow triggers
    Then the workflow completes without error
    And a comment is posted on the pull request
    And no external API key was used

  Scenario: Large diff is truncated with a visible note
    Given the provider is set to "anthropic"
    And the diff_lines limit is set to "10"
    When the pull request workflow triggers
    Then the workflow completes without error
    And the review comment contains the truncation note "Diff was large — review based on first 10 lines only."

  Scenario: Missing API key produces a clear error
    Given the API key is empty
    When the pull request workflow triggers
    Then the workflow fails with a non-zero exit code
    And the log contains "AI_API_KEY secret not configured"
    And no review comment is posted

  Scenario: Missing model identifier produces a clear error
    Given the model identifier is empty
    When the pull request workflow triggers
    Then the workflow fails with a non-zero exit code
    And the log contains "AI_MODEL variable not configured"
    And no review comment is posted

  Scenario: Invalid API key produces an HTTP error
    Given the API key is syntactically valid but rejected by the provider
    When the pull request workflow triggers
    Then the workflow fails with a non-zero exit code
    And the log contains an HTTP 401 error code
    And no review comment is posted

  Scenario: Unknown provider value produces a clear error listing valid options
    Given the provider is set to "notarealai"
    When the pull request workflow triggers
    Then the workflow fails with a non-zero exit code
    And the log lists all supported provider names
    And no review comment is posted

  Scenario: Empty diff does not cause a crash
    Given the provider is set to "anthropic"
    And the pull request has an empty diff
    When the pull request workflow triggers
    Then the workflow completes without error
    And a comment is posted on the pull request
