# Build and deploy

Command to build the application. PLease remeber to change the project name and application name
```
gcloud builds submit --tag gcr.io/streamlitapp-437103/streamlit-00001-bkf  --project=streamlitapp-437103
```

Command to deploy the application
```
gcloud run deploy --image gcr.io/streamlitapp-437103/streamlit-00001-bkf --platform managed  --project=streamlitapp-437103 --allow-unauthenticated
```
