import click
from script.gencovery_package_manager import GencoveryPackageManager
from script.workspace_config import WorkspaceConfig


@click.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.pass_context
@click.option("--env-mode")
def install(ctx, env_mode: str):
    gpm = GencoveryPackageManager(
        settings_file_path=WorkspaceConfig.CONFIG_FILE_PATH, env_mode=env_mode
    )
    gpm.init_all()


if __name__ == "__main__":
    install()
