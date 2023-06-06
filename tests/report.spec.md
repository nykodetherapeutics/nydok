# Report specification

nydok supports generating several different reports.

They're implemented by a command line interface, letting you specify which reports to generate and where to output them. The input is a run result of the nydok plugin, which is a JSON file containing the test results.

## Traceability matrix

The traceability matrix outputs all requirements, potentially filtered on a given ID prefix, along with the description, referenced requirements and which test case that covers this requirement (if any).

It supports configurable columns showing referenced requirement IDs. As an example, given a filter on "Design requirement" IDs, this allows for showing "User requirement" and "Functional requirement" columns with respective IDs, alongside the main Design requirement IDs (in the ID column).

The output is provided in Markdown table format.

### Functional requirements

- FR500 [UR080]: Traceability matrix report must support outputting a table in Markdown format.
- FR510 [UR080]: Traceability matrix report must list requirement IDs, description, references and test cases.
- FR520 [UR080]: Traceability matrix report must support filtering requirement IDs on a given prefix.
- FR530 [UR080]: Traceability matrix report must support configuring columns showing reference requirement IDs.

## Risk assessment report

### Functional requirements

- FR550 [UR050]: The system must generate a reportable on risk assessment, linking each connected test to a risk assessment.


## Test overview report

The test overview report displays a table of all the test cases, their description and whether it passed or failed.

### Functional requirements

- FR600 [UR070]: The test overview report must display a table of test cases, their description and pass or fail status, ordered by test case ID.

## Test case report

The test case report contains a list of all test cases and related information like what requirements were tested, the input and output data used (if applicable) and the code of the test itself.

- FR610 [UR070]: The test case report must display the tested requirements per test case.
- FR611 [UR070]: The test case report must display a description of the testcase in the heading, if available.
- FR620 [UR070]: The test case report must display input data and expected output data if available.
- FR630 [UR070]: The test case report must display a summary table of all tests and pass or fail status.

## Code review report

The code review report reports on merged merge requests from Gitlab, listing the merge request commit, title, author, date and who approved the change. Given a proper code review process, this allows for tracking who approved which changes.

### Functional requirements

- FR650 [UR060]: The code review report must collect merge requests from Gitlab for a given project and branch.
- FR651 [UR060]: If a tag is provided, the code review report must only display merge requests since the tag.
- FR660 [UR060]: The code review report must display a table of all merge requests, ordered by date in descending order.
- FR670 [UR060]: The code review report must display, for each merge request, the merge request commit, title, author, date and who approved the change.


## Pipeline logs report

The pipeline logs report collects the logs from a given Gitlab pipeline, and displays them in a report.

- FR700 [UR090]: The pipeline logs report must collect logs from a given Gitlab pipeline and display them in a report.

