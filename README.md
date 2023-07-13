# fiddler-report-generator

## Installation
Fiddler Report Generator uses the Fiddler Client to communicate with the Fiddler platform. You can use the following command to install the latest version of the Fiddler Python Client.

`pip install fiddler-client`

Once you downloaded this package, run the following command at the package root directory. This will install FRoG and all the necessary dependencies.

`pip install .`


## Quick Start
Fiddler report generator utilizes a modular design which allows users to fully customize a report by specifying what analysis modules they want to add to a report. After importing reportgen, the user can generate a report by calling the generate_report function and passing a Fiddler Client object and a list of analysis modules to it. 

For a general overview report, the ProjectSummary module alone is sufficient in most common use cases.

In the following we show some examples of creating reports using the ProjectSummary module. First we need to create a Fiddler Client object which allows report generator to connect with a Fiddler deployment.

import fiddler as fdl
api = fdl.FiddlerApi(url='http://demo.fiddler.ai',
                     org_id='demo',
                     auth_token='', #Add your auth key
                     )
 

Next we import the report generator library and some of its useful modules.

from reportgen import generate_report, OutputTypes
from reportgen.analysis_modules import ProjectSummary, PerformanceAnalysisSpec
 
Now we show a few example of creating reports. For creating a report, we call the generate_report API and pass the following arguments to it:

fiddler_api: A fiddler client object

analysis_modules: A list of analysis modules

output_type: Currently two output types are accepted; OutputTypes.PDF and OutputTypes.DOCX

output_path: The name of the output file. The default value is 'fiddler_report'.

author: An optional argument to add author name to the metadata.

 
Example 1. A Simple Summary Report
For a simple summary report, we add a ProjectSummary module which we create by specifying the project_id and the start_time_delta argument. 


generate_report(fiddler_api=api,
                analysis_modules=[ProjectSummary(project_id="", #Add project id
                                                 start_time_delta='30D')],
                output_type=OutputTypes.DOCX,   
                output_path='example1',
                author='', #Add your name
                )

The start_time_delta argument of the ProjectSummary is one way of specifying the time interval for which the report will be generated and it denotes the relative starting time with respect the current time, expressed in difference units (e.g. days, hours) in a consistent format with Panda's timedelta. For example, set start_time_delta  to '30D' for a report of the past 30 days, and to '48h' for a report of the past 48 hours.

Alternatively, you can explicitly specify the start point and the end point of the reporting interval using the start_time and end_time arguments.

Example 2. A Summary Report with Production Performance
In addition to the charts and tables that are included in a report by the ProjectSummary module, one can add performance charts for the reporting period using the performance_analysis parameter of ProjectSummary. Performance charts are specified by creating PerformanceAnalysisSpec objects.

The following code shows a simple example of crating a PerformanceAnalysisSpec object by specifying the model for which we want to create a performance chart, the performance metric, and the interval length of chart time bins.

 A full description of the available parameters for specifying a PerformanceAnalysisSpec object is provided at the end of this page.


perf_analysis1 = PerformanceAnalysisSpec(model_id='logreg_all',
                                         metric='accuracy'
                                         interval_length='2D')

generate_report(fiddler_api=api,
                analysis_modules=[ProjectSummary(project_id="lending", 
                                                 start_time_delta='30D',
                                                 performance_analysis=[perf_analysis1]
                                                 ),
                output_type=OutputTypes.DOCX,   
                output_path='example2',
                author='', #Add your name
                )
Example 3. A Summary Report with Production Performance and Data Segmentation
A useful parameter of PerformanceAnalysisSpec is the segment_col attribute which allows the users to create performance charts segmented by the feature values in a column.   


perf_analysis2 = PerformanceAnalysisSpec(model_id='logreg_all',
                                         metric='f1_score',
                                         interval_length='2D',
                                         segment_col='home_ownership')

generate_report(fiddler_api=api,
                analysis_modules=[
                  ProjectSummary(
                    project_id="bank_churn", 
                    start_time_delta='30D',
                    performance_analysis=[perf_analysis2]
                  )
                ],
                output_type=OutputTypes.DOCX,   
                output_path='example3',
                author='', #Add your name
                )
