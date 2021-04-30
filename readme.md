# BAG FAQ Crawler

## Prerequisites
Running python 3.7 and virtualenv installed (pip install virtualenv)

## Install required libraries

pip install -r requirements.txt

## Run

python -m src watson_api_key watson_skill_id watson_workspace_url bag_faq_url

## Bundle for IBM Cloud function
cd venv && virtualenv virtualenv && source virtualenv/bin/activate && pip install -r ../requirements.txt && cd .. && deactivate
cd venv && zip -r ../bag_faq_crawler.zip virtualenv && cd ../src && zip ../bag_faq_crawler.zip *.py && cd ..

## Deploy as IBM Cloud function
ibmcloud fn action update bag_faq_crawler bag_faq_crawler.zip --kind python:3.7 --main src