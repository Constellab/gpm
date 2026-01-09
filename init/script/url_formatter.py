"""URL formatting with environment variable substitution and credential protection."""

import os
import re

from .config_reader import SettingsReader


class UrlFormatter:
    """Handles URL formatting with environment variable substitution and credential redaction.

    This class is responsible for:
    - Replacing environment variable placeholders in URLs
    - Resolving variables from multiple sources (local, OS env, config)
    - Redacting credentials from URLs for safe logging
    """

    def __init__(self, config_reader: SettingsReader):
        """Initialize the URL formatter.

        Args:
            config_reader: SettingsReader instance for accessing global environment variables
        """
        self.config_reader = config_reader

    def format_url(self, string: str, variables: dict[str, str] | None = None) -> str:
        """Replace environment variable placeholders in a string with their values.

        Searches for variables in this order:
        1. Local variables parameter
        2. OS environment variables
        3. Global config environment variables

        Supports both ${VAR} and $VAR syntax for variable placeholders.

        Args:
            string: The string containing variable placeholders to replace
            variables: Local variables to use for substitution (optional)

        Returns:
            The string with all variables replaced by their values

        Raises:
            Exception: If a required environment variable is not found
        """
        if not string:
            return string

        if not variables:
            variables = {}

        global_config_vars = self.config_reader.get_environment_variables()

        # Find all variable placeholders in format $VAR or ${VAR}
        # Pattern matches: ${VAR_NAME} or $VAR_NAME where VAR_NAME is uppercase letters and underscores
        tokens = self.find_variables(string)

        for token in tokens:
            value = self.resolve_variable(token, variables, global_config_vars)
            if value:
                string = re.sub(r"\$\{?" + token + r"\}?", value, string)

        return string

    def find_variables(self, string: str) -> list[str]:
        """Find all environment variable placeholders in a string.

        Args:
            string: The string to search for variable placeholders

        Returns:
            List of variable names found in the string
        """
        return re.findall(r"\$\{?([A-Z_]+)\}?", string)

    def resolve_variable(
        self, token: str, local_vars: dict[str, str], global_vars: dict[str, str]
    ) -> str:
        """Resolve a variable token to its value.

        Searches in order: local variables, OS environment, global config variables.

        Args:
            token: Variable name to resolve
            local_vars: Local variables dictionary
            global_vars: Global configuration variables dictionary

        Returns:
            The resolved value

        Raises:
            Exception: If the variable cannot be found in any source
        """
        # Search for values in local variable first
        value = local_vars.get(token)
        if not value:
            # Search for values in os environment
            value = os.getenv(token)
            if not value:
                # Search for values in global environment (given by the main config file)
                value = global_vars.get(token)
                if not value:
                    raise Exception(f"No environment variable {token} found")

        return value

    def redact_credentials(self, url: str) -> str:
        """Redact credentials from a URL for safe logging.

        Replaces user:password@ in URLs with ***@

        Args:
            url: The URL that may contain credentials

        Returns:
            URL with credentials redacted

        Examples:
            >>> redact_credentials("https://user:pass@github.com/repo.git")
            "https://***@github.com/repo.git"
        """
        return re.sub(r"(https?://)[^@]*@", r"\1***@", url)
