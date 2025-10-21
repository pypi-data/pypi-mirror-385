# src/konvigius/cli_parser.py

import argparse
from . import Config


def create_args_from_cfg(
    cfg: Config, cfg_kwargs: dict = None, show_help_defaults: bool = True
) -> list[dict, ...]:

    if cfg_kwargs is None:
        cfg_kwargs = {}

    parser_args = []

    # from cg.options create parse-arger argument keywords etc
    for opt in cfg._metadata.values():

        kwargs = cfg_kwargs.get(opt.name) or {}

        # option names
        names = []
        if opt.short_flag:
            names.append("-" + opt.short_flag)
        names.append("--" + opt.name.replace("_", "-"))

        # boolean flags
        if opt.field_type is bool:
            # if opt.name.startswith('no_'):
            #     if not 'dest' in kwargs:
            #         kwargs['dest'] = opt.name.partition('_')[2]
            #     if not 'action' in kwargs:
            #         kwargs['action'] = "store_false"
            # else:
            # inverted boolean
            if "dest" not in kwargs:
                kwargs["dest"] = opt.name
            if "action" not in kwargs:
                kwargs["action"] = "store_true"
        else:
            # non-boolean args

            if opt.field_type is int:
                kwargs["metavar"] = "NUM"
            elif opt.field_type is str:
                kwargs["metavar"] = "CHARS"

            # nargs='?' : 0 or 1 integer required
            # const=1   : Used when -s is passed without a number
            # default=1 : Used when -s is not passed at all

            if "type" not in kwargs:
                kwargs["type"] = opt.field_type
            if "nargs" not in kwargs:
                kwargs["nargs"] = "?"
            if "dest" not in kwargs:
                kwargs["dest"] = opt.name
            if "default" not in kwargs:
                kwargs["default"] = opt.default_value

        # common args
        if "help" not in kwargs:
            h = opt.help_text
            if show_help_defaults and opt.field_type is not bool:
                if opt.field_type is str:
                    help_ = f'{h} (default: "{opt.default_value}")'
                else:
                    help_ = f"{h} (default: {opt.default_value})"
            else:
                help_ = f"{h}"
            kwargs["help"] = help_

        parser_args.append({"names": names, "kwargs": kwargs})

    return parser_args


def build_parser(parser_args) -> argparse.ArgumentParser:
    """
    Builds an argparse.ArgumentParser from a Config instance's metadata.

    Args:
        config (Config): The config object whose schema metadata will be used
                         to define CLI arguments.

    Returns:
        argparse.ArgumentParser: A parser configured from the config's schema.

    Raises:
        ConfigMetadataError: If an invalid short flag is found in the schema.
    """
    parser = argparse.ArgumentParser()
    for args in parser_args:
        parser.add_argument(*args["names"], **args["kwargs"])
    return parser


def run_parser(
    cfg: Config, parser_args: list[dict, ...] = None, cli_args=None
) -> argparse.ArgumentParser:
    """
    Parses CLI arguments and updates the given config instance with parsed values.

    Args:
        config (Config): The config object to update with CLI arguments.
        args (list[str], optional): CLI arguments. If None, defaults to sys.argv[1:].

    Side Effects:
        Modifies the config instance in-place, setting attributes from CLI input.

    Raises:
        Any validation exceptions triggered by invalid CLI values.
    """
    if cli_args is not None:
        # Argparse expects all command-line arguments to be strings, because
        # they normally come from sys.argv, which is a list of strings.
        cli_args = list(map(str, cli_args))

    if not parser_args:
        parser_args = create_args_from_cfg(cfg)

    parser = build_parser(parser_args)
    parsed_args = parser.parse_args(args=cli_args)
    # inspect_actions(parser)
    selected_values = vars(parsed_args)

    # copy choosen CLI value(s) to config
    for name, value in selected_values.items():
        if value is not None:
            # print('writing to cfg: name=', name, 'value=', value)
            try:
                setattr(
                    cfg, name.replace("-", "_"), value
                )  # triggers validation via descriptor
            except AttributeError:
                pass

    return parser, parsed_args


def inspect_actions(parser: argparse.ArgumentParser):
    """Print the actions of a parser to the standard output."""
    for action in parser._actions:
        print(f"Option strings: {action.option_strings}")
        print(f"  Dest: {action.dest}")
        print(f"  Help: {action.help}")
        print(f"  Default: {action.default}")
        print(f"  Required: {action.required}")
        print()


# === END ===
