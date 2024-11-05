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

#suceess in this we get comment and we can see live report 

def push_results(pr_number):
    # Directory where the tests repo will be cloned
    tests_repo_dir = "/tmp/tests-repo"
    
    # Create the directory if it doesn't exist
    if os.path.exists(tests_repo_dir):
        subprocess.run(["rm", "-rf", tests_repo_dir])
    
    try:
        # Clone the tests repo
        git.Repo.clone_from(TESTS_REPO, tests_repo_dir, branch="gh-pages")
        print("Tests repository cloned successfully.")
        
        # Copy index.html from htmlcov to tests repo
        index_html_source = os.path.join("/tmp/django-repo/inventory/htmlcov/index.html")
        index_html_destination = os.path.join(tests_repo_dir, "index.html")
        
        if os.path.exists(index_html_source):
            subprocess.run(["cp", index_html_source, index_html_destination])
            print("index.html copied to tests repo.")
        else:
            print("index.html not found in coverage report.")
            return

        # Commit and push the changes to gh-pages branch
        repo = git.Repo(tests_repo_dir)
        repo.index.add(["index.html"])
        repo.index.commit("Update coverage report")
        repo.remotes.origin.push("gh-pages")
        print("Coverage report pushed to tests repo successfully.")
        
        # Construct the URL to the index.html file in GitHub Pages
        report_url = f"https://kartikvermaa.github.io/tests-repo/index.html"
        
        # Post a comment on the PR with the URL to the report
        post_comment(pr_number, report_url)

    except Exception as e:
        print(f"Error in push_results: {e}")

def post_comment(pr_number, report_url):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    comment_body = f"Coverage report available at: {report_url}"
    comment_url = f"https://api.github.com/repos/rtiwari13/inventory-management-application/issues/{pr_number}/comments"
    
    response = requests.post(comment_url, json={"body": comment_body}, headers=headers)
    
    if response.status_code == 201:
        print("Comment posted successfully.")
    else:
        print(f"Failed to post comment: {response.status_code} - {response.text}")



 #success
# def push_results(pr_number):
#     results_repo_dir = "/tmp/tests-repo"
#     if os.path.exists(results_repo_dir):
#         subprocess.run(["rm", "-rf", results_repo_dir])

#     try:
#         # Clone the test results repo
#         git.Repo.clone_from(TESTS_REPO, results_repo_dir)
#         print("Tests repo cloned successfully.")
        
#         # Copy coverage report
#         subprocess.run(["cp", "-r", "/tmp/django-repo/inventory/htmlcov/index.html", f"{results_repo_dir}/pr-{pr_number}"])
        
#         # Commit and push results
#         repo = git.Repo(results_repo_dir)
#         repo.git.add(A=True)
#         repo.index.commit(f"Add coverage report for PR #{pr_number}")
#         repo.remote("origin").push()
#         print("Coverage report pushed successfully.")
        
#         # Comment on the PR with a link to the coverage report
#         comment_url = f"https://api.github.com/repos/rtiwari13/inventory-management-application/issues/{pr_number}/comments"
#         headers = {"Authorization": f"token {GITHUB_TOKEN}"}
#         data = {
#             "body": f"Coverage and test reports available [here](https://kartikvermaa.github.io/tests-repo/pr-{pr_number}/index.html)"
#         }
#         response = requests.post(comment_url, headers=headers, json=data)
#         if response.status_code == 201:
#             print("Comment added to the PR successfully.")
#         else:
#             print(f"Failed to add comment: {response.status_code} - {response.text}")
#     except Exception as e:
#         print(f"Error processing test results: {e}")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)







