# gws-log-export
Google Workspace Log Export tool.

This tool retrieves Google Workspace log files and saves them as json.

```
usage: gws-log-export.py [-h] --credential-file CREDENTIAL_FILE --credential-subject CREDENTIAL_SUBJECT --start-date START_DATE
                         [--end-date END_DATE] [--applications APPLICATIONS [APPLICATIONS ...]] [--all-applications] [--compress]
                         [--show-all-applications] [--debug] [--output-directory OUTPUT_DIRECTORY] [--interval INTERVAL] [--user USER]

Google Admin SDK reports_v1 API arguments parser

optional arguments:
  -h, --help            show this help message and exit
  --credential-file CREDENTIAL_FILE
                        Path to the JSON file with Google service account credentials
  --credential-subject CREDENTIAL_SUBJECT
                        E-mail of an account to act as to retrieve logs
  --start-date START_DATE
                        Date from which to retrieve the logs, must be formatted as ISO8601 datetime
  --end-date END_DATE   End date for logs retrieval, defaults to current date and time if not provided
  --applications APPLICATIONS [APPLICATIONS ...]
                        List of applications for which to retrieve log files
  --all-applications    Flag to select all applications from a list of all known reports_v1 applications
  --compress            Compress outputs as gz
  --show-all-applications
                        Only display all valid application choices
  --debug               Flag to set logging level to debug in the loguru module
  --output-directory OUTPUT_DIRECTORY
                        Directory where to output retrieved data, defaults to current directory if not provided
  --interval INTERVAL   Time in minutes into which the logs will be split for retrieval
  --user USER           User account to retrieve, defaults to all
```

## Get started
You need to grant a service account the necessary permissions:

1. Granting access to the API: You need to grant the service account access to the necessary APIs from the Google Cloud Console.
2. Delegating domain-wide authority to the service account: To call the Reports API as a user in a Google Workspace domain, the service account must be delegated domain-wide authority by a super administrator for the domain.

### Granting access to the API

* From the Google Cloud Console, go to IAM & Admin > IAM.
* Find the service account in the list.
* Click on the pencil icon to edit the service account.
* Click on Add Another Role.
* In the Role dropdown, find the appropriate role (for Reports API, you'd typically need Roles > Logging > Logs Viewer or any other role that grants the necessary permissions).
* Click Save.
* If you have not enabled Admin API for the project you created, enable that API.

### Delegating domain-wide authority to the service account

* From your Google Admin console (admin.google.com), go to Security > API controls.
* In the Domain wide delegation panel, select Manage Domain Wide Delegation.
* Click Add new.
* In the Client ID field, enter the client ID for the service account. You can find this in your service account JSON file or in the service account details in the Google Cloud Console.
* In the OAuth Scopes field, enter the necessary scopes for the APIs you are using. For the Reports API, you would typically need https://www.googleapis.com/auth/admin.reports.audit.readonly.
* Click Authorize.

### Get Credentials
* Go to your project's service account and click "Add Keys" 
* Download the key and save it.


