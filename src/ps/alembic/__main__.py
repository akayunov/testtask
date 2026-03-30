import os
import os.path

from alembic.config import CommandLine, Config

alembic_dir = os.path.dirname(os.path.abspath(__file__))


def get_default_alembic_config() -> str:
    return os.path.join(alembic_dir, 'alembic.ini')


def main(argv=None):
    alembic_cfg = Config(get_default_alembic_config())
    alembic_cli = CommandLine()
    options = alembic_cli.parser.parse_args(argv)
    alembic_cli.run_cmd(alembic_cfg, options)


if __name__ == "__main__":
    main()
