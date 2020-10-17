from flask import Flask, request, jsonify, abort
import json
import filecmp
from shutil import copy
from pathlib import Path
from os import environ
from git import exc, Repo

app = Flask(__name__)
app.config['DEBUG'] = True

GITLAB_USERNAME = environ['GITLAB_USERNAME']
GITLAB_PASSWORD = environ['GITLAB_PASSWORD']
GITLAB_SECRET_TOKEN = environ['GITLAB_SECRET_TOKEN']

GIT_TEMP_REPO = Path('/tmp/repos') if "GIT_TEMP_REPO" not in environ else Path(environ['GIT_TEMP_REPO'])
COREDNS_FILE_MAP = json.loads(environ['COREDNS_FILE_MAP'])


def repo_exist(directory):

    try:
        Repo(directory)
        return True

    except exc.NoSuchPathError:
        return False

    except exc.InvalidGitRepositoryError:
        return False


@app.errorhandler(400)
def resource_not_found(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(401)
def resource_not_found(e):
    return jsonify(error=str(e)), 401


@app.route('/', methods=['GET'])
def index():
    # GET Request
    if request.method == 'GET':
        return '<h1>CoreDNS Webhook Listener</h1>'


@app.route('/', methods=['POST'])
def update_records():
    # Check that event is validated
    if request.headers['X-Gitlab-Token'] != GITLAB_SECRET_TOKEN:
        abort(401, description="Invalid token")

    # Ensure event is push event
    if request.headers['X-Gitlab-Event'] != "Push Hook":
        abort(400, description="only accepts push hooks")

    # Pull the webhook
    request_json = request.get_json()
    repo_name = request_json['repository']['name']
    repo_dir = GIT_TEMP_REPO.joinpath(repo_name)

    # Check if repo exist already
    does_repo_exist = repo_exist(directory=str(repo_dir))

    # Clone the repo if it doesn't exist
    if not does_repo_exist:

        # Login to the repo
        git_login = f"{GITLAB_USERNAME}:{GITLAB_PASSWORD}@"
        repo_login = \
            request_json['project']['git_http_url'][:8] + git_login + request_json['project']['git_http_url'][8:]

        # Clone the repo
        Repo.clone_from(repo_login, str(repo_dir))

    else:

        # Update (pull) the repo
        Repo(str(repo_dir)).remotes.origin.pull()

    # copy files to mapped directory
    for mapped_directory in COREDNS_FILE_MAP:

        # get full path of repo path
        mapped_dir_full_path = repo_dir.joinpath(mapped_directory)

        dir_file_comparison = filecmp.dircmp(
            mapped_dir_full_path,
            COREDNS_FILE_MAP[mapped_directory]
        ).right_only

        for file in dir_file_comparison:
            Path(COREDNS_FILE_MAP[mapped_directory]).joinpath(file).unlink()

        for files in mapped_dir_full_path.iterdir():

            # don't copy directories
            if not files.is_file():
                continue

            # copy file
            copy(str(files), COREDNS_FILE_MAP[mapped_directory])

    return {"success": "file added"}
