from flask import Flask, request, jsonify
import os
import subprocess
import requests
import git
from dotenv import load_dotenv
import base64


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Retrieve environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TEST_TOKEN = os.getenv("TEST_TOKEN")

TESTS_REPO = f"https://{TEST_TOKEN}@github.com/kartikvermaa/tests-repo.git"
DJANGO_REPO = f"https://{GITHUB_TOKEN}@github.com/rtiwari13/inventory-management-application.git"

@app.route("/webhook", methods=["POST"])
def webhook_listener():
    data = request.json
    if data.get("action") in ["opened", "synchronize"]:
        pr_url = data["pull_request"]["html_url"]
        pr_number = data["number"]
        handle_pr(pr_url, pr_number)
    return jsonify({"message": "Received"}), 200

def handle_pr(pr_url, pr_number):
    repo_dir = "/tmp/django-repo"
    #print(repo_dir)
    if os.path.exists(repo_dir):
        subprocess.run(["rm", "-rf", repo_dir])

    try:
        # Clone the private Django repo
        git.Repo.clone_from(DJANGO_REPO, repo_dir)
        print("Repository cloned successfully.")
        django_project_path = os.path.join(repo_dir, "inventory")
       
        # requirements_path = os.path.join(repo_dir, "requirements.txt")
        # if os.path.exists(requirements_path):
        #     print("Installing requirements...")
        #     subprocess.run(["pip", "install", "-r", requirements_path], check=True)
        #     print("Requirements installed successfully.")
        # else:
        #     print("requirements.txt not found.")
        # Run tests and collect coverage report
        run_tests(django_project_path)
        # Push test results and comment on the PR
        push_results(pr_number)
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return jsonify({"message": "Failed to clone repository"}), 500
# def run_tests(django_project_path):
#     try:
#         # Run Django tests with coverage
#         subprocess.run(
#             ["python", "manage.py", "test"],
#             cwd=django_project_path,
#             check=True
#         )
#         print("Tests ran successfully.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error running tests: {e}")
#         return jsonify({"message": "Failed to run tests"}), 500
def run_tests(django_project_path):
    try:
        # Install dependencies for code coverage if not already installed
        subprocess.run(["pip", "install", "coverage"], check=True)

        # Run Django tests with coverage
        subprocess.run(
            ["coverage", "run", "--source=.", "manage.py", "test"],
            cwd=django_project_path,
            check=True
        )

        # Generate the HTML report
        subprocess.run(
            ["coverage", "html", "--directory=htmlcov"],
            cwd=django_project_path,
            check=True
        )
        print("HTML coverage report generated successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")


def push_results(pr_number):
    # GitHub API details
    results_repo = "kartikvermaa/tests-repo"
    branch = "gh-pages"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Path to the HTML coverage report
    htmlcov_path = "/tmp/django-repo/inventory/htmlcov/index.html"

    if not os.path.exists(htmlcov_path):
        print("No coverage report generated.")
        return

    # Read the index.html file and encode it
    with open(htmlcov_path, "rb") as file:
        content = base64.b64encode(file.read()).decode("utf-8")

    # Define the path in the GitHub repo
    github_file_path = f"pr-{pr_number}/index.html"
    url = f"https://api.github.com/repos/{results_repo}/contents/{github_file_path}"

    # Prepare the payload for uploading the file
    data = {
        "message": f"Add coverage report for PR #{pr_number}",
        "content": content,
        "branch": branch
    }

    # Send the request to create/update the file
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [201, 200]:
        print(f"File {github_file_path} pushed successfully.")
        
        # Construct the URL for the uploaded file
        file_url = f"https://kartikvermaa.github.io/tests-repo/{github_file_path}"
        
        # Comment on the PR with the URL to the coverage report
        comment_url = f"https://api.github.com/repos/{results_repo}/issues/{pr_number}/comments"
        comment_data = {
            "body": f"Coverage and test reports available [here]({file_url})"
        }

        comment_response = requests.post(comment_url, headers=headers, json=comment_data)
        if comment_response.status_code == 201:
            print("Comment added to the PR successfully.")
        else:
            print(f"Failed to add comment: {comment_response.status_code} - {comment_response.text}")
    else:
        print(f"Failed to push {github_file_path}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
