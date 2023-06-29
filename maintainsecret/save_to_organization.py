"""
This module, `save_to_organization.py`, is part of the `maintainsecret` package.
It provides functionality to save secrets to a GitHub organization. 

This module raises a `ValueError` if there is a mismatch between the provided repository
IDs and the secret visibility setting.

Functions:
- `savesecret()`: Creates or updates an organization secret with an encrypted value.

Exceptions:
- `ValueError`: Raised when there is a mismatch between the provided repository IDs and
the secret visibility setting.
"""
import argparse
import json
import logging
from operator import xor
from typing import List

import requests

from maintainsecret.lib import (
    GITHUB_DOT_COM_API_BASE,
    encrypt_secret,
    get_organization_public_key,
)

log = logging.getLogger(__name__)


def savesecret(
    destination_github_token: str,
    secret_name: str,
    secret_value: str,
    secret_visibility: str,
    destination_organization: str,
    selected_repository_ids: List[str],
    github_api_base_url: str = GITHUB_DOT_COM_API_BASE,
) -> None:
    """Creates or updates an organization secret with an encrypted value."""

    print(f"Saving secret to organization: {destination_organization}")

    organization_public_key = get_organization_public_key(
        organization=destination_organization,
        github_token=destination_github_token,
        github_api_base_url=github_api_base_url,
    )

    secret = encrypt_secret(
        public_key=organization_public_key["key"], secret_value=secret_value
    )

    if xor(bool(selected_repository_ids), (secret_visibility == "selected")):
        raise ValueError(
            (
                "To scope the secret to a particular set of repositories, both "
                "parameters 'selected_repository_ids' and 'visibility' must be "
                "provided."
            )
        )

    response_save_secret = requests.put(
        url=(
            f"{github_api_base_url}/orgs/{destination_organization}"
            f"/actions/secrets/{secret_name}"
        ),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {destination_github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        data=json.dumps(
            {
                "encrypted_value": secret,
                "key_id": organization_public_key["key_id"],
                "visibility": secret_visibility,
                "selected_repository_ids": selected_repository_ids,
            }
        ),
        timeout=5,
    )

    try:
        log.warning(response_save_secret.json().get("message", ""))
    except requests.exceptions.JSONDecodeError:
        pass

    response_save_secret.raise_for_status()
    log.info("Successfully saved secret to organization")


def get_args():
    """
    Parses command-line arguments.

    This function uses the argparse module to parse command-line arguments.
    The arguments are expected to be passed in the following order:
    - GitHub Token
    - Secret Name
    - Secret Value
    - Secret Visibility
    - Target Organization
    - Target Repository IDs

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
        "--secret-visibility",
        dest="secret_visibility",
        choices=["all", "private", "selected"],
        required=True,
    )
    parser.add_argument("--destination-organization", dest="destination_organization")
    parser.add_argument(
        "--destination-selected-repository-ids",
        dest="selected_repository_ids",
        default="",
        required=False,
        type=lambda ids: [int(id.strip()) for id in ids.split(",") if id.strip()],
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    savesecret(
        destination_github_token=args.destination_github_token,
        secret_name=args.secret_name,
        secret_value=args.secret_value,
        secret_visibility=args.secret_visibility,
        destination_organization=args.destination_organization,
        selected_repository_ids=args.selected_repository_ids,
    )
