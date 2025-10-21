# Standard BDD Acceptance Criteria

*The following ACs must be included in every QoS Work Item to enforce process quality.*

-   [ ] **BDD Scenario Coverage:** A BDD scenario exists in a `.feature` file that validates the primary success path of every Functional Requirement (FR) in this work item.
-   [ ] **BDD Scenario Implementation:** All step definitions required by the new BDD scenarios are fully implemented in Python.
-   [ ] **BDD Scenario Execution:** All BDD scenarios related to this work item execute successfully with a 100% pass rate in the CI pipeline.
-   [ ] **BDD-AC Validation Report:** The AC Fulfillment Report for this work item includes the mandatory "BDD Scenario Validation" section, with links to the passing test execution report.
-   [ ] **Configuration Compliance:** All new user-facing or behavior-driving values are managed via `application.json` and referenced in BDD scenarios using the `{config:key.path}` syntax, per `BDD-Authoring-Rules.md`.
