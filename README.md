# Popbots-Emailling

The emailing system is designed to send email to study participants on a daily, weekly and end of study basis in their local timezone
This project was tailored to Popbots study but can be used for any other project requiring sending emails to participants a regular basis (see adapt this code recommendation)

The process is as follow: 

1. Every Pulls data from the qualtrics registration survey and register new participants. (This survey needs to have some embedded variables see Requirements in survey)


2. Check if the local participants time is over 20h 
    
    if yes: Performed the following action > send daily, weekly or unsubscribe email 
    \n else: proceed to the next participant


## Adapt/Deploy this code: 

1. To deploy

1.1. Create a python3.7 venv (see online tutorials) recommended name popbots_emailing_venv
- Activate the venv by doing: 
    > source "venv_name"/bin/activate
- install all the required packages by navigating into the popbots folder and running 
    > pip3 install -r requirements.txt

1.1.2 Set the required environment variables 

```bash
QUALTRICS_API_TOKEN # qualtrics api this must be requested at stanford university
DATA_CENTER #this is given by the organization on qualtrics , in our case stanford university
SURVEY_ID # this is the id of the survey, can be found on the web link
FILE_FORMAT="csv" #must be set as csv for this code

EMAILING_HASHING_KEY #this is a key that you set yourself to hash the user's data before storing it

#gmail credentials, your google account must be set on lower security
GMAIL_ADDRESS  
GMAIL_PASSWORD 
```

## These are recommendations to adapt this code to any project

* Disable the server.sendemail instruction while testing. This is to make sure you won't accidentally send bad emails, or 10000 emails due to a loop

* Change the study duration variable : STUDY_DURATION_DAYS in days to fit your experiment length

* Change the email templates in the email_views folder

* Edit the emails directory, type, embedded variables 

* Adapt the qualtrics (to store) survey variables in the in the fetch_update_participants() function. This function creates all the PARTICIPANT class instances and store them in a pickle file locally.  ( You may want to edit the code to push this to a database)
 
Note: you must update the participant class if you need to add more info for participant 

## Requirements in Qualtrics Survey:


Use this JS to catch the user's timezone from their browsers. 

After declaring (id, timeZoneOffset, INATZ,population) as embedded variables in Qualtrics

```
id = ${rand://int/1000000:9999999}  
```

```js
Qualtrics.SurveyEngine.addOnload(function() {
    var d = new Date();
	var n = d.getTimezoneOffset()
	var tz = Intl.DateTimeFormat().resolvedOptions().timeZone
    Qualtrics.SurveyEngine.setEmbeddedData("timeZoneOffset", n);
	Qualtrics.SurveyEngine.setEmbeddedData("INATZ", tz); // fetch the user's timezone

});
```
INATZ is the variables like https://en.wikipedia.org/wiki/List_of_tz_database_time_zones?oldformat=true

population was set to either intervention/group



