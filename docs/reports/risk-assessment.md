# Risk assessment

The risk assessment report is a table of all the risk assessments and their calculated risk priorities.

## Usage

You can create a risk assessment report by running the following command:

```bash
nydok report risk-assessment <args>
```

## Example report

The report is provided as a table in HTML format. The following is a rendered example of the report, given a single risk assessment:

<table class="nydok-risk-assessment">
  <thead>
    <tr>
      <th class="nydok-risk-id" rowspan="3" style="text-align: center;">RA001</th>
      <th class="nydok-risk-header nydok-risk-prior" colspan="3" style="text-align: center;">Prior</th>
      <th class="nydok-risk-header nydok-risk-residual" colspan="3" style="text-align: center;">Residual</th>
    </tr>
    <tr>
      <th class="nydok-risk-category nydok-risk-prior" style="text-align: center;">Prob.</th>
      <th class="nydok-risk-category nydok-risk-prior" style="text-align: center;">Severity</th>
      <th class="nydok-risk-category nydok-risk-prior" style="text-align: center;">Detect.</th>
      <th class="nydok-risk-category nydok-risk-residual" style="text-align: center;">Prob.</th>
      <th class="nydok-risk-category nydok-risk-residual" style="text-align: center;">Severity</th>
      <th class="nydok-risk-category nydok-risk-residual" style="text-align: center;">Detect.</th>
    </tr>
    <tr>
        <td colspan=1 class="nydok-risk-score nydok-risk-score-red nydok-risk-prior" style="color: #FF2020; background-color: #FFC7CE; text-align: center; min-width: 65px;">High</td>
        <td colspan=1 class="nydok-risk-score nydok-risk-score-orange nydok-risk-prior" style="color: #9C6500; background-color: #FFEB9C; text-align: center; min-width: 65px;">Medium</td>
        <td colspan=1 class="nydok-risk-score nydok-risk-score-orange nydok-risk-prior" style="color: #9C6500; background-color: #FFEB9C; text-align: center; min-width: 65px;">Medium</td>
        <td colspan=1 class="nydok-risk-score nydok-risk-score-green nydok-risk-residual" style="color: #3CA03F; background-color: #C6EFCE; text-align: center; min-width: 65px;">Low</td>
        <td colspan=1 class="nydok-risk-score nydok-risk-score-orange nydok-risk-residual" style="color: #9C6500; background-color: #FFEB9C; text-align: center; min-width: 65px;">Medium</td>
        <td colspan=1 class="nydok-risk-score nydok-risk-score-green nydok-risk-residual" style="color: #3CA03F; background-color: #C6EFCE; text-align: center; min-width: 65px;">High</td>
    </tr>
    <tr>
        <th>Risk priority</th>
        <td colspan=3 class="nydok-risk-score nydok-risk-score-red nydok-risk-prior" style="color: #FF2020; background-color: #FFC7CE; text-align: center; min-width: 65px;">High</td>
        <td colspan=3 class="nydok-risk-score nydok-risk-score-green nydok-risk-residual" style="color: #3CA03F; background-color: #C6EFCE; text-align: center; min-width: 65px;">Low</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th class="nydok-risk-text-header" style="padding: 10px;">Description</th>
      <td class="nydok-risk-text" style="padding: 10px;" colspan="5">Ipsem lorem dolor sit amet, consectetur adipiscing elit.</td>
    </tr>
    <tr>
      <th class="nydok-risk-text-header" style="padding: 10px;">Consequence</th>
      <td class="nydok-risk-text" style="padding: 10px;" colspan="5">Morbi laoreet et purus gravida hendrerit.</td>
    </tr>
    <tr>
      <th class="nydok-risk-text-header" style="padding: 10px;">Mitigation</th>
      <td class="nydok-risk-text" style="padding: 10px;" colspan="5">Praesent a magna condimentum. Mitigation requirement IDs: FR001.</td>
    </tr>
  </tbody>
</table>


## Minimum risk priority threshold

You can set a minimum risk priority threshold for the report. This will make the report command exit with an exception if the residual risk priority is higher than the threshold.

The default threshold is `low`, which means that by default the report will fail if there are any risk assessments with a residual risk priority of `medium` or `high`.

To adjust the accepted risk priority threshold, use the `--nydok-risk-priority-threshold` option:

```bash
nydok report risk-assessment --nydok-risk-priority-threshold medium ...
```
