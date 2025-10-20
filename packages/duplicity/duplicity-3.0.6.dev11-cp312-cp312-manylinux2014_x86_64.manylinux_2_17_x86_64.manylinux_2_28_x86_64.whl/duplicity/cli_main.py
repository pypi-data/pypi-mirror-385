# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf-8 -*-
#
# Copyright 2022 Kenneth Loafman
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Main for parse command line, check for consistency, and set config
"""

import copy
import inspect
import sys
from textwrap import dedent

# TODO: Remove duplicity.argparse311 when py310 xgoes EOL
from duplicity import argparse311 as argparse
from duplicity import backend
from duplicity import config
from duplicity import cli_util
from duplicity import gpg
from duplicity import log
from duplicity import util
from duplicity.cli_data import *


class DuplicityHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """
    A working class to combine ArgumentDefaults, RawDescription.
    Use with make_wide() to insure we catch argparse API changes.
    """


def make_wide(formatter, w=120, h=46):
    """
    Return a wider HelpFormatter, if possible.
    See: https://stackoverflow.com/a/5464440
    Beware: "Only the name of this class is considered a public API."
    """
    try:
        kwargs = {"width": w, "max_help_position": h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("argparse help formatter failed, falling back.")
        return formatter


def new_parser(**kwargs):
    """
    Return properly defined overrideable parser
    """
    action_help = "positional args:\n"
    for var, meta in DuplicityCommands.__dict__.items():
        if var.startswith("__"):
            continue
        action_str = f"  {var2cmd(var)} {' '.join(meta)}"
        action_help += f"{action_str:48}" f"# duplicity {var2cmd(var)} [options] {' '.join(meta)}"
        action_help += "\n"
    action_help += "\n"

    return argparse.ArgumentParser(
        prog="duplicity",
        argument_default=None,
        formatter_class=make_wide(DuplicityHelpFormatter),
        epilog=action_help + help_footer,
        allow_abbrev=True,
        exit_on_error=False,
        **kwargs,
    )


def harvest_namespace(args):
    """
    Copy all arguments and their values to the config module.  Don't copy
    attributes that are 'hidden' (start with an underscore) or whose name is
    the empty string (used for arguments that don't directly store a value
    by using dest="")
    """
    for f in [x for x in dir(args) if x and not x.startswith("_")]:
        v = getattr(args, f)
        setattr(config, f, v)


def parse_log_options(arglist):
    """
    Parse the commands and options that need to be handled first.
    Mainly to make sure logging goes to the right place with correct verbosity.
    Everything else is passed on to the main parsers.
    """
    # set up parent parser
    parser = new_parser(add_help=False)

    # add logging/version options to the parser
    for opt in sorted(logging_options):
        var = opt2var(opt)
        names = [opt] + OptionAliases.__dict__.get(var, [])
        parser.add_argument(*names, **OptionKwargs[var])

    # process parent args now
    try:
        args, remainder = parser.parse_known_intermixed_args(arglist)
    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        command_line_error(str(e))

    return args, remainder


def parse_cmdline_options(arglist):
    """
    Parse remaining argument list once all is defined.
    """
    # interpret logging/version options early
    args, remainder = parse_log_options(arglist)

    # set up parser
    parser = new_parser()

    # add all options to the parser
    for opt in sorted(all_options):
        var = opt2var(opt)
        names = [opt] + OptionAliases.__dict__.get(var, [])
        parser.add_argument(*names, **OptionKwargs[var])

    # parse the options
    try:
        args, remainder = parser.parse_known_intermixed_args(remainder)
    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        command_line_error(str(e))

    # let's test the command and try to assume which action,
    # eventually err out if no valid action could be determined/was given
    if len(remainder) == 2 and remainder[0] not in all_commands:
        if is_path(remainder[0]) and is_url(remainder[1]):
            log.Notice(
                _(
                    "No valid action found. Will imply 'backup' because "
                    "a path source was given and target is a url location."
                )
            )
            remainder.insert(0, "backup")
        elif is_url(remainder[0]) and is_path(remainder[1]):
            log.Notice(
                _(
                    "No valid action found. Will imply 'restore' because "
                    "url source was given and target is a local path."
                )
            )
            remainder.insert(0, "restore")
        else:
            msg = _(
                f"Invalid '{remainder[0]}' action and cannot be implied from the "
                f"given arguments:\n{arglist}\n"
                f"Valid actions are: {all_commands}"
            )
            command_line_error(msg)

    # check for added/removed options
    for opt in remainder:
        if opt.startswith("-"):
            if opt in changed_options:
                command_line_error(
                    dedent(
                        f"""\
                        Option '{opt} was changed in 2.0.0.
                            --file-to-restore to --path-to-restore
                            --do-not-restore-ownership to --no-restore-ownership
                            """
                    )
                )
            elif opt in removed_options:
                removed_commands_string = "\n".join(f"    {c}" for c in sorted(removed_options))
                command_line_error(
                    dedent(
                        f"""\
                        Option '{opt}' was removed in 2.0.0.
                        The following options were deprecated and removed in 2.0.0
                        """
                    )
                    + f"{removed_commands_string}"
                )
            elif opt in removed_backup_options and args.action in ("backup", "full", "incremental"):
                removed_commands_string = "\n".join(f"    {c}" for c in sorted(removed_backup_options))
                command_line_error(
                    dedent(
                        f"""\
                        Option '{opt}' was removed for backup actions in 2.0.0.
                        The following options were deprecated and removed in 2.0.0
                        """
                    )
                    + f"{removed_commands_string}"
                )

    # check for proper action
    if remainder and remainder[0] in all_commands:
        args.action = remainder[0]
    else:
        command_line_error("Missing or invalid explicit or implicit action.")

    # translate aliases to long action
    var = cmd2var(args.action)
    arg_checks = DuplicityCommands.__dict__.get(var, None)
    if not arg_checks:
        for var, aliases in CommandAliases.__dict__.items():
            if var.startswith("__"):
                continue
            if args.action in aliases:
                arg_checks = DuplicityCommands.__dict__.get(var, None)
                args.action = var2cmd(var)
    if not arg_checks:
        command_line_error(f"'{args.action}' is not a valid action or alias.")

    # parse the positionals relating to action
    if len(arg_checks) == len(remainder[1:]):
        for name, val in zip(arg_checks, remainder[1:]):
            func = getattr(cli_util, f"check_{name}")
            setattr(config, name, func(val))
    else:
        command_line_error(
            f"Wrong number of positional args for '{args.action}', got {len(remainder[1:])}\n"
            f"Expected {len(arg_checks)} positionals from {remainder[1:]}."
        )

    # harvest args to config
    harvest_namespace(args)

    return args


def process_command_line(cmdline_list):
    """
    Process command line, set config
    """
    # build initial gpg_profile
    config.gpg_profile = gpg.GPGProfile()

    # parse command line
    args = parse_cmdline_options(cmdline_list)

    # if we get a different gpg-binary from the commandline then redo gpg_profile
    if config.gpg_binary is not None:
        src = copy.deepcopy(config.gpg_profile)
        config.gpg_profile = gpg.GPGProfile(
            passphrase=src.passphrase,
            sign_key=src.sign_key,
            recipients=src.recipients,
            hidden_recipients=src.hidden_recipients,
        )
    else:
        if config.use_gpgsm:
            program = "gpgsm"
        else:
            program = "gpg"
        config.gpg_binary = util.which(program)
    gpg_version = ".".join(map(str, config.gpg_profile.gpg_version))
    log.Info(_(f"GPG binary is {config.gpg_binary}, version {gpg_version}"))
    if config.use_gpgsm and config.gpg_profile.gpg_version < (2, 2, 27):
        log.FatalError(f"Version {gpg_version} of gpgsm is not supported.  Minimum version is 2.2.27")

    # --use-agent is not safe for symmetric encryption.
    # Notify user and let them decide.
    if (
        config.use_agent
        and config.gpg_profile.sign_key is None
        and len(config.gpg_profile.recipients) == 0
        and len(config.gpg_profile.hidden_recipients) == 0
    ):
        log.Warn(
            "Option --gpg-agent is unsafe with symmetric encryption.\n"
            "Refer to https://gitlab.com/duplicity/duplicity/-/issues/799 for more information."
        )

    # shorten incremental to inc, replace backup with inc
    if config.action in ("incremental", "backup"):
        if config.action == "backup":
            config.implied_inc = True
        config.action = "inc"

    # import all backends and determine which one we use
    backend.import_backends()
    remote_url = config.source_url or config.target_url
    if remote_url:
        config.backend = backend.get_backend(remote_url)
    else:
        config.backend = None

    # determine full clean local path
    local_pathname = config.source_path or config.target_path
    if config.action in ["full", "inc", "restore", "verify"]:
        local_path = path.Path(path.Path(local_pathname).get_canonical())
        if config.action == "restore":
            if (local_path.exists() and not local_path.isemptydir()) or (
                os.getcwd() == os.path.realpath(local_path.name).decode()
            ):
                log.FatalError(
                    _(f"Restore '{local_path.uc_name}' is not empty or is current_dir.\nWill not overwrite."),
                    log.ErrorCode.restore_path_exists,
                )
        elif config.action == "verify":
            if not local_path.exists():
                log.FatalError(
                    _(f"Verify directory {local_path.uc_name} does not exist"),
                    log.ErrorCode.verify_dir_doesnt_exist,
                )
        else:
            assert config.action in ("full", "inc")
            if not local_path.exists():
                log.FatalError(
                    _(f"Backup source directory {local_path.uc_name} does not exist."),
                    log.ErrorCode.backup_dir_doesnt_exist,
                )

        config.local_path = local_path

    # generate backup name and set up archive dir
    if config.backup_name is None:
        config.backup_name = generate_default_backup_name(remote_url)
    set_archive_dir(expand_archive_dir(config.archive_dir, config.backup_name))

    # count is only used by the remove-* commands
    config.keep_chains = config.count

    # selection only applies to certain commands
    if config.action in ["full", "inc", "verify"]:
        set_selection()

    # print derived info
    log.Info(_(f"Using archive dir: {config.archive_dir_path.uc_name}"))
    log.Info(_(f"Using backup name: {config.backup_name}"))

    return config.action


if __name__ == "__main__":
    import types

    log.setup()
    action = process_command_line(sys.argv[1:])
    for a, v in sorted(config.__dict__.items()):
        if a.startswith("_") or isinstance(config.__dict__[a], types.ModuleType):
            continue
        print(f"{a} = {v} ({type(config.__dict__[a])})")
    print("verbosity: " + str(log.getverbosity()))
