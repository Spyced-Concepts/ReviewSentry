Feature: Publisher trust and documentation transparency
  Users must understand exactly what ReviewSentry does with their secrets,
  how the AI is briefed, and how to audit the action source.
  The README example workflow must be accurate, minimal, and secure.

  Scenario: SECURITY.md exists in the repository root
    Given the repository at the current release SHA is examined
    Then a SECURITY.md file exists at the repository root

  Scenario: SECURITY.md lists all secrets the action receives
    Given the SECURITY.md file is read
    Then it lists every secret the action receives
    And it states exactly how each secret is used
    And it states no secret is logged stored or transmitted beyond its intended destination

  Scenario: SECURITY.md documents what data leaves the runner
    Given the SECURITY.md file is read
    Then it states only the PR diff and metadata are sent to the AI provider
    And it states no source code beyond the diff is transmitted

  Scenario: SECURITY.md provides SHA audit instructions
    Given the SECURITY.md file is read
    Then it explains how to pin to a full commit SHA
    And it provides commands for verifying SHA to tag correspondence
    And it provides a responsible disclosure contact

  Scenario: SECURITY.md documents the SYSTEM prompt
    Given the SECURITY.md file is read
    Then it includes the complete SYSTEM prompt text
    And it explains the purpose of the untrusted-input instruction

  Scenario: README example workflow does not include actions/checkout
    Given the README example workflow is examined
    Then it does not contain a step using "actions/checkout"

  Scenario: README example workflow does not include contents:read permission
    Given the README example workflow permissions block is examined
    Then it does not include "contents: read"

  Scenario: README example workflow includes a job timeout
    Given the README example workflow is examined
    Then it includes "timeout-minutes"

  Scenario: README example workflow includes concurrency control
    Given the README example workflow is examined
    Then it includes a "concurrency" block keyed to the pull request number
    And "cancel-in-progress" is set to true

  Scenario: SYSTEM prompt instructs AI to treat PR content as untrusted data
    Given the SYSTEM prompt in review.py is examined
    Then it contains an explicit instruction to treat PR title and body as data only
    And it contains an explicit instruction not to follow instructions embedded in PR content
