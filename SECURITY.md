# Security Policy

## Scope

This repository contains a research paper, a JSON Schema, example contracts and a
validator. It is **not** a deployed system and holds no credentials or user data.

The schema and validator are **specification and linting tools**. They do not
enforce anything at runtime. Nothing here should be relied on as a security
control by itself: enforcement requires a tool gateway that mediates every
side-effecting call, which this repository does not provide.

## Reporting an issue

For a defect in the validator, the schema or the examples, open a normal GitHub
issue.

For anything you believe should not be discussed publicly, use GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository.

## A note on the threat model

If you find a case where a contract that passes validation would still permit an
action the paper claims it forbids, that is a finding worth reporting — it is a
gap between the specification and the invariants, and exactly the kind of
correction this project wants.
