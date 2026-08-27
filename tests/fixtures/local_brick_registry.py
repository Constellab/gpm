"""Local git-backed stand-ins for community bricks.

The community API (``COMMUNITY_API_URL``) is the only thing that stops the GPM
tests from running offline: it is what turns a brick name + version into a
clonable repository URL. This module replaces it with a registry of ordinary
git repositories created in a temp folder and served over ``file://`` URLs.

Everything downstream of the lookup stays real — the bricks are really cloned
by ``GitPackageInstaller``, tags are really resolved, ``.git`` is really
removed — so the tests keep exercising the production install path without a
network call or a secret.
"""

import json
import os

from git import Actor, Repo

from init.script.community_service import CommunityBrick

# Explicit identity so commits work on machines with no global git config (CI).
_COMMIT_ACTOR = Actor("gpm-tests", "tests@gencovery.com")


class LocalBrickRegistry:
    """A folder of git repositories standing in for community-hosted bricks."""

    def __init__(self, root: str) -> None:
        self.root = root
        os.makedirs(self.root, exist_ok=True)
        # (brick_name, version) -> clone url
        self._bricks: dict[tuple[str, str], str] = {}

    @property
    def source_url(self) -> str:
        """Base URL usable as a ``source`` in a settings.json git channel."""
        return f"file://{self.root}"

    def url_for(self, name: str) -> str:
        """Clone URL of a repository in this registry."""
        return f"file://{os.path.join(self.root, name + '.git')}"

    @property
    def community_service(self) -> "FakeCommunityService":
        """A CommunityService stand-in resolving against this registry."""
        return FakeCommunityService(self)

    def add_repo(self, name: str, files: dict[str, str], version: str | None = None) -> str:
        """Create a git repo named ``<name>.git`` containing ``files``.

        Args:
            name: Repository name, without the ``.git`` suffix
            files: Relative path -> file content
            version: Tag to create on the single commit, or None for none

        Returns:
            The ``file://`` clone URL of the new repository
        """
        repo_dir = os.path.join(self.root, f"{name}.git")
        os.makedirs(repo_dir)
        repo = Repo.init(repo_dir)

        for rel_path, content in files.items():
            abs_path = os.path.join(repo_dir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as file:
                file.write(content)

        repo.index.add(list(files))
        repo.index.commit("initial commit", author=_COMMIT_ACTOR, committer=_COMMIT_ACTOR)
        if version:
            repo.create_tag(version)
        repo.close()

        return self.url_for(name)

    def add_brick(
        self,
        name: str,
        version: str,
        brick_deps: list[dict] | None = None,
        git_channels: list[dict] | None = None,
        pip_channels: list[dict] | None = None,
    ) -> str:
        """Create a brick repo (settings.json + src folder) and register it.

        The brick is tagged with ``version``, which is what the installer clones,
        and is resolvable through ``community_service`` under (name, version).
        """
        settings = {
            "name": name,
            "version": version,
            "variables": {},
            "environment": {
                "bricks": brick_deps or [],
                "git": git_channels or [],
                "pip": pip_channels or [],
                "variables": {},
            },
        }
        url = self.add_repo(
            name,
            files={
                "settings.json": json.dumps(settings, indent=2),
                "src/__init__.py": "",
                "README.md": f"# {name}\n",
            },
            version=version,
        )
        self._bricks[(name, version)] = url
        return url

    def resolve(self, name: str, version: str) -> str:
        """Clone URL of a registered brick, or raise like the community API does."""
        if (name, version) not in self._bricks:
            raise Exception(f"Brick '{name}' version '{version}' not found in local registry")
        return self._bricks[(name, version)]


class FakeCommunityService:
    """Drop-in replacement for ``CommunityService`` backed by a local registry.

    Mirrors the real contract: returns a CommunityBrick, raises on an unknown
    brick. No API key is involved because every repo is local and public.
    """

    def __init__(self, registry: LocalBrickRegistry) -> None:
        self.registry = registry

    def get_brick(self, brick_name: str, version: str) -> CommunityBrick:
        url = self.registry.resolve(brick_name, version)
        return CommunityBrick(
            brickName=brick_name,
            brickVersion=version,
            repoType="git",
            repositoryUrl=url,
            repositoryAccessUrl=url,
        )
