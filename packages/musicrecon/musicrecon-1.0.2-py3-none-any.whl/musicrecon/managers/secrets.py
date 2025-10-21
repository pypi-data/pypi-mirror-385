from pathlib import Path
import os
import sys
import getpass
from typing import Dict
from ..utils.exceptions import SecretsError, SystemError


class SecretManager:
    """
    A class to securely manage application secrets, such as API keys or credentials.

    This class handles loading secrets from a local .env file or system environment variables,
    prompting the user for missing secrets, and ensuring secure storage. It follows best practices
    for security, including using secure input methods and proper error handling.

    Attributes:
        env (Path): The directory path for storing the .env file (e.g., ~/.musicrecon/).
        secrets (Dict[str, str]): A dictionary to hold loaded secrets in memory.
    """

    def __init__(self):
        """
        Initialize the SecretManager.

        Sets the environment directory to ~/.musicrecon/ and ensures it exists.
        Initializes an empty secrets dictionary.
        """
        self.env: Path = Path.home() / ".musicrecon"
        self.ensure_dir(self.env)
        self.secrets: Dict[str, str] = {}

    def load_secrets(self) -> Dict[str, str]:
        """
        Load secrets from the .env file if it exists, otherwise from system environment variables.

        If no secrets are found, prompt the user to input them securely. Secrets are stored
        in memory as a dictionary and returned as a list of values.

        Returns:
            List[str]: A list of secret values loaded or prompted.

        Raises:
            RuntimeError: If prompting fails or secrets cannot be loaded.
        """
        env_file = self.env / ".env"

        # Try loading from .env file
        if env_file.exists():
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            self.secrets[key.strip()] = value.strip()
            except Exception as e:
                raise RuntimeError(f"Failed to load secrets from {env_file}: {e}")

        # If no secrets loaded, check system environment variables
        if not self.secrets:
            for key in os.environ:
                if key.lower() in [
                    "access_key",
                    "access_secret",
                ]:
                    self.secrets[key] = os.environ[key]

        # If still no secrets, prompt the user
        if not self.secrets:
            self.secrets = self.prompt_secrets()

        return self.secrets

    def prompt_secrets(self) -> Dict[str, str]:
        """
        Prompt the user to input secrets securely and store them in environment variables and .env file.

        Uses getpass for secure input to avoid echoing sensitive data. Secrets are added to
        os.environ and written to the .env file in the self.env directory.

        Returns:
            Dict[str, str]: A dictionary of the prompted secrets.

        Raises:
            RuntimeError: If writing to .env fails.
        """
        secrets = {}
        env_file = self.env / ".env"

        print("No secrets found. Please provide the required secrets:")
        secret_keys = ["access_key", "access_secret"]

        try:
            for key in secret_keys:
                value = getpass.getpass(f"Enter value for {key}: ")
                secrets[key] = value
                os.environ[key] = value  # Add to system env
        except KeyboardInterrupt:
            sys.exit("\nInterrupt")
        except Exception as e:
            raise SecretsError(f"Could not obtain secrets: {e}")

        # Write to .env file
        try:
            with open(env_file, "w") as f:
                for key, value in secrets.items():
                    f.write(f"{key}={value}\n")
        except Exception as e:
            raise SystemError(f"Failed to write secrets to {env_file}: {e}")

        return secrets

    def ensure_dir(self, path: Path) -> bool:
        """
        Ensure that the specified directory exists, creating it if necessary.

        Args:
            path (Path): The directory path to check/create.

        Returns:
            bool: True if the directory exists or was successfully created, False otherwise.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
