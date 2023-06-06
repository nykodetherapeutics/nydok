# Pipeline logs

The pipeline logs report is a report that can be generated from the pipeline logs of a CI system, such as Gitlab CI.

It is useful for including in a CSV report, as it can be used to show that the software has been deployed and tested in a controlled environment.


## Usage

You can create a pipeline logs report by running the following command:

```bash
nydok report pipeline-logs <args>
```

!!! note "Gitlab API"
    The pipeline logs report uses the Gitlab API to collect pipeline job traces. This means that you need to provide a Gitlab URL and a Gitlab token to the command. You can do this by setting the environment variables `GITLAB_URL` and `GITLAB_TOKEN`.

For instance, in a Gitlab CI context, you can do something like the following command:

```bash
export GITLAB_URL=$CI_SERVER_URL
export GITLAB_TOKEN=$CI_JOB_TOKEN
nydok report pipeline-logs \
    --repo-path $CI_PROJECT_PATH_SLUG \
    --pipeline-id $CI_PIPELINE_ID \
    --job-names build,test,release
```