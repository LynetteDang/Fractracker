# fractracker-complaints

## Acknowledgement
The Civic Data and Technology Clinic at the University of Chicago partners with public interest organizations to leverage data science research and technology to address pressing social and environmental challenges. This project is a collaboration with FracTracker Alliance, completed by three student developers: Jacob Lehr, Sophia MLawer, and Lynette Dang under the supervision of Launa Greer and with the help from Sebastian Clavijo. 

## Background
FracTracker, the project, was launched as a website at the University of Pittsburgh in 2010 to investigate health concerns and data gaps surrounding western Pennsylvania fracking. In 2012, FracTracker Alliance registered as a non-profit organization. Since then, it has supported groups across the United States, addressing pressing extraction-related concerns with a lens toward health effects and exposure risks on communities from oil and gas development.  Our main contacts at the organization will be Kyle Ferrar (Western Program Coordinator), Matt Kelso (Manager of Data & Technology), and Brook Lenker (Executive Director).

The FracTracker mobile app allows users to document potentially harmful encroachment of wells, pipelines, trains, refineries, landfills, mines, pits, and compressors within their local communities.  Users select the type of infrastructure or activity witnessed and the physical senses impacted (e.g., smell, sound); report their location; and then, optionally, add a written description, title, and photos. In the coming months, FracTracker Alliance will add a new feature to the app permitting users to submit reports as official complaints to the appropriate state agencies.
User metadata and reports are currently available through one of FracTracker Alliance’s internal APIs (application programming interfaces).  The goal of this clinic project is to build a set of scripts that run nightly to (1) query the API for new reports, (2) route each report to a state agency, and (3) submit the required data through either an automated email or WebDriver tool such as Selenium.  We will start with the seven primary fracking states of California, New Mexico, Colorado, Texas, Ohio, Pennsylvania, and West Virginia and expand to others as time permits. Our scripts will be deployed to Google Cloud Platform (GCP) and run on a Cloud Run or Compute Engine instance that is created and destroyed on demand.

## Description

This project automates webform and email submissions of environmental complaints for FracTracker Alliance, for a list of state and county agencies specified below:


State | Agency Name | Webform or Email Submission
---|---------|------
California |  California EPA Environmental Complaint System | Webform
New Mexico |  New Mexico Environment Department | Webform
Ohio | Ohio Environmental Protection Agency | Webform
Pennsylvania | Pennsylvania Department of Environmental Protection | Webform
Texas | Texas Comission on Environmental Quality | Webform
 | | 
Kentucky | Kentucky Energy and Environment Cabinet | Email
Nebraska | Nebraska Department of Environmental Quality | Email
North Dakota | North Dakota Department of Environmental Quality | Email
Tennessee | Tennessee Department of Environment and Conservation | Email
 | | 
Colorado | Colorado Oil and Gas Conservation Commission | Webform and Email
West Virginia | West Virginia Department of Environmental Protection | Webform and Email

## Setup

To run the project in an interactive terminal using Docker:

1. Install [Docker](https://docker-curriculum.com/) if you have not already done so. Windows users
will have to set up and configure Windows Subsystem for Linux ([WSL2](https://docs.microsoft.com/en-us/windows/wsl/install))
beforehand.

2. Open a new `bash` shell/terminal and enter `sh run.sh`. This script builds the Docker image specified in `.Dockerfile`. After downloading a base Python image, it installs Chromedriver and its dependencies as well as all required Python packages specified in `requirements.txt`. It then runs the container in interactive mode so users can execute Python scripts against it.

3. Shut down the terminal any time by entering `CTRL-d` or `exit 13`.


## Configuration

`config.dev.yaml`, `config.prod.yaml`, and `config.test.yaml` each contains the configuration for the development environment, the production environment, and the testing environment.  

## Utilities

The utilities sub-directory contains a list of utility classes and modules: 
1. `FracAPI` for interfacing with FracTracker Alliance's internal APIs, 
2. `logger.py` for configuring a logger for standard input, 
3. `Metadata` for storing metadata from email and webform submission, 
4. `Location` for generating street address, city, state, and/or county data given a pair of latitude-longitude coordinates, 
5. `Submission` for processing submissions to state agencies, 
6. `SendGridEmail` for  sending email submissions using SendGrid, 
7. `web_utilities.py` for accessing state webform websites, 
8. `config.py` for reading and storing values from the configuration file that corresponds to the current development environment, and 
9. `Datastore` for working with Google Cloud Storage.

## Tests

The tests sub-directory contains a series of Python unit test classes against some of the utilities class: 
1. `TestFracAPI` for the FracTracker API utility class `FracAPI`,
2. `TestGeocode` for the reverse geocoder utility class `Location`,
3. `TestEmailModule` for the email submission utility class `SendGridEmail`. 
4.  a `data` folder that contains a list of test data, including multiple pdf attachments for email submissions and a json file with coordinates for reverse geocoder. 


## Models

The models sub-directory contains a model class, `Report`. It takes in a single json report and creates attributes from json items to store relevant info from API json as class attributes. 


## Submissions

The submissions sub-directory contains the followings:


1. `_example.py`, an example use of Selenium with a headless web browser. To execute the script, launch the Docker container as explained above and then enter the command:

```
python submissions/_example.py
```

  The script navigates to a sample web page, enters a phrase into the search bar, and waits for the page to load before saving a full-page screenshot to the directory `tests/screenshots/`. (NOTE: This code was intended to serve as a quick example. Please don't hardcode file paths; instead, save them as constants, in configuration files, or as environmental variables.)


  To facilitate testing, the entire directory has been mounted. This allows you to make save changes to files and then re-run your scripts to see the effects _without_ restarting the Docker container.


2. `state_email.py`, which contains a class `StateEmail` that represents an email sent to a state agency using SendGrid and reflects the content of environmental complaints submitted by FracTracker mobile app users. All states that require email submissions will need to create a `StateEmail` object in order to submit an environmental complaint in the form of email. All states that require web form submissions will need to import the `web_utilities` module under the `Utilities` sub-directory in order to submit an environmental complaint in the form of webform. All states have to import `Report` in order to retrieve relevant info of reports from the FracTracker API. 


3. `california.py`, `colorado.py`, `kentucky.py`, `nebraska.py`, `new_mexico.py`, `north_dakota.py`, `Ohio.py`, `pennsylvania.py`, `tennessee.py`, `Texas.py`, `West_Virginia.py`, a list of submission filefor each state, each submission file completes and submits webforms and/or emails to the corresponding state agency for fracking complaints, and return the submission results as metadata.  

## Executing program

`main.py` triggers the submission of complaints submitted by FracTracker users to state agencies by querying FracTracker's internal API
for new reports, routing the reports to the appropriate states, and submitting the data through a web form or email for each state to the corresponding state agency. Submission results are saved in a CSV file and stored on Google Cloud. 

To run the program, enter the command:

```
python main.py
```

## Prototype: SSD Connect
[SSD Connect](https://www.figma.com/community/file/1216973904264301889) is an extension of this project. It is an ALL-IN-ONE networking web app for alumni and current students to network and form mentorships based on career and research interests under UChicago's Social Science Division (SSD) 
