import json
import logging
import os
from gits import __gits_root_dir__
from gits import __gits_config_file_name__
from gits.utils import run

default_config = {
    "this_is_a_comment_example": "<!--JSON-style comment markers (similar to HTML comments)-->",
    "working_branch": "<!--change via the `gits switch` command, default=None-->",
    "projects": [
        {
            "name": "<!--project's name-->",
            "url": "<!--project's repo url>",
            "branch": "<!--branch's name-->",
            "local_path": "<!--local path to clone repo, default=.>",
            "additional_remote": [
                {"<!--remote's name-->": "<!--remote's url-->"}
            ],
            "forward_to_git": {
                "clone": ["<!--command args of git clone, eg:--depth=1-->"]
            }
        }
    ],
    "groups": [
        {
            "group_name": "all",
            "projects": [
                "<!--project_name, default=[]-->"
            ]
        }
    ]
}

def gits_init_impl(args):
    """
    Initialize a gits repository with optional URL or local configuration
    
    Parameters:
    - args: Command-line arguments object containing:
        * directory: Target directory for repository
        * URL: Optional remote repository URL for cloning
        
    Returns:
    - None (exits with status code 0 on success, 1 on failure)
    """
    if not os.path.isdir(args.directory):
        logging.error("the value of -d/--directory is not a valid path: {}".format(args.directory))
        exit(1)

    gits_repo_path = os.path.join(args.directory, __gits_root_dir__)
    if os.path.isdir(gits_repo_path):
        logging.error("reinitialized existing gits repository in {}".format(args.directory))
        exit(0)

    os.mkdir(gits_repo_path)
    if args.url and run(["wget", args.url], workspace=gits_repo_path, capture_output=True).returncode == 0:
        exit(0)
    elif args.url:
        os.rmdir(gits_repo_path)
        logging.error("failed to initialize gits with {}".format(args.url))
        exit(1)
    else:
        gits_config_file_path = os.path.join(gits_repo_path, __gits_config_file_name__)
        with open(gits_config_file_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        logging.warn("default config file created at {}. Customize as needed.".format(gits_config_file_path))
        exit(0)
