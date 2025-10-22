import argparse
import logging
import os
from gits import __version__
from gits.gits_init import gits_init_impl
from gits.gits_clone import gits_clone_impl
from gits.gits_sync import gits_sync_impl
from gits.gits_switch import gits_switch_impl
from gits.gits_branch import gits_branch_impl
from gits.gits_push import gits_push_impl

def main():
    logging.info("New Run ==================================================")

    gits = argparse.ArgumentParser(
        prog="gits", formatter_class=argparse.RawTextHelpFormatter, description=__doc__
    )
    gits.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = gits.add_subparsers(
        title="sub-commands", help="additional help with sub-command -h"
    )
    gits_init = subparsers.add_parser("init", description="Initialize the projects", help="initialize the projects")
    gits_init.add_argument("-u", "--url", dest="url", help="the gits configuration repository")
    gits_init.add_argument("-d", "--directory", dest="directory", default=".", help="the path to init gits configuration repository")
    gits_init.set_defaults(func=gits_init_impl)

    gits_clone = subparsers.add_parser("clone", description="Clone repo(s)", help="clone repo(s)")
    gits_clone.add_argument("-g", "--group", dest="group", default="all", help="group to clone, default all")
    gits_clone.set_defaults(func=gits_clone_impl)

    gits_sync = subparsers.add_parser("sync", description="Sync source project(s) ", help="sync source project(s)")
    gits_sync.add_argument("-g", "--group", dest="group", default="all", help="projects to sync, default all")
    gits_sync.set_defaults(func=gits_sync_impl)

    gits_switch = subparsers.add_parser("switch", description="Switch branches", help="switch branches")
    gits_switch.add_argument("remote", nargs='?', default="origin", help="remote name to switch branches, default origin")
    gits_switch.add_argument("-g", "--group", dest="group", default="all", help="group to switch branches, default all")
    gits_switch_meg = gits_switch.add_mutually_exclusive_group()
    gits_switch_meg.add_argument("-c", "--create", dest="new_branch_name", help="create a new branch named <new-branch> base on origin/HEAD")
    gits_switch_meg.add_argument("-b", "--branch", dest="branch_name", help="branch to switch to")
    gits_switch.set_defaults(func=gits_switch_impl)

    gits_branch = subparsers.add_parser("branch", description="List or delete branches", help="list or delete branches")
    gits_branch.add_argument("list", nargs='?', default="list", help="list branch names")
    gits_branch.add_argument("-g", "--group", dest="group", default="all", help="group to operate, default all")
    gits_branch_meg = gits_branch.add_mutually_exclusive_group()
    gits_branch_meg.add_argument("-d", "--delete", dest="delete", help="delete fully merged branch")
    gits_branch_meg.add_argument("-D", "--DELETE", dest="force_delete", help="delete branch (even if not merged)")
    gits_branch.set_defaults(func=gits_branch_impl)

    gits_cherry_pick = subparsers.add_parser("cherry-pick", description="TODO:add repo(s)", help="TODO:add repo(s)")

    gits_push = subparsers.add_parser("push", description="Update remote refs along with associated objects", help="update remote refs along with associated objects")
    gits_push.add_argument("remote", default="remote", help="remote branch to be pushed")
    gits_push.add_argument("-g", "--group", dest="group", default="all", help="group to push, default all")
    gits_push.add_argument("-f", "--force", dest="force", action='store_true', help="force updates")
    gits_push.set_defaults(func=gits_push_impl)

    args = gits.parse_args()
    logging.debug("command args={}".format(args))
    if "func" in args:
        args.func(args)
    else:
        gits.print_help()

if __name__ == "__main__":
    main()