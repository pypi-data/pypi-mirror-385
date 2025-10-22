import logging
import os
from gits.utils import run
from gits.utils import get_gits_dir
from gits.utils import load_user_config
from gits.utils import get_user_config
from gits.utils import get_projects_by_group

def gits_branch_impl(args):
    """
    Implementation for managing Git branches across multiple projects.
    
    Args:
        args: Command-line arguments containing:
            - group (str): Group name to filter projects
            - delete (str): Branch name to delete (non-force)
            - force_delete (str): Branch name to force delete
    
    Returns:
        None
    """
    user_config = load_user_config()
    for project in get_projects_by_group(user_config, args.group):
        project_name = get_user_config(project, "name")
        logging.info("Processing branches for {}...".format(get_user_config(project, "name")))
        logging.debug("Processing project={}".format(project))

        repo_path = os.path.join(get_gits_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error("the remote {} project branch hasn't been pulled locally yet.".format(project_name))
            exit(1)

        branch_cmd = ["git", "branch"]
        if args.delete is not None:
            branch_cmd.extend(["-d", args.delete])
        elif args.force_delete is not None:
            branch_cmd.extend(["-D", args.force_delete])
        run(branch_cmd, workspace=repo_path)
