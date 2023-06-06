# Compiling a CSV report

You may want to compile a CSV[^1] report at the end of each release of your software. Defining a global process for this is impossible, as all companies and projects are different and have different approval processes.

Thus, how to compile a complete CSV report is very much up to you, nydok gives you the different parts that can go into such a report, but doesn't provide any templates or tools for compiling them into a complete report.

That said, here is an example of how you could get started to create a complete PDF report in a CI pipeline:

- Run `py.test` to run the tests and generate the `nydok.json` file
- Create all the nydok report parts you want to include into the report, like code review report, traceability matrix, test report, etc.
- Compile your specifications and nydok reports into HTML and concatenate them into one HTML file.
- Use a tool to convert the HTML file into a PDF file.

If you want to include validation of deployment of the software in the report, you normally want to run the report generation late in the process, after deployment. You can then include the pipeline logs and relevant test evidence into the report.

[^1]: Computerized System Validation