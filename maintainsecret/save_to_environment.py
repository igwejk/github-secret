import argparse
import json
import logging

import requests

from maintainsecret.lib import (
    GITHUB_DOT_COM_API_BASE,
    encrypt_secret,
    get_environment_public_key,
)

log = logging.getLogger(__name__)


def savesecret(
    destination_github_token: str,
    destination_environment: str,
    secret_value: str,
    secret_name: str,
    destination_repository_id: str,
    github_api_base_url: str = GITHUB_DOT_COM_API_BASE,
) -> None:
    """Creates or updates an environment secret with an encrypted value."""

    print(
        f"Saving secret to repository_id/environment_name: {destination_repository_id}/{destination_environment}"
    )

    environment_public_key = get_environment_public_key(
        repository_id=destination_repository_id,
        environment=destination_environment,
        github_token=destination_github_token,
        github_api_base_url=github_api_base_url,
    )

    secret = encrypt_secret(
        public_key=environment_public_key["key"], secret_value=secret_value
    )

    response_save_secret = requests.put(
        url=f"{github_api_base_url}/repositories/{destination_repository_id}/environments/{destination_environment}/secrets/{secret_name}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {destination_github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        data=json.dumps(
            {
                "encrypted_value": secret,
                "key_id": environment_public_key["key_id"],
            }
        ),
        timeout=5,
    )

    try:
        log.warning(response_save_secret.json().get("message", ""))
    except requests.exceptions.JSONDecodeError:
        pass

    response_save_secret.raise_for_status()
    log.info("Successfully saved secret to environment")


def get_args():
    """
    Parses command-line arguments.

    The following arguments are expected to be passed:
    - GitHub Token
    - Secret Name
    - Secret Value
    - Destination repository id
    - Destination environment name

    Returns:
        An argparse.Namespace object containing the arguments.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--destination-github-token", dest="destination_github_token", required=True
    )
    parser.add_argument("--secret-name", dest="secret_name", required=True)
    parser.add_argument("--secret-value", dest="secret_value", required=True)
    parser.add_argument(
        "--destination-repository-id",
        dest="destination_repository_id",
        required=True,
    )
    parser.add_argument(
        "--destination-environment",
        dest="destination_environment",
        required=True,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    savesecret(
        destination_github_token=args.destination_github_token,
        secret_name=args.secret_name,
        secret_value=args.secret_value,
        destination_environment=args.destination_environment,
        destination_repository_id=args.destination_repository_id,
    )
