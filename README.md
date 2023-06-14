# gws-log-export
Google Workspace Log Export tool.

This tool retrieves Google Workspace log files and saves them as json.

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


