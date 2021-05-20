# BAG FAQ Crawler

## Prerequisites
Running python 3.7 and virtualenv installed (pip install virtualenv)

## Install required libraries
```
pip install -r requirements.txt
```
## Run
```
python3 __main_local__.py [watson_api_key] [watson_skill_id] [watson_workspace_url] [bag_faq_url] [vaccination_center_url]
```
## Bundle for IBM Cloud function
```
cd venv && virtualenv virtualenv && source virtualenv/bin/activate && pip install -r ../requirements.txt && cd .. && deactivate
rm -fr venv/virtualenv/lib/python3.7/site-packages/lxml*
rm -f bag_faq_crawler.zip && rm -fr *.pyc src/*.pyc __pycache__ src/__pycache__
cd venv && zip -r ../bag_faq_crawler.zip virtualenv && cd .. && zip bag_faq_crawler.zip src/*.py && zip bag_faq_crawler.zip __main__.py
```
## Deploy as IBM Cloud function
```
ibmcloud fn action update bag_faq_crawler bag_faq_crawler.zip --kind python:3.7
```