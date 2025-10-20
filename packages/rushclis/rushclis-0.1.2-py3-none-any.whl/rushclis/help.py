def cmd_help(app):
    print("📋 可用控制台命令")
    print("   ", end="")
    print("{" + f"{",".join(app.cmd_commands.keys())}" + "}")
    print(f"{" " * 24}👉 选择要执行的操作")
    for k in app.cmd_commands.keys():
        print("     ", end="")
        print(k)

    print()

    app.parser.print_help()

    print()
