# BDD Authoring Rules and Standards

### Rule 1: NO MAGIC STRINGS
If a value is defined in a configuration file (`application.json`), it **MUST** be referenced in `.feature` files using the `{config:key.path}` syntax. Hardcoding configured values in Gherkin steps is forbidden.

- **INCORRECT:** `Then a new archive page should contain a heading "Test Transcript"`
- **CORRECT:** `Then a new archive page should contain a heading "{config:coda_meeting.archive_transcript_heading_text}"`

This ensures that tests validate the configuration system, not a hardcoded value.

### Rule 2: Single Source of Truth for Test Values
The `tests/config/application.test.json` file is the **single source of truth** for all values used during BDD testing.

### Rule 3: Workflow for New Configured Values
When a new feature requires a new configurable value, this checklist is mandatory:

1.  [ ] **Add to Base Config:** Add the key and production value to `config/application.json`.
2.  [ ] **Add to Test Config:** Add the key and a specific *test* value to `tests/config/application.test.json`.
3.  [ ] **Update Schema:** Add the new key to the `SCHEMA` in `config/config_manager.py` to enforce its presence and type.
4.  [ ] **Reference in BDD:** Write a Gherkin step using the new `{config:your.new.key}` placeholder.
5.  [ ] **Implement Step Definition:** Ensure the step definition code resolves the placeholder.
