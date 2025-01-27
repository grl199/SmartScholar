# SmartScholar

Design of a LangGraph architecture that takes an academic paper as an input (pdf), extracts the relevant sections, summaries, and keywords, and loads the result as structured data in a database on GCP BigQuery.

## Features

- Extracts raw text from PDF files
- Identifies and extracts sections from academic papers
- Summarizes sections and identifies keywords
- Loads structured data into Google Cloud BigQuery

## Setup Instructions

### Prerequisites

- Python 3.11
- [Pipenv](https://pipenv.pypa.io/en/latest/)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Google Cloud BigQuery account and credentials

### Running the App Locally

First, clone the following repository:

```sh
git clone https://github.com/grl199/SmartScholar.git
cd SmartScholar
```
Install dependencies**

```sh
pipenv install
```

Set up environment variables: Create a .env file in the root directory of your project and add the following environment variables: 

```
OPENAI_API_KEY=your_open_api_token 
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
```
GOOGLE_APPLICATION_CREDENTIALS is mandatory. OPENAI_API_KEY may be replaced by any API token needed for the user's preferred LLM. Modify config.yaml just in case the user wants to make use of a specific LLM


```sh
pipenv run streamlit run src/main.py 
```

### Running the App on Google Cloud 

To install, you may find instructions [here](https://cloud.google.com/sdk/docs/install). 
Once completed, authenticate, set your Google Cloud project and enable required services:

```sh
gcloud auth login
```

```sh
gcloud config set project YOUR_PROJECT_ID
```

```sh
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

Create yaml file in the root directory. Again, the environment variables show a free API token as an example

```yaml
runtime: python39

entrypoint: pipenv run streamlit run src/main.py

env_variables:
  OPENAI_API_KEY: your_openai_api_token
  GOOGLE_APPLICATION_CREDENTIALS: path/to/your/credentials.json

handlers:
- url: /.*
  script: auto
```

To deploy your application, 

```sh
gcloud app deploy
```
 After deployment, you will receive a URL where your application is hosted. You can access your Streamlit application using this URL. The URL will typically be in the format:

```
https://YOUR_PROJECT_ID.REGION_ID.r.appspot.com
```

## Additional comments

* This is a simple application that runs a LLM agent with a few nodes. Proper data extraction and checking can be achieved with a more complex graph to ensure robustness. For instance, we may "challenge" the output of one LLM node using another LLM node
* The app's interface is built upon Streamlit and can be further refined. This is just an alpha version
* To ensure better portability, an example Dockerfile is also contained in this repo. Creating an image of this app an deploying it is quite straightforward too