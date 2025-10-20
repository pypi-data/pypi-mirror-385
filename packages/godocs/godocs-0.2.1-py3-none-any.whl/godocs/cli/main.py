from godocs.cli.command import AppCommand


def main():
    """
    Entrypoint for the `godocs` CLI application.
    """

    # Instantiates main app
    app = AppCommand()

    app.register()

    args = app.parse()

    app.start(args)


if __name__ == "__main__":
    main()
