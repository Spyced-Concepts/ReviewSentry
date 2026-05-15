# ReviewSentry — Test Suite

BDD-driven test suite for ReviewSentry. Tests are derived directly from the Gherkin feature files in `features/` and run in an isolated Python virtual environment.

---

## Quick start

```bash
cd tests
bash setup.sh          # creates .venv and installs pinned dependencies
.venv/bin/pytest -v    # Linux / macOS
.venv\Scripts\pytest -v  # Windows (Git Bash or PowerShell)
```

**Requirements:** Python 3.9 or later. No machine-wide package installs — everything runs inside `tests/.venv`.

Expected output:

```
19 passed, 22 skipped in 0.xx s
```

Skipped tests require a live GitHub Actions environment with a configured `AI_API_KEY` secret (end-to-end provider scenarios). They are not failures.

---

## Structure

```
tests/
  README.md               — this file
  requirements-dev.txt    — all dependencies, exact versions, no ranges
  setup.sh                — creates .venv and installs dependencies
  pytest.ini              — pytest configuration (testpaths, bdd_features_base_dir)
  conftest.py             — shared fixtures and step definitions
  test_transparency.py    — features/transparency.feature (10 static scenarios)
  test_criteria_config.py — features/criteria_config.feature (7 unit scenarios)
  test_core_review.py     — features/core_review.feature (validation scenarios only)
  test_input_safety.py    — features/input_safety.feature (static analysis)
  test_model_handling.py  — features/model_handling.feature (static + documentation)
  test_sensitive_data.py  — features/sensitive_data.feature (config + integration)
```

Feature files live at the repository root under `features/` and are the source of truth for all test scenarios. Tests are never written ahead of features — feature files are written first, then step definitions implement them.

---

## Development convention — BDD-first

All new ReviewSentry functionality must follow this order:

1. **Write the feature file first.** Define the scenario in Gherkin under `features/`. This is the specification and the acceptance test.
2. **Run the tests.** They will fail (step definitions not yet implemented or code not written). That failure is expected and correct.
3. **Implement the step definitions** in the relevant `tests/test_*.py` file.
4. **Implement the production code** until the tests pass.
5. **Commit.** The feature file, step definitions, and production code ship together.

---

## Dependency due diligence

All test dependencies have been individually assessed for security, maintenance, licensing, and geo-provenance before adoption.

**Assessment date:** 2026-05-15
**Assessed by:** Spyced Concepts Ltd.

**No unpatched CVEs were found in any of the pinned versions listed below at the time of this assessment (2026-05-15).** Where CVEs exist in earlier versions of these packages, the pinned versions in `requirements-dev.txt` contain the fixes.

The 14 packages listed below are the **complete resolved dependency tree** — both direct dependencies of pytest-bdd and all transitive dependencies — as produced by a clean `pip install pytest-bdd==8.1.0` dry run. Every package that enters the test environment is documented here.

These are **dev/test-only dependencies** — they are never bundled into the distributed action. They exist solely on developer machines and in CI test jobs. Production consumers of ReviewSentry are not exposed to these packages.

---

### Package schema

Every entry uses the following fields in this order. No entry omits a field; `None` or `N/A` is used where not applicable.

