import logging
import os
from gits.utils import run
from gits.utils import get_gits_dir
from gits.utils import load_user_config
from gits.utils import get_user_config
from gits.utils import get_projects_by_group
from gits.utils import update_user_config

def gits_switch_impl(args):
    """
    Implements the branch switching functionality for multiple projects based on group configuration.

    Parameters:
    - args: Command-line arguments containing:
        - group: Name of the group to switch branches for
        - new_branch_name: Optional name for the new branch to create (if provided)
        - branch_name: Optional name of the existing branch to switch to (if provided)

    Returns:
    - None (exits with error code 1 on failure)
    """
    user_config = load_user_config()
    projects_of_group = get_projects_by_group(user_config, args.group)
    if not projects_of_group:
        return

    for project in projects_of_group:
        project_name = get_user_config(project, "name")
        logging.info("Switching branch for {}...".format(project_name))
        logging.debug("Switching project={}".format(project))

        if args.new_branch_name is not None:
            switch_cmd = ["git", "switch", "-c", args.new_branch_name, "origin/{}".format(get_user_config(project, "branch"))]
        elif args.branch_name is not None:
            switch_cmd = ["git", "switch", "{}".format(args.branch_name)]
        else:
            logging.error("No branch name provided to switch for {}.".format(project_name))
            exit(1)

        repo_path = os.path.join(get_gits_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error("the remote {} project branch hasn't been pulled locally yet.".format(project_name))
            exit(1)
        if run(switch_cmd, workspace=repo_path).returncode != 0:
            exit(1)
    else:
        update_user_config("working_branch", args.new_branch_name if args.new_branch_name is not None else args.branch_name)
        return
