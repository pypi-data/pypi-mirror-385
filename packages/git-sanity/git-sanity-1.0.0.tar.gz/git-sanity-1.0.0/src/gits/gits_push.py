import logging
import os
from gits.utils import run
from gits.utils import get_gits_dir
from gits.utils import load_user_config
from gits.utils import get_user_config
from gits.utils import get_projects_by_group

def gits_push_impl(args):
    user_config = load_user_config()
    working_branch = get_user_config(user_config, "working_branch")
    if not working_branch:
        logging.error("working_branch is not set. Please set it via `gits switch` command.")
        exit(1)

    for project in get_projects_by_group(user_config, args.group):
        project_name = get_user_config(project, "name")
        logging.info("Pushing {}...".format(get_user_config(project, "name")))
        logging.debug("Pushing project={}".format(project))

        repo_path = os.path.join(get_gits_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error("the remote {} project branch hasn't been pulled locally yet.".format(project_name))
            exit(1)

        current_branch = run(["git", "branch", "--show-current"], workspace=repo_path, capture_output=True).stdout.strip()
        if not current_branch:
            logging.error("failed to get current branch for repo at {}".format(repo_path))
            exit(1)
        elif current_branch != working_branch:
            continue

        check_result = run(["git", "log", "origin/{}..HEAD".format(get_user_config(project, "branch"))], workspace=repo_path, capture_output=True)
        if check_result.returncode != 0 or check_result.stderr.strip():
            logging.error("failed to check for commits to push for repo at {}".format(repo_path))
            exit(1)
        elif not check_result.stdout.strip():
            continue

        push_cmd = ["git", "push", args.remote, current_branch]
        if args.force:
            push_cmd.append("--force")
        result = run(push_cmd, workspace=repo_path)
        if result.returncode != 0:
            exit(1)
