# URS

## Introduction

In Computerized Software Validation (CSV) there is a need to keep track of software requirements and how they are validated, in addition to giving an overview of current the validation status and having traceability in process.

To facilite this process it is necessary to have a tool that can support a risk assessment process, track requirements by their identifiers, their validation status and provide the various reports needed to document the validation process.

At the time of writing there is no known tool that can provide all the desired functionality, tracking requirements with identifiers and with a close integration to a Python ecosystem, while supporting a pure Documentation-as-Code process.

## Background

nydok's main purpose is to aid documentation authoring in a CSV development process. The desired process is Documentation-as-Code, all documentation should live as part of the code and as much validation as possible should be automated.

The intended user is a developer in a development team, where both the gathering of requirements and actual implementation is done within the same team of developers, in collaboration with the users of the software and a QA team.

The goal for the software is to support a process where everything lives in the same code repository, and complete documentation is compiled automatically from the versioned code.

## System context

The software is assumed to operate in an environment where Python is the main programming language of choice.

The software will be used both while developing and in CI pipelines, and should support an agile development process.

Gitlab is assumed as system for version control and running CI/CD pipelines.

## Requirements

- UR001: The tool must support creating one or several documentation packages in PDF format.
- UR010: The tool must support authoring specification documents in a format well supported by text based version control.
- UR020: Each specification document must be able to contain requirements, each one testable by code.
- UR030: Each requirement must support having exactly one ID.
- UR031: The format of a requirement should be flexible.
- UR032: Each requirement must have a test case, or else present an error message.
- UR033: A test case must be able to cover multiple requirements.
- UR040: Each requirement must support referencing other requirements or IDs from other systems.
- UR045: The tool must support tracking test results from external sources.
- UR050: The tool must support a risk assessment process.
- UR051: The tool must support setting acceptable risk threshold.
- UR060: The tool must support creating a code review report.
- UR070: The tool must support creating a test report, listing test information with requirements tested and their context.
- UR080: The tool must support creating a traceability matrix report.
- UR090: The tool must support collecting evidence of test runs and releases.