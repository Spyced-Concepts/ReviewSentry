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

All test dependencies have been individually assessed for security, maintenance, licensing, and geo-provenance before adoption. This section is the permanent record of that assessment.

**Assessment date:** 2026-05-15
**Assessed by:** Spyced Concepts Ltd.
**No unpatched CVEs were found in any of the versions listed below at the time of this assessment (2026-05-15).** CVEs that existed in earlier versions of these packages have been fixed in the pinned versions specified in `requirements-dev.txt`.

The 14 packages listed below are the **complete resolved dependency tree** — both direct dependencies of pytest-bdd and their transitive dependencies — as produced by a clean `pip install pytest-bdd==8.1.0` dry run. Every package that enters the test environment is accounted for here; there are no undocumented transitive packages.

These are **dev/test-only dependencies** — they are never bundled into the distributed action. They exist solely on developer machines and in CI test jobs. Production consumers of ReviewSentry are not exposed to these packages.

---

### Package register

#### pytest — 9.0.3

| Field | Detail |
|---|---|
| **Purpose** | Test runner — collects, executes, and reports test results |
| **Maintainer** | pytest-dev organisation (community governed, Europe/US collective) |
| **Repository** | https://github.com/pytest-dev/pytest |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None — CVE-2025-71176 (tmp dir privilege escalation) was present in earlier versions and **fixed in 9.0.3** |
| **Maintenance** | Active — release 9.0.3 published April 2026; weekly releases |
| **Risk** | ✅ Low |
| **Permitted because** | Industry-standard test runner under transparent community governance; no unpatched CVEs; MIT licence |

---

#### pytest-bdd — 8.1.0

| Field | Detail |
|---|---|
| **Purpose** | BDD step wiring — links Gherkin `.feature` files to Python step definitions |
| **Maintainer** | Alessio Bogon (@youtux), pytest-dev org; original authors Oleg Pidsadnyi and Anatoly Bubenkov |
| **Repository** | https://github.com/pytest-dev/pytest-bdd |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Geo** | Europe (Italy/Benelux maintainer) — geo-aligned |
| **Maintenance** | Active — 8.1.0 released December 2025, repo updated April 2026 |
| **Risk** | ✅ Low |
| **Permitted because** | Active EU-based maintainer under pytest-dev org; no CVEs; MIT licence; enables direct use of our Gherkin feature files as test specs |

---

#### gherkin-official — 29.0.0

| Field | Detail |
|---|---|
| **Purpose** | Gherkin parser — reads and validates `.feature` files |
| **Maintainer** | Cucumber project (SmartBear Software) |
| **Repository** | https://github.com/cucumber/gherkin |
| **License** | Apache 2.0 — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Note** | Version 29.0.0 is the version required by pytest-bdd 8.1.0; current Gherkin is at 39.x. Version is pinned by the framework dependency, not by us directly. |
| **Maintenance** | Active — Cucumber project is actively maintained by SmartBear |
| **Risk** | ✅ Low |
| **Permitted because** | Official Gherkin specification parser from the spec owners; Apache 2.0 licence; version pinned by pytest-bdd requirement |

---

#### Mako — 1.3.12

| Field | Detail |
|---|---|
| **Purpose** | Template engine — used by pytest-bdd for generating step stub code |
| **Maintainer** | Mike Bayer / Pylons Project (SQLAlchemy author) |
| **Repository** | https://github.com/sqlalchemy/mako |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None — CVE-2022-40023 (ReDoS) was present in versions before 1.2.2 and **fixed in 1.2.2+**. Pinned version 1.3.12 is not affected. |
| **Maintenance** | Active — 1.3.12 released 2024/2025 |
| **Risk** | ✅ Low |
| **Permitted because** | Well-maintained by a trusted Python ecosystem author; no unpatched CVEs in pinned version; MIT licence |

---

#### MarkupSafe — 3.0.3

| Field | Detail |
|---|---|
| **Purpose** | HTML/XML escaping — Mako dependency |
| **Maintainer** | Pallets (David Lord et al.) — maintainers of Flask, Jinja2 |
| **Repository** | https://github.com/pallets/markupsafe |
| **License** | BSD-3-Clause — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Active — 3.0.3 released September 2025 |
| **Risk** | ✅ Low |
| **Permitted because** | Pallets is a highly trusted Python web ecosystem org; no CVEs; BSD licence |

---

#### parse — 1.22.0

| Field | Detail |
|---|---|
| **Purpose** | String parsing — used by pytest-bdd for matching step text to definitions |
| **Maintainer** | Richard Jones (@r1chardj0n3s) |
| **Repository** | https://github.com/r1chardj0n3s/parse |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Stable — 1.22.0 is current; low commit frequency consistent with a mature, feature-complete library |
| **Risk** | ✅ Low |
| **Permitted because** | Stable library with no CVEs; MIT licence; low complexity reduces attack surface |

---

#### parse_type — 0.6.6

| Field | Detail |
|---|---|
| **Purpose** | Typed parse expressions — pytest-bdd dependency for typed step parameters |
| **Maintainer** | Jens Engel (@jenisys) |
| **Repository** | https://github.com/jenisys/parse_type |
| **License** | BSD — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Active — 0.6.6 released August 2025 |
| **Risk** | ✅ Low |
| **Permitted because** | Active maintenance in the pytest-bdd ecosystem; no CVEs; BSD licence |

---

#### iniconfig — 2.3.0

