# Code review report

The code review report collects merge requests from Gitlab, and displays them in a report. It allows for documenting who approved which changes and listing all the introduced changes for a given version.


## Usage

You can create a code review report by running the following command:

```bash
nydok report code-review <args>
```

!!! note "Gitlab API"
    The code review report uses the Gitlab API to collect merge requests. This means that you need to provide a Gitlab URL and a Gitlab token to the command. You can do this by setting the environment variables `GITLAB_URL` and `GITLAB_TOKEN`.

For instance, in a Gitlab CI context, you can do something like the following command:

```bash
export GITLAB_URL=$CI_SERVER_URL
export GITLAB_TOKEN=$CI_JOB_TOKEN
nydok report code-review \
    --repo-path $CI_PROJECT_PATH_SLUG \
    --to-ref $CI_COMMIT_REF_NAME \
    --from-ref $PREV_VERSION_TAG
```

## Default report

Included information is the merge request commit, title, author, date and who approved the change.


Commit  | Title                                                | Date       | Author                | Approver(s)
------- | ---------------------------------------------------- | ---------- | --------------------- | ------------
e4a101c | Resolve "Support test results from external sources" | 2022-11-01 | Author name           |
af3d500 | Resolve "Create document for code review evidence"   | 2022-10-11 | Author name           | Reviewer name
3d1746c | Resolve "Support categories in traceability matrix"  | 2022-09-08 | Author name           | Reviewer name


## Specifying branches and tags

The code review report works by collecting all _commits_ from a range of git `ref`s. Next, it goes through all Merge Requests in Gitlab connected to any of these commits and gathers necessary the metadata.

By using the `--from-ref` and `--to-ref` arguments, you can specify which branch or tag to include in the report. The default is to include the whole range from the first commit until HEAD (latest commit) for the default branch configured in Gitlab.

### Example

Normally you want the difference between two version tags, to include the code reviews performed between the two versions.

```bash
nydok report code-review --from-ref v1.0.0 --to-ref v1.1.0
```