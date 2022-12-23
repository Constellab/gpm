# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import click
from script.gpm import GPM

@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))
@click.pass_context
@click.option('--env-mode')
def install(ctx, env_mode: str = None):
    gpm = GPM(settings_file_path=GPM.CONFIG_FILE_PATH, env_mode=env_mode)
    gpm.init_all()

    print(f"Installed pip packages:\n{GPM._installed_pip_packages}")
    print(f"Installed git packages:\n{GPM._installed_git_packages}")


if __name__ == "__main__":
    install()
