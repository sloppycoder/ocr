
# Welcome to your Python project

## quick start

```shell

# create .env file with database details and DocumentAI API info

DATABASE_URL=postgres://@/ocr
PROJECT_ID=<gcp_project_id>
PROCESSOR_LOCATION=us
PROCESSOR_ID=<documentai_processor_id>
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}

# run the django application and djang-q worker

# with hivemind
hivmind

# without hivemind or similiar

# in the first shell
python manage.py runserver

# in the 2nd shell
python manage.py qcluster

```

## open the browser to 

[http://localhost:80000/statements/](http://localhost:80000/statements/)
