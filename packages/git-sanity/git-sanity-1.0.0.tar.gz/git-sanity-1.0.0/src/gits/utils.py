import json
import logging
import os
import subprocess
from gits import __gits_root_dir__
from gits import __gits_config_file_name__

def run(command, workspace="./", env=os.environ, capture_output=False):
    """
    Execute an external command and return its execution result
    
    This function uses subprocess.run() to execute the specified command, 
    supporting execution in a specified working directory and environment,
    with the ability to capture command output and error messages.
    
    Args:
        command (str/list): Command string or command list to execute (e.g., ["ls", "-l"])
        workspace (str): Working directory path for command execution, defaults to current directory(".")
        env (dict): Environment variables dictionary, defaults to os.environ (current process environment)
        capture_output (bool): Whether to capture command's standard output and error output, defaults to False
    
    Returns:
        - When capture_output is True, returns tuple: (stdout_str, stderr_str)
        - When capture_output is False, returns boolean: whether command executed successfully (returncode == 0)
    
    Examples:
        >>> run(["ls", "-l"], capture_output=True)
        ('total 8\n-rw-r--r-- 1 user group 1234 Jan 1 12:34 file.txt', '')
        
        >>> run("ls -l", capture_output=False)
        True
    """
    logging.debug("gits (cwd:{}) Running: {}".format(workspace, command))
    result = subprocess.run(
        command,
        cwd=workspace,
        env=env,
        text=True,
        capture_output=capture_output
    )
    logging.debug("gits result: {}".format(result))
    return result


def get_gits_dir(start_path=None):
    if start_path is None:
        start_path = os.getcwd()

    current_path = os.path.abspath(os.path.expanduser(start_path))
    while True:
        gits_path = os.path.join(current_path, __gits_root_dir__)
        if os.path.isdir(gits_path):
            return current_path
        
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            break
        current_path = parent_path
    return None


def load_user_config():
    gits_dir = get_gits_dir()
    if gits_dir is None:
        logging.error("cannot find gits repository from current path: {}".format(os.getcwd()))
        exit(1)

    gits_config_file_path = os.path.join(gits_dir, __gits_root_dir__, __gits_config_file_name__)
    if os.path.exists(gits_config_file_path):
        with open(gits_config_file_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        return user_config
    else:
        logging.error("{} does not exist.".format(gits_config_file_path))
        exit(1)


# JSON-style comment markers (similar to HTML comments)
json_comment_prefix = "<!--"
json_comment_suffix = "-->"
def get_user_config(user_config, field_path, default=None):
    """
    Safely retrieves a nested configuration value from a dictionary using dot notation,
    with support for commented-out values.
    
    Args:
        user_config (dict): Configuration dictionary to search through
        field_path (str): Dot-separated path to the desired field (e.g. 'parent.child')
        default: Default value to return if path doesn't exist or is commented
    
    Returns:
        The found value if path exists and isn't commented, otherwise returns default.
        Returns None if no default is specified.
    """
    keys = field_path.split('.')
    current = user_config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif default is None:
            logging.error("there is no key({}) in user_config({})".format(field_path, user_config))
        else:
            return default

    if isinstance(current, str) and current.startswith(json_comment_prefix) and current.endswith(json_comment_suffix):
        if default is None:
            logging.error("there is no value of key({}) in user_config({})".format(field_path, user_config))
        else:
            return default
    else:
        return current


def get_projects_by_group(user_config, group_name):
    """
    Retrieve all projects belonging to a specified group from user configuration
    
    Args:
        user_config (dict): Dictionary containing user configuration with 'projects' and 'groups'
        group_name (str): Name of the group to filter projects by
    
    Returns:
        list: List of project dictionaries that belong to the specified group.
              Returns all projects if group_name is "all"
    """
    all_projects = get_user_config(user_config, "projects", default=[])
    if group_name == "all":
        return all_projects
    
    result_projects = []
    for group in get_user_config(user_config, "groups", default=[]):
        if get_user_config(group, "group_name") != group_name:
            continue

        target_projects = get_user_config(group, "projects", default=[])
        for project in all_projects:
            if get_user_config(project, "name", default="") in target_projects:
                result_projects.append(project)

    return result_projects


def update_user_config(key_path, new_value):
    if isinstance(key_path, str):
        keys = key_path.split('.')
    else:
        keys = key_path

    user_config = load_user_config()
    current = user_config
    for key in keys[:-1]:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            logging.error("key_path({}) does not exist".format(key_path))
            return False

    final_key = keys[-1]
    if isinstance(current, dict) and final_key in current:
        current[final_key] = new_value
    else:
        logging.error("key_path({}) does not exist".format(key_path))
        return False

    gits_config_file_path = os.path.join(get_gits_dir(), __gits_root_dir__, __gits_config_file_name__)
    with open(gits_config_file_path, "w", encoding="utf-8") as f:
        json.dump(user_config, f, indent=4, ensure_ascii=False)
    return True