| Field | Description |
|---|---|
| **Purpose** | What the package does in this test suite |
| **Maintainer** | Person or organisation responsible |
| **Geo** | Operational base of the maintainer (geo scoring per Spyced Concepts supplier policy) |
| **Repository** | Canonical source URL |
| **Licence** | [SPDX identifier](https://spdx.org/licenses/) |
| **CVEs (pinned version)** | CVEs at 2026-05-15 with NVD links; `None at 2026-05-15` if clean |
| **Maintenance status** | Active / Stable / Dormant — with most recent release date |
| **Risk rating** | ✅ Low / ⚠️ Medium / 🔴 High |
| **Permitted because** | Reasoning for adoption |

---

### Package register

#### pytest — 9.0.3

| Field | Detail |
|---|---|
| **Purpose** | Test runner — collects, executes, and reports test results |
| **Maintainer** | pytest-dev organisation (community governed) |
| **Geo** | Europe / US collective |
| **Repository** | https://github.com/pytest-dev/pytest |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 — [CVE-2025-71176](https://nvd.nist.gov/vuln/detail/CVE-2025-71176) (tmp dir privilege escalation, fixed in 9.0.3) does not affect this version |
| **Maintenance status** | Active — 9.0.3 released April 2026 |
| **Risk rating** | ✅ Low — industry-standard test runner, actively maintained, no unpatched CVEs |
| **Permitted because** | Industry-standard test runner under transparent community governance; no unpatched CVEs in pinned version; MIT licence |

---

#### pytest-bdd — 8.1.0

| Field | Detail |
|---|---|
| **Purpose** | BDD step wiring — links Gherkin `.feature` files to Python step definitions |
| **Maintainer** | Alessio Bogon (@youtux), pytest-dev org; original authors Oleg Pidsadnyi and Anatoly Bubenkov |
| **Geo** | Europe (Italy/Benelux) — geo-aligned |
| **Repository** | https://github.com/pytest-dev/pytest-bdd |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 8.1.0 released December 2025 |
| **Risk rating** | ✅ Low — EU-based maintainer, pytest-dev org, no CVEs |
| **Permitted because** | Active EU-based maintainer under pytest-dev org; no CVEs; MIT licence; enables direct use of Gherkin feature files as executable test specs |

---

#### gherkin-official — 29.0.0

| Field | Detail |
|---|---|
| **Purpose** | Gherkin parser — reads and validates `.feature` files |
| **Maintainer** | Cucumber project (SmartBear Software) |
| **Geo** | US / global |
| **Repository** | https://github.com/cucumber/gherkin |
| **Licence** | Apache-2.0 |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — version 29.0.0 is the version required by pytest-bdd 8.1.0; pinned by the framework dependency, not directly by us. Current Gherkin is at 39.x |
| **Risk rating** | ✅ Low — official Gherkin spec parser, Apache-2.0 licence, no CVEs |
| **Permitted because** | Official Gherkin specification parser from the spec owners; Apache-2.0 licence; version pinned by pytest-bdd requirement |

---

#### Mako — 1.3.12

| Field | Detail |
|---|---|
| **Purpose** | Template engine — used by pytest-bdd for generating step stub code |
| **Maintainer** | Mike Bayer / Pylons Project (SQLAlchemy author) |
| **Geo** | US |
| **Repository** | https://github.com/sqlalchemy/mako |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 — [CVE-2022-40023](https://nvd.nist.gov/vuln/detail/CVE-2022-40023) (ReDoS, fixed in 1.2.2) does not affect this version |
| **Maintenance status** | Active — 1.3.12 released December 2024 |
| **Risk rating** | ✅ Low — trusted Python ecosystem author, no unpatched CVEs |
| **Permitted because** | Well-maintained by a trusted Python ecosystem author; no unpatched CVEs in pinned version; MIT licence |

---

#### MarkupSafe — 3.0.3

| Field | Detail |
|---|---|
| **Purpose** | HTML/XML escaping — transitive dependency of Mako |
| **Maintainer** | Pallets (David Lord et al.) — maintainers of Flask and Jinja2 |
| **Geo** | US / global |
| **Repository** | https://github.com/pallets/markupsafe |
| **Licence** | BSD-3-Clause |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 3.0.3 released September 2025 |
| **Risk rating** | ✅ Low — Pallets project, widely trusted, no CVEs |
| **Permitted because** | Pallets is a highly trusted Python web ecosystem org; no CVEs; BSD-3-Clause licence |

---

#### parse — 1.22.0

| Field | Detail |
|---|---|
| **Purpose** | String parsing — used by pytest-bdd for matching step text to step definitions |
| **Maintainer** | Richard Jones (@r1chardj0n3s) |
| **Geo** | Unknown |
| **Repository** | https://github.com/r1chardj0n3s/parse |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Stable — 1.22.0 is current; low commit frequency consistent with a mature, feature-complete library |
| **Risk rating** | ✅ Low — stable, low-complexity library, no CVEs |
| **Permitted because** | No CVEs; MIT licence; low complexity reduces attack surface; test-only with no runtime exposure |

---

#### parse_type — 0.6.6

| Field | Detail |
|---|---|
| **Purpose** | Typed parse expressions — pytest-bdd dependency for typed step parameters |
| **Maintainer** | Jens Engel (@jenisys) |
| **Geo** | Unknown |
| **Repository** | https://github.com/jenisys/parse_type |
| **Licence** | BSD-2-Clause |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 0.6.6 released August 2025 |
| **Risk rating** | ✅ Low — active pytest-bdd ecosystem package, no CVEs |
| **Permitted because** | Active maintenance; no CVEs; BSD-2-Clause licence |

---

#### iniconfig — 2.3.0

| Field | Detail |
|---|---|
| **Purpose** | INI file parsing — pytest internal configuration |
| **Maintainer** | Ronny Pfannschmidt / pytest-dev org |
| **Geo** | Europe |
| **Repository** | https://github.com/pytest-dev/iniconfig |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 2.3.0 released October 2025 |
| **Risk rating** | ✅ Low — minimal pytest-dev library, no CVEs |
| **Permitted because** | pytest-dev org; minimal, well-audited library; no CVEs; MIT licence |

---

#### pluggy — 1.6.0

| Field | Detail |
|---|---|
| **Purpose** | Plugin framework — pytest's hook and plugin system |
| **Maintainer** | pytest-dev org; Tidelift supported |
| **Geo** | Europe / US collective |
| **Repository** | https://github.com/pytest-dev/pluggy |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 1.6.0 released May 2025; Tidelift subscription provides commercial support |
| **Risk rating** | ✅ Low — core pytest infrastructure, Tidelift-backed, no CVEs |
| **Permitted because** | Core pytest infrastructure; Tidelift-backed; no CVEs; MIT licence |

---

#### packaging — 26.2

| Field | Detail |
|---|---|
| **Purpose** | Version parsing — used by pytest for version comparison |
| **Maintainer** | Python Packaging Authority (PyPA) — Donald Stufft et al. |
| **Geo** | US / global |
| **Repository** | https://github.com/pypa/packaging |
| **Licence** | Apache-2.0 AND BSD-2-Clause |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 26.2 released April 2026 |
| **Risk rating** | ✅ Low — PyPA (Python Packaging Authority), no CVEs |
| **Permitted because** | PyPA is the authoritative Python packaging standards body; no CVEs; dual permissive licence |

---

#### colorama — 0.4.6

| Field | Detail |
|---|---|
| **Purpose** | Terminal colour output — cross-platform ANSI support for pytest output |
| **Maintainer** | Jonathan Hartley / Arnon Yaari |
| **Geo** | Unknown |
| **Repository** | https://github.com/tartley/colorama |
| **Licence** | BSD-3-Clause |
| **CVEs (pinned version)** | None at 2026-05-15 — a supply-chain typosquatting attack targeted a *different* package name (not colorama itself); pinned version 0.4.6 is unaffected |
| **Maintenance status** | Dormant — last release January 2022; considered feature-complete and intentionally stable rather than abandoned |
| **Risk rating** | ⚠️ Medium — dormant release cadence; low blast radius as test-only terminal formatting |
| **Permitted because** | No unpatched CVEs; typosquatting targeted a different package; test-only dependency with no runtime exposure; BSD-3-Clause licence. Accepted with awareness of dormant status |

---

#### Pygments — 2.20.0

| Field | Detail |
|---|---|
| **Purpose** | Syntax highlighting — used by pytest for code display in test failure output |
| **Maintainer** | Georg Brandl et al. |
| **Geo** | Germany — geo-aligned |
| **Repository** | https://github.com/pygments/pygments |
| **Licence** | BSD-2-Clause |
| **CVEs (pinned version)** | None at 2026-05-15 — [CVE-2026-4539](https://nvd.nist.gov/vuln/detail/CVE-2026-4539) (ReDoS, fixed in 2.20.0) does not affect this version |
| **Maintenance status** | Active — 2.20.0 released March 2026 |
| **Risk rating** | ✅ Low — German maintainer, geo-aligned, no unpatched CVEs |
| **Permitted because** | German maintainer (geo-aligned); no unpatched CVEs in pinned version; BSD-2-Clause licence |

---

#### six — 1.17.0

| Field | Detail |
|---|---|
| **Purpose** | Python 2/3 compatibility shim — transitive dependency of parse_type; not used directly |
| **Maintainer** | Benjamin Peterson |
| **Geo** | Unknown |
| **Repository** | https://github.com/benjaminp/six |
| **Licence** | MIT |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Dormant — feature-frozen by design; Python 2 is end-of-life; last release December 2024 |
| **Risk rating** | ⚠️ Medium — effectively dormant; included only as a transitive dependency of parse_type |
| **Permitted because** | No CVEs; MIT licence; test-only transitive dependency with zero production exposure; feature-frozen rather than abandoned. Accepted with awareness of dormant status |

---

#### typing_extensions — 4.15.0

| Field | Detail |
|---|---|
| **Purpose** | Standard library backport — provides newer typing features on Python 3.9+ |
| **Maintainer** | Python core developers |
| **Geo** | US / global (Python Software Foundation) |
| **Repository** | https://github.com/python/typing_extensions |
| **Licence** | PSF-2.0 |
| **CVEs (pinned version)** | None at 2026-05-15 |
| **Maintenance status** | Active — 4.15.0 released August 2025 |
| **Risk rating** | ✅ Low — Python core team, PSF-2.0 licence, no CVEs |
| **Permitted because** | Python core team; no CVEs; PSF-2.0 licence; standard library backport with minimal attack surface |

---

## Licence compatibility summary

All 14 packages use permissive licences. None carry copyleft requirements. All are compatible with ReviewSentry's MIT licence. Since these are dev/test-only dependencies and are never bundled into the distributed action, there is no licence propagation concern for end users.

| Licence (SPDX) | Packages |
|---|---|
| MIT | pytest, pytest-bdd, Mako, parse, iniconfig, pluggy, six |
| BSD-3-Clause | MarkupSafe, colorama |
| BSD-2-Clause | parse_type, Pygments |
| Apache-2.0 | gherkin-official |
| Apache-2.0 AND BSD-2-Clause | packaging |
| PSF-2.0 | typing_extensions |

---

## Attribution

The ReviewSentry test suite was designed and authored by Spyced Concepts Ltd. The BDD feature files and step definitions are original work. The test infrastructure relies on the open-source projects listed above, whose authors are credited in the package register.

We particularly acknowledge:

- **Alessio Bogon** and the original pytest-bdd authors **Oleg Pidsadnyi** and **Anatoly Bubenkov** — without pytest-bdd, running Gherkin feature files directly as Python tests would not be possible.
- **The pytest-dev organisation** — for maintaining the pytest ecosystem that makes structured, reproducible testing straightforward.
- **The Cucumber project** — for the Gherkin specification and the `gherkin-official` parser that enforces it.

If you are a maintainer of any of these packages and would like to know more about how ReviewSentry uses your work, we would love to hear from you.
