Feature: Draft pull request review control
  By default ReviewSentry reviews every pull request including drafts.
  Teams that prefer to defer review until a PR is marked ready for review
  can opt out of draft reviews by setting review_drafts to false.
  The current default behaviour must remain unchanged for teams that do
  not set this input.

  Background:
    Given the action is configured with a valid API key
    And the action is configured with a valid model identifier
    And the provider is set to "anthropic"

  # ── Core behaviour ─────────────────────────────────────────────────────────

  Scenario: Draft PR is reviewed by default when review_drafts is not set
    Given the pull request is a draft
    And the review_drafts input is not configured
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted on the pull request

  Scenario: Draft PR is reviewed when review_drafts is explicitly true
    Given the pull request is a draft
    And the review_drafts input is set to "true"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted on the pull request

  Scenario: Draft PR is skipped when review_drafts is false
    Given the pull request is a draft
    And the review_drafts input is set to "false"
    When the pull request workflow triggers
    Then the workflow exits with code 0
    And no review comment is posted
    And the log contains "Skipping review — pull request is a draft"

  Scenario: Ready PR is always reviewed regardless of review_drafts setting
    Given the pull request is not a draft
    And the review_drafts input is set to "false"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted on the pull request

  # ── Draft to ready transition ───────────────────────────────────────────────

  Scenario: PR converted from draft to ready is reviewed when review_drafts is false
    Given the pull request was a draft and has been marked ready for review
    And the review_drafts input is set to "false"
    When the pull request workflow triggers on the ready_for_review event
    Then the workflow completes without error
    And a review comment is posted on the pull request

  Scenario: Closed PR that is reopened is reviewed
    Given the pull request is not a draft
    And the pull request was previously closed and has been reopened
    When the pull request workflow triggers on the reopened event
    Then the workflow completes without error
    And a review comment is posted on the pull request

  # ── Input validation ────────────────────────────────────────────────────────

  Scenario: review_drafts accepts "1" as truthy
    Given the pull request is a draft
    And the review_drafts input is set to "1"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted on the pull request

  Scenario: review_drafts accepts "yes" as truthy
    Given the pull request is a draft
    And the review_drafts input is set to "yes"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted on the pull request

  Scenario: review_drafts accepts "0" as falsy
    Given the pull request is a draft
    And the review_drafts input is set to "0"
    When the pull request workflow triggers
    Then the workflow exits with code 0
    And no review comment is posted
    And the log contains "Skipping review — pull request is a draft"

  Scenario: review_drafts accepts "no" as falsy
    Given the pull request is a draft
    And the review_drafts input is set to "no"
    When the pull request workflow triggers
    Then the workflow exits with code 0
    And no review comment is posted
    And the log contains "Skipping review — pull request is a draft"

  Scenario: Unrecognised review_drafts value triggers a warning and defaults to true
    Given the pull request is a draft
    And the review_drafts input is set to "maybe"
    When the pull request workflow triggers
    Then the log contains a warning about the unrecognised review_drafts value
    And the log states the accepted values for review_drafts
    And the workflow completes without error
    And a review comment is posted on the pull request

  Scenario: Empty review_drafts value triggers a warning and defaults to true
    Given the pull request is a draft
    And the review_drafts input is set to ""
    When the pull request workflow triggers
    Then the log contains a warning about the unrecognised review_drafts value
    And the workflow completes without error
    And a review comment is posted on the pull request

  # ── Safe defaults ───────────────────────────────────────────────────────────

  Scenario: When draft status cannot be determined the PR is reviewed
    Given the pull request draft status is unavailable in the event context
    And the review_drafts input is set to "false"
    When the pull request workflow triggers
    Then the workflow completes without error
    And a review comment is posted on the pull request

  # ── Interaction with other inputs ───────────────────────────────────────────

  Scenario: Skip due to draft takes precedence over fail_on setting
    Given the pull request is a draft
    And the review_drafts input is set to "false"
    And the fail_on input is set to "request_changes"
    When the pull request workflow triggers
    Then the workflow exits with code 0
    And no review comment is posted
    And the log contains "Skipping review — pull request is a draft"

  # ── Documentation ───────────────────────────────────────────────────────────

  Scenario: review_drafts is documented in action.yml with accepted values and default
    Given the action.yml file is examined
    Then the review_drafts input is defined
    And its description states the default is true
    And its description lists the accepted values
    And its description explains the fallback behaviour for unrecognised values

  Scenario: review_drafts is documented in the README inputs table
    Given the README file is examined
    Then the inputs table contains a row for review_drafts
    And the row states the default value
    And the row describes the accepted values and fallback behaviour

  Scenario: README notes that draft PRs are reviewed by default
    Given the README file is examined
    Then it mentions that draft pull requests are reviewed by default
    And it mentions the review_drafts input as the opt-out mechanism
