import argparse
import shlex
import sys
from typing import Callable, Literal, Dict

from colorama import Style, Fore

from rushlib.args import parse_args
from rushlib.func import smart_call

from rushlib.output import print_red
from rushclis.command import Command
from rushclis.help import cmd_help


class RushCli:
    @staticmethod
    def default_func(args):
        ...

    def __init__(self, name: str = "clitool", version: str = "1.0.0", description: str = None, epilog: str = None,
                 is_add_default: bool = True, show_text: bool = True):
        """
        :param name: 命令行显示的名称
        :param version: 版本号
        :param description: 介绍
        :param epilog: 例子
        """
        self.name = name
        self.version = version
        self.parser = Command(
            prog=name,
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog,
            add_help=False,
            print_error=True
        )

        self._subparsers = None
        self.subcommands: Dict[str, "RushCli"] = {}  # 存储子命令
        self.command_dest = f"command_{id(self)}"
        self.parent = None

        self.args: argparse.Namespace | list = []
        self.main_func = self.default_func
        self.extra_args = []
        self.extra_kwargs = {}

        self.cmd_commands = {}

        self.add_version = True
        self.show_text = show_text
        self.exit = False

        if is_add_default:
            self._add_default()

    def _add_default(self):
        self.parser.add_argument('--help', '-h', action='help',
                                 help='ℹ️ 显示帮助信息', default=argparse.SUPPRESS)
        if self.add_version:
            self.parser.add_argument('--version', '-v', action='version',
                                     help='ℹ️ 显示版本信息', version=f"{self.name} {self.version}")

        self.add_cmd_command("help", cmd_help)

    def set_main_func(self, func: Callable, *args, **kwargs):
        """
        设置此命令触发后的事件
        :param func: 触发函数，默认传入args参数，如果需要额外参数，则参数是必须的(或额外参数使用kwargs).
        :param args: 额外参数.
        :param kwargs: 额外参数.
        """
        self.main_func = func
        self.extra_args = args
        self.extra_kwargs = kwargs

    def set_sub_main_func(self, _id: str, func: Callable, *args, **kwargs):
        """
        设置子命令的主函数
        :param _id: 子命令名称
        :param func: 触发函数，默认传入args参数，如果需要额外参数，则参数是必须的(或额外参数使用kwargs).
        :param args: 额外参数.
        :param kwargs: 额外参数.
        """
        self.get(_id).set_main_func(func, *args, **kwargs)

    def add_argument(self, name: str, flag=None, action: Literal["append", "store_true"] = None, _help=None,
                     default=None, *_args, **_kwargs):
        """
        添加arg
        :param name: arg的名称。为直接名称或--名称(如果添加了子命令，那么不能使用直接名称)
        :param flag: arg的简称，只能在name为--名称时使用，格式为-单个字母
        :param action: arg输入的类型，默认为str，可用值有[append, store_true]
        :param _help: 提示命令
        :param default: 默认值
        :param _args: 其他参数
        :param _kwargs: 其他参数
        """
        args = []
        kwargs = {}

        args.append(name)
        if flag:
            args.append(flag)

        if default is not None:
            kwargs["default"] = default

        if action:
            kwargs["action"] = action

        if _help:
            kwargs["help"] = _help

        args = [
            *args,
            *_args
        ]

        kwargs = {
            **kwargs,
            **_kwargs
        }

        self.parser.add_argument(
            *args,
            **kwargs
        )

    def add_sub_argument(self, _id: str, name: str, flag=None, action: Literal["append", "store_true"] = None,
                         _help=None, default=None, *_args, **_kwargs):
        """
        添加子命令的arg
        :param _id: 子命令名称
        :param name: arg的名称。为直接名称或--名称(如果添加了子命令，那么不能使用直接名称)
        :param flag: arg的简称，只能在name为--名称时使用，格式为-单个字母
        :param action: arg输入的类型，默认为str，可用值有[append, store_true]
        :param _help: 提示命令
        :param default: 默认值
        :param _args: 其他参数
        :param _kwargs: 其他参数
        """
        self.get(_id).add_argument(name, flag, action, _help=_help, default=default, *_args, **_kwargs)

    def add_command(self, name: str, _help: str = None):
        """
        添加子命令
        :param name: 子命令名称
        :param _help: 提示信息
        """
        if not self._subparsers:
            self._set_subparsers()
        _command = RushCli(name)
        parser = self._subparsers.add_parser(name, help=_help)
        _command.parser = parser
        _command.parent = self
        _command.add_version = False
        self.subcommands[name] = _command

    def add_sub_command(self, _id: str, name: str, _help: str = None):
        """
        添加子命令的子命令
        :param _id: 子命令名称
        :param name: 子命令名称
        :param _help: 提示信息
        """
        self.get(_id).add_command(name, _help)

    def add_cmd_command(self, name, func):
        if name in self.cmd_commands.keys():
            raise RuntimeError(f"Command {name} already registered")

        self.cmd_commands[name] = {}

        self.cmd_commands[name]["func"] = func

    def get(self, name) -> "RushCli":
        """
        获得子命令
        :param name: 子命令名称
        :return: 子命令
        """
        return self.subcommands.get(name, None)

    def _set_subparsers(self):
        if self._subparsers is None:
            self._subparsers = self.parser.add_subparsers(
                title='📋 可用命令',
                dest=self.command_dest,  # 使用唯一的dest标识符
                help='👉 选择要执行的操作'
            )
        return self._subparsers

    def _run(self):
        args = getattr(self.parent, "args", None)
        if args:
            self.args = args[1:]

        parsed = parse_args(self.args, self.parser)

        _command = getattr(parsed, self.command_dest, None)
        if _command:
            self.subcommands[_command]._run()
        else:
            smart_call(self.main_func, parsed, *self.extra_args, **self.extra_kwargs)

    def _cmd_command(self):
        if not self.args:
            return False

        _command = self.args[0]

        match _command:
            case "exit":
                self.exit = True
                return True

        for c in self.cmd_commands.keys():
            if c == _command:
                smart_call(self.cmd_commands[c]["func"], self)
                return True

        return False

    def enter_event(self):
        pass

    def exit_event(self):
        pass

    @property
    def print_value(self):
        return ''

    def _run_cmd(self):
        self.enter_event()

        if self.show_text:
            print(f"{self.name.capitalize()} {self.version}")
            print(f'Type {", ".join([f'"{i}"' for i in self.cmd_commands.keys()])} for more information.')
            print()

        while True:
            if self.exit:
                self.exit_event()
                break

            try:
                print(f"{self.print_value}{Fore.MAGENTA}>>> {Style.RESET_ALL}", end="")
                self.args = shlex.split(input())
                print(Style.RESET_ALL, end="")
                if self._cmd_command(): continue
                self._run()
            except Exception as e:
                print_red(f"{e}")

    def run(self):
        """
        开始运行
        """
        self.args = sys.argv[1:]

        if not self.args:
            self._run_cmd()
            return
        self._run()
