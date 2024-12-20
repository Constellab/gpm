

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


if __name__ == "__main__":
    install()
