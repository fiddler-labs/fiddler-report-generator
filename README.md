# Fiddler Report Generator

## Overview
The Fiddler Report Generator (FRoG) is a stand-alone Python package that enables Fiddler users to create fully customizable reports for the models deployed on Fiddler. These reports can be downloaded in different formats (e.g. pdf and docx), and shared with teams for periodic reviews. 

## Installation
Fiddler Report Generator uses the Fiddler Client to communicate with the Fiddler AI Observability platform. You can use the following command to install the latest version of the Fiddler Python Client.

`pip install fiddler-client`

Once you downloaded this package, run the following command at the package root directory. This will install FRoG and all the necessary dependencies.

`pip install .`


## Using Fiddler Report Generator
Fiddler Report Generator utilizes a modular design that allows users to fully customize a report by specifying what analysis modules they want to add to a report. After importing `reportgen`, the user can generate a report by calling the `generate_report` function and passing a Fiddler Client object and a list of analysis modules to it. You can create a summary report using the `ProjectSummary` module alone, which provides you with a general overview of your models and datasets for most common use cases.

You can see examples of how to generate a report in the [FRoG QuickStart Notebook](https://colab.research.google.com/drive/15xoPw7WJfUtZ3vgvflAYxNLB2cs_h7ku?usp=sharing).

