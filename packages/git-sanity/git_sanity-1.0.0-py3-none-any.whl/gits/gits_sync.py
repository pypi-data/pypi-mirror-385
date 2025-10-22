import logging
import os
from gits.utils import run
from gits.utils import get_gits_dir
from gits.utils import load_user_config
from gits.utils import get_user_config
from gits.utils import get_projects_by_group

def gits_sync_impl(args):
    user_config = load_user_config()
    for project in get_projects_by_group(user_config, args.group):
        project_name = get_user_config(project, "name")
        logging.info("Syncing source for {}...".format(get_user_config(project, "name")))
        logging.debug("Syncing project={}".format(project))

        repo_path = os.path.join(get_gits_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error("the remote {} project branch hasn't been pulled locally yet.".format(project_name))
            exit(1)

        fetch_cmd = ["git", "fetch", "origin"]
        if run(["git", "rev-parse", "--is-shallow-repository"], workspace=repo_path, capture_output=True).stdout == "True":
            fetch_cmd.append("--unshallow")
        if run(fetch_cmd, workspace=repo_path).returncode != 0:
            exit(1)

        rebase_cmd = ["git", "rebase", "origin/{}".format(get_user_config(project, "branch"))]
        if run(rebase_cmd, workspace=repo_path).returncode != 0:
            exit(1)