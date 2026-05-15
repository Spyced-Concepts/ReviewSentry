Feature: Model identifier handling
  ReviewSentry accepts any model identifier the configured provider supports.
  It must not validate model names against a hardcoded list, must not produce
  false-positive findings about model names in reviews, and must surface
  provider API errors clearly when an invalid model is used.

  Background:
    Given the action is configured with a valid API key
    And the provider is set to "anthropic"

  Scenario: A valid model identifier succeeds
    Given the model identifier is set to a current valid provider model slug
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted

  Scenario: An invalid model identifier produces a provider API error not a validation error
    Given the model identifier is set to "not-a-real-model-xyz"
    When the pull request workflow triggers
    Then the workflow fails with a non-zero exit code
    And the log contains a provider API error
    And the log does not contain a ReviewSentry-generated model validation message

  Scenario: ReviewSentry does not flag valid model names in diffs as invalid
    Given the pull request diff adds a workflow using a valid provider model slug in ai_model
    When the pull request workflow triggers
    Then the review comment does not contain a finding claiming the model name is invalid or non-existent

  Scenario: README documents that any provider-supported model identifier is accepted
    Given the README is examined
    Then it does not list specific model identifiers as the only valid options
    And it states that any model identifier supported by the configured provider is accepted
    And it recommends choosing a cost-efficient model without naming specific models
