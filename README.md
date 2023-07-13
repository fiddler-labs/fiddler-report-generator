# fiddler-report-generator

## Installation
Fiddler Report Generator uses the Fiddler Client to communicate with the Fiddler platform. You can use the following command to install the latest version of the Fiddler Python Client.

`pip install fiddler-client`

Once you downloaded this package, run the following command at the package root directory. This will install FRoG and all the necessary dependencies.

`pip install .`


## Using Fiddler Report Generator
Fiddler report generator utilizes a modular design which allows users to fully customize a report by specifying what analysis modules they want to add to a report. After importing `reportgen`, the user can generate a report by calling the `generate_report` function and passing a Fiddler Client object and a list of analysis modules to it. For a general overview report, the `ProjectSummary` module alone is sufficient in most common use cases.

You can see examples of how to generate a repot in the [FRoG QuickStart Notebook](https://github.com/fiddler-labs/fiddler-auditor/blob/main/examples/Custom_Evaluation.ipynb).

