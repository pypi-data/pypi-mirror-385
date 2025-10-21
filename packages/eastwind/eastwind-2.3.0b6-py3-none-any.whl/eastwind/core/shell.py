# -*- coding: utf-8 -*-
import os
import sys
import shlex
import asyncio
from argparse import ArgumentParser
from typing import Callable, Awaitable, TypeAlias
from starlette.datastructures import State
from eastwind.lib.exception import (
    CliCommandError,
    EastwindCriticalError
)
from eastwind.lib.util import (
    import_module,
    run_python,
    BUILTIN_PREFIX,
    PROJECT_PREFIX
)
from eastwind.core.project import (
    Project,
    start_project,
    stop_project
)

COMMAND_EXIT: set[str] = {'exit', 'quit'}


def __help_show_command_list(base_command: str, command_list: list[str]) -> None:
    # When command list is empty, show no command exist text.
    if len(command_list) == 0:
        if len(base_command) == 0:
            print("no available commands")
        else:
            print(f"no available sub commands for {base_command}")
        return
    # Print header and content.
    if len(base_command) == 0:
        print("supported commands:")
    else:
        print(f"{base_command} supported commands:")
    print("\n".join(f" - {key}" for key in command_list))


async def __command_help(state: State, _: list[str]) -> None:
    # Load the project defined user modules.
    config = state.config
    # Use set to merge all the commands.
    all_commands: set[str] = set(BUILTIN_COMMANDS.keys())
    # Tried and check whether these modules have shell command or not.
    def __has_cli(module_prefix: str) -> bool:
        cli_module = import_module(f"{module_prefix}.cli")
        return hasattr(cli_module, "command_handler")

    for builtin_module in config.module_builtin:
        if __has_cli(f"{BUILTIN_PREFIX}{builtin_module}"):
            all_commands.add(builtin_module)
    for user_module in config.module_project:
        if __has_cli(f"{PROJECT_PREFIX}{user_module}"):
            all_commands.add(user_module)
    # Sort the command based on alphabet order.
    all_commands: list[str] = list(all_commands)
    all_commands.sort()
    __help_show_command_list("", all_commands)


async def __command_sm3_hash(_: State, arg_tokens: list[str]) -> None:
    parser = ArgumentParser(
        prog='sm3sum',
        description='Print or check SM3 (256-bit) checksums of a text.',
    )
    parser.add_argument('text', help='The text to hash.')
    args = parser.parse_args(arg_tokens)
    # Print the HEX result.
    from eastwind.lib.util import sm3_hash_text
    print(sm3_hash_text(args.text).hex())


async def __command_hex_to_base64(_: State, arg_tokens: list[str]) -> None:
    parser = ArgumentParser(
        prog='hex_to_base64',
        description='Convert a hex encoded binary to URL safe Base64'
    )
    parser.add_argument('hex_data', help='The hexadecimal encoded bytes to be converted.')
    args = parser.parse_args(arg_tokens)
    try:
        # Convert the hex into byte array.
        hex_bytes: bytes = bytes.fromhex(args.hex_data)
    except Exception:
        raise CliCommandError(f"invalid hexadecimal bytes provided")
    # Use Base64 to encode the bytes.
    from base64 import urlsafe_b64encode
    print(urlsafe_b64encode(hex_bytes).decode())


async def __command_db_init(state: State, _: list[str]) -> None:
    # Ensure the database directory under storage exists.
    from eastwind.lib.path import DIR_STORAGE_DATABASE
    os.makedirs(DIR_STORAGE_DATABASE, exist_ok=True)
    # Initialize the database.
    from eastwind.core.project import iterate_all_modules
    from eastwind.lib.util import import_module
    for _, module_prefix in iterate_all_modules(state):
        target = import_module(f"{module_prefix}.model")
        if target is not None:
            print(module_prefix, flush=True)
    await state.main_db.create_all_tables()
    print("Database initialized successfully")


