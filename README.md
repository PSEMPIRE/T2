# Webhook Listener Handbook

## Overview

This Webhook Listener is designed to listen for GitHub pull request events and, when triggered, automatically clones the django repository, run tests, generate a coverage report along with test report and post the results back to the PR as a comment. This process ensures that developers receive instant feedback on their pull requests with test results and coverage.

---

## Prerequisites

To use this webhook listener, ensure you have:

1. **GitHub Token**: To interact with GitHub's API, you’ll need a GitHub token of django repo and flask repo with necessary permissions.
2. **Python Environment**:
   - Python Installed
   - Required Python packages, as specified in the Django repo’s requirements.txt.
    
3. **Flask**: A web framework for setting up the server to receive GitHub webhooks.
4. **Git**: For cloning repositories and pushing results to remote repositories.
5. **Testing Tools**:
   - pytest and coverage for running tests and generating reports.

---

## Setup

### Step 1. Clone the Webhook Listener Repository

Clone this repository to your local environment or server.

```bash
git clone https://github.com/yourusername/webhook-listener.git

cd webhook-listener
```
### 2. Install Dependencies
Make sure you have Python and the required dependencies installed. Use pip to install the packages:

```bash
pip install -r requirements.txt
```
### 3. Create a .env File for Environment Variables
In the root directory, create a .env file to store your GitHub tokens and other environment variables:

```bash 
GITHUB_TOKEN=your-github-token
TEST_TOKEN=your-test-repo-token
```
### 4. Configure GitHub Webhook
1. Go to Settings > Webhooks in your GitHub repository and click Add webhook.
2. In the "Payload URL" field, enter the URL of your webhook listener (e.g., http://your-server-url/webhook).
3. Set the content type to application/json.
4. Select Pull request events (e.g., opened, synchronized, closed).
5. Save the webhook.

---

## Workflow of the Webhook Listener

### 1.Receiving Webhook Events
The webhook listener receives PR events from GitHub. Each payload includes details about the PR, such as its number and repository URL.

When a PR is opened or synchronized, the webhook_listener function is triggered, calling handle_pr to clone the repository, run tests, and generate a coverage report.

### 2. Cloning the Repository
The handle_pr function clones the target repository (e.g., Django project) to a temporary directory:

```python
import git

repo_dir = "/tmp/django-repo"
git.Repo.clone_from(DJANGO_REPO, repo_dir)
```
It uses the git library to clone the repository into a temporary directory. The repository URL and branch are specified through environment variables.

### 3. Running Tests with Coverage
Once the repository is cloned, the run_tests function installs pytest and coverage, runs tests, and generates a coverage report:

``` python
import subprocess

subprocess.run(["pip", "install", "coverage"], check=True)
subprocess.run(
["coverage", "run", "--source=.", "manage.py", "test"],
cwd=django_project_path,
check=True
)
```
It generates both a coverage report and an HTML report (index.html in the htmlcov folder).

### 4. Posting Results to GitHub
The push_results function uploads the index.html coverage report to a GitHub Pages repository, and posts the report URL as a comment on the PR.

```python
import requests

comment_body = f"Coverage report available at: {report_url}"
comment_url = f"https://api.github.com/repos/yourusername/yourrepo/issues/{pr_number}/comments"
response = requests.post(comment_url, json={"body": comment_body}, headers=headers)
```
The URL to the coverage report is then posted as a comment on the pull request.

---

## Running the Webhook Listener

### 1. Start Flask Server
You can run the Flask server with the following command:

```bash
python app.py
```
This starts the server on port 8000 by default. For production, deploy it to a server like AWS or Heroku that can handle web traffic.

### 2. Testing the Webhook
To test the webhook:

- Create a PR in your GitHub repository to trigger the webhook.
- Alternatively, use a tool like ngrok to expose your local server to the internet and test the webhook manually.

---

## Managing the Results

### 1. Viewing the Test Results
Once the webhook is triggered and the test results are posted, you can view them by going to the pull request in your GitHub repository. The comment will include a link to the test results in GitHub Pages.

### 2. Tracking Comments
If you'd like to store and track the comments (so they don't disappear after a page refresh), you can store them in a file (e.g., comments.json) and update them whenever a new comment is added.

---

## Common Issues and Troubleshooting

### 1. Issue: Webhook Not Triggering
- Verify the GitHub webhook configuration.
- Confirm that your server can receive incoming requests from GitHub.

### 2. Issue: GitHub API Authentication
- Ensure that your GITHUB_TOKEN has the correct permissions to post comments on PRs. The token should have repo and workflow scopes.

### 3. Issue: Coverage Report Not Showing Styles
- Ensure the assets folder (containing style.css) is correctly pushed to the gh-pages branch.
- Check the HTML report to confirm the CSS is being linked correctly.

---

## Best Practices

### 1.Security
- Avoid hardcoding sensitive tokens directly into the codebase. Always use environment variables or secret management tools.

### 2.Error Handling
- Make sure to implement proper error handling in the webhook listener, especially for failed repository clones or test runs.

### 3.Local Testing 
- Before deploying to production, test your webhook locally using a tool like ngrok to ensure it works as expected.

---

## Conclusion
This webhook listener automates the process of running tests, generating coverage reports, and posting results to GitHub pull requests. It helps ensure that the code is properly tested before being merged into the main branch, providing continuous feedback to developers.
