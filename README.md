# Webhook Listener Handbook

## Overview

This Webhook Listener is designed to listen for GitHub pull request events and, when triggered, automatically clones the django repository, run tests, generate a coverage report along with test report and post the results back to the PR as a comment. This process ensures that developers receive instant feedback on their pull requests with test results and coverage.

---

# Webhook Listener for Automated Testing and Reporting

This Flask application listens to webhook events, clones specified GitHub repositories, runs tests, and posts reports back to the pull request (PR) as comments. This setup includes environment variables, dependency installation, and report generation. 

## Prerequisites

- **Python 3.7+**
- **Pip** (Python package installer)
- **Git** (to clone repositories)
- **GitHub Access Tokens** for accessing private repositories


## Setup Instructions

### 1. Clone this Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Dependencies
Install required Python packages with:
```bash
pip install -r requirements.txt
```
### 3. Create a .env File
Create a .env file in the root directory to securely store your GitHub tokens:
```bash
GITHUB_TOKEN=<your_github_token>
TEST_TOKEN=<your_test_repo_token>
```

### 4. Environment Variables
GITHUB_TOKEN: Personal access token for accessing the Django repository (DJANGO_REPO).
TEST_TOKEN: Personal access token for accessing the test results repository (TESTS_REPO).

### 5. Running the Application
Run the application using:

```bash
python app.py
```
The application will start and listen on http://0.0.0.0:8000.

### 6. Set Up a Webhook
- Go to your GitHub repository.
- Under Settings > Webhooks, add a new webhook with:
```
Payload URL: http://<your-local-ip>:8000/webhook
Content Type: application/json
```
- Trigger Events: Pull Request (select Pull request events).
Save the webhook.

### 7. Testing the Webhook
a. Create or update a pull request in the monitored repository.

b.The webhook will be triggered, and the application will:
- Clone the repository
- Run tests
- Generate coverage and test reports
- Post a comment on the pull request with links to the reports