async def __command_run(_: State, arg_tokens: list[str]) -> None:
    parser = ArgumentParser(
        prog='run',
        description='Run a Eastwind batch script'
    )
    parser.add_argument('script_path', help='The path of the Eastwind shell batch script.')
    args = parser.parse_args(arg_tokens)
    # Launch the command line by line.
    if not os.path.isfile(args.script_path):
        raise CliCommandError(f"script {args.script_path} not found")
    with open(args.script_path, "r", encoding="utf-8") as script_file:
        for script_command in filter(lambda x: x, script_file.readlines()):
            # Ignore the command script.
            if script_command[0] == '#':
                continue
            # Run the command.
            await run_python(__file__, script_command)


CommandHandler: TypeAlias = Callable[[State, list[str]], Awaitable]
CommandMap: TypeAlias = dict[str, CommandHandler]


BUILTIN_COMMANDS: CommandMap = {
    "help": __command_help,
    "sm3sum": __command_sm3_hash,
    "db_init": __command_db_init,
    "hex_to_base64": __command_hex_to_base64,
    "run": __command_run,
}


async def __command_exec(command: str, args: list[str]) -> None:
    # Start the project.
    project: Project = start_project()
    # Actual command executor
    async def __run_handler(error_prefix: str, handler: CommandHandler, command_args: list[str]) -> None:
        try:
            # Launch the handler.
            await handler(State(project), command_args)
            # Close the database connection explicitly (fuck MySQL).
            await stop_project(project)
        except EastwindCriticalError as e:
            # When critical error happened, show the error message.
            print(f'-{error_prefix}: {e.message}')
        except CliCommandError as e:
            # This is a shell-level based command error, use shell as error prefix.
            print(f'-shell: {error_prefix}: {e.error_info}')
        except Exception as e:
            # Other general critical error, just raise it.
            raise
        finally:
            await stop_project(project)

    # Built-in commands check (first priority).
    if command in BUILTIN_COMMANDS:
        await __run_handler(command, BUILTIN_COMMANDS[command], args)
        return

    # Module command handler check.
    from eastwind.lib.util import import_module

    def __extract_command_map(module_prefix: str) -> CommandMap | None:
        # Try to import the CLI modules.
        target = import_module(f"{module_prefix}.cli")
        if target is None:
            return None
        # Try to combine the handler.
        return target.command_handler if hasattr(target, 'command_handler') else None

    async def __parse_and_run(module_prefix: str) -> None:
        # Extract the command block.
        command_map = __extract_command_map(module_prefix)
        if command_map is None:
            print(f'-shell: "{command}" command handler not provided')
            return
        # Check out whether the token is .
        if len(args) == 0:
            # Run the help command for this map.
            command_map_names: list[str] = list(command_map.keys())
            command_map_names.sort()
            __help_show_command_list(command, command_map_names)
            return
        # Extract the sub command from the token.
        sub_command: str = args[0]
        if sub_command not in command_map:
            print(f'-shell: {command}: unknown sub command "{sub_command}"')
            return
        await __run_handler(command, command_map[sub_command], args[1:])

    if command in project["config"].module_builtin:
        await __parse_and_run(f'eastwind.modules.{command}')
        return
    if command in project["config"].module_project:
        await __parse_and_run(f'modules.{command}')
        return
    # Otherwise, unknown command.
    print(f'-shell: {command}: command not found')
    await stop_project(project)


def run_command(raw_command: str) -> None:
    # Ignore the beginning and ending whitespaces.
    raw_command = raw_command.strip()
    # Ignore the empty line and comment.
    if len(raw_command) == 0 or raw_command[0] == '#':
        return
    # Split the command into tokens.
    tokens: list[str] = shlex.split(raw_command)
    # Extract the command map name.
    asyncio.run(__command_exec(tokens[0], tokens[1:]))


def run_shell() -> None:
    # Loop forever until command is in the EXIT.
    while True:
        try:
            command: str = input('$ ')
        except (KeyboardInterrupt, UnicodeDecodeError):
            break
        command = command.strip()
        # First priority: quit command.
        if command in COMMAND_EXIT:
            break
        # Ignore the empty command.
        if len(command) == 0:
            continue
        # Run the target command in an independent process.
        asyncio.run(run_python(__file__, command))


def main() -> None:
    if len(sys.argv) != 2:
        return
    # The second argument is the command passed in, run the command.
    run_command(sys.argv[1])


if __name__ == '__main__':
    main()
