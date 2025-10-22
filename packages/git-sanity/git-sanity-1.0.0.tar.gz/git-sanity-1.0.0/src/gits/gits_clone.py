import logging
import os
from gits.utils import run
from gits.utils import get_gits_dir
from gits.utils import load_user_config
from gits.utils import get_user_config
from gits.utils import get_projects_by_group

def gits_clone_impl(args):
    """
    Implements the gits clone operation for multiple projects based on user configuration
    
    This function:
    1. Loads user configuration from arguments
    2. Retrieves all projects belonging to the specified group
    3. Clones each project using git clone with configured parameters
    4. Handles optional forward_to_git parameters
    5. Uses configured workspace or current directory as default
    
    Args:
        args: Command-line arguments containing group name and other configuration
        
    Returns:
        None (performs side effects by cloning repositories)
    """
    user_config = load_user_config()
    for project in get_projects_by_group(user_config, args.group):
        logging.info("Cloning {}...".format(get_user_config(project, "name")))
        logging.debug("Cloning project={}".format(project))

        clone_cmd = ["git", "clone", get_user_config(project, "url"), "-b", get_user_config(project, "branch")]
        clone_cmd.extend(get_user_config(project, "forward_to_git.clone", []))

        workspace = os.path.join(get_gits_dir(), get_user_config(project, "local_path", "."))
        result = run(clone_cmd, workspace=workspace)
        if result.returncode == 0:
            for remote in get_user_config(project, "additional_remote", []):
                for remote_name, remote_url in remote.items():
                    run(["git", "remote", "add", remote_name, remote_url], workspace=os.path.join(workspace, get_user_config(project, "name")))
