import click

from init.script.gencovery_package_manager import GencoveryPackageManager


@click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
@click.option("--env-mode")
def install(ctx, env_mode: str = None):
    gpm = GencoveryPackageManager(
        settings_file_path=GencoveryPackageManager.CONFIG_FILE_PATH, env_mode=env_mode
    )
    gpm.init_all()


if __name__ == "__main__":
    install()