| Field | Detail |
|---|---|
| **Purpose** | INI file parsing — pytest internal configuration |
| **Maintainer** | Ronny Pfannschmidt / pytest-dev org |
| **Repository** | https://github.com/pytest-dev/iniconfig |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Active — 2.3.0 released October 2025 |
| **Risk** | ✅ Low |
| **Permitted because** | pytest-dev org; minimal, well-audited library; no CVEs; MIT licence |

---

#### pluggy — 1.6.0

| Field | Detail |
|---|---|
| **Purpose** | Plugin framework — pytest's hook and plugin system |
| **Maintainer** | pytest-dev org; Tidelift supported |
| **Repository** | https://github.com/pytest-dev/pluggy |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Active — 1.6.0 released May 2025; Tidelift subscription provides commercial support |
| **Risk** | ✅ Low |
| **Permitted because** | Core pytest infrastructure; Tidelift-backed; no CVEs; MIT licence |

---

#### packaging — 26.2

| Field | Detail |
|---|---|
| **Purpose** | Version parsing — used by pytest for version comparison |
| **Maintainer** | Python Packaging Authority (PyPA) — Donald Stufft et al. |
| **Repository** | https://github.com/pypa/packaging |
| **License** | Apache 2.0 / BSD-2-Clause — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Active — 26.2 released April 2026 |
| **Risk** | ✅ Low |
| **Permitted because** | PyPA is the authoritative Python packaging standards body; no CVEs; dual permissive licence |

---

#### colorama — 0.4.6

| Field | Detail |
|---|---|
| **Purpose** | Terminal colour output — cross-platform ANSI support for pytest output |
| **Maintainer** | Jonathan Hartley / Arnon Yaari |
| **Repository** | https://github.com/tartley/colorama |
| **License** | BSD-3-Clause — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Last release** | January 2022 — no releases since then; the library is considered feature-complete and intentionally stable rather than abandoned |
| **Note** | A supply-chain typosquatting attack targeted a *different* package name (not colorama itself); pinned version 0.4.6 is unaffected |
| **Risk** | ⚠️ Medium — dormant release cadence; low blast radius as test-only output formatting |
| **Permitted because** | No unpatched CVEs; typosquatting was on a different package; test-only dependency with no runtime exposure; BSD licence. Reviewed and accepted with awareness of dormant status. |

---

#### Pygments — 2.20.0

| Field | Detail |
|---|---|
| **Purpose** | Syntax highlighting — used by pytest for code display in failure output |
| **Maintainer** | Georg Brandl et al. |
| **Repository** | https://github.com/pygments/pygments |
| **License** | BSD-2-Clause — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None — CVE-2026-4539 (ReDoS) was present in earlier versions and **fixed in 2.20.0**. Pinned version is not affected. |
| **Maintenance** | Active — 2.20.0 released March 2026 |
| **Risk** | ✅ Low |
| **Permitted because** | German maintainer (geo-aligned); no unpatched CVEs in pinned version; BSD licence |

---

#### six — 1.17.0

| Field | Detail |
|---|---|
| **Purpose** | Python 2/3 compatibility shim — transitive dependency of parse_type |
| **Maintainer** | Benjamin Peterson |
| **Repository** | https://github.com/benjaminp/six |
| **License** | MIT — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Note** | Python 2 is end-of-life; `six` exists for compatibility. It is a transitive dependency — we do not use it directly. It is feature-frozen by design. |
| **Risk** | ⚠️ Medium — effectively dormant; included only because parse_type requires it |
| **Permitted because** | No CVEs; MIT licence; test-only transitive dependency with zero production exposure; feature-frozen rather than abandoned (intentional maintenance state). Reviewed and accepted. |

---

#### typing_extensions — 4.15.0

| Field | Detail |
|---|---|
| **Purpose** | Standard library backport — provides newer typing features on Python 3.9+ |
| **Maintainer** | Python core developers |
| **Repository** | https://github.com/python/typing_extensions |
| **License** | PSF Licence — permissive, compatible with our MIT licence |
| **CVEs in pinned version** | None known |
| **Maintenance** | Active — 4.15.0 released August 2025 |
| **Risk** | ✅ Low |
| **Permitted because** | Python core team; no CVEs; PSF licence; standard library backport with minimal attack surface |

---

## Licence compatibility summary

All 14 packages use permissive licences (MIT, BSD variants, Apache 2.0, PSF). None carry copyleft requirements. All are compatible with ReviewSentry's MIT licence for development and distribution. Since these are dev/test-only dependencies and are never bundled into the distributed action, there is no licence propagation concern for end users of ReviewSentry.

| Licence | Packages |
|---|---|
| MIT | pytest, pytest-bdd, Mako, parse, parse_type, iniconfig, pluggy, six, typing_extensions |
| BSD (2 or 3-clause) | MarkupSafe, colorama, Pygments |
| Apache 2.0 | gherkin-official, packaging |
| PSF | typing_extensions |

---

## Attribution

The ReviewSentry test suite was designed and authored by Spyced Concepts Ltd. The BDD feature files and step definitions are original work. The test infrastructure relies on the open-source projects listed above, whose authors are credited in the package register.

We particularly acknowledge:

- **Alessio Bogon** and the original pytest-bdd authors **Oleg Pidsadnyi** and **Anatoly Bubenkov** — without pytest-bdd, running Gherkin feature files directly as Python tests would not be possible.
- **The pytest-dev organisation** — for maintaining the pytest ecosystem that makes structured, reproducible testing straightforward.
- **The Cucumber project** — for the Gherkin specification and the `gherkin-official` parser that enforces it.

If you are a maintainer of any of these packages and would like to know more about how ReviewSentry uses your work, we would love to hear from you.
