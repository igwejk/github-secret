"""
This module contains utility functions for interacting with the GitHub API.

It includes functions to:
- Fetch the public key of an organization (`get_organization_public_key`)
- Fetch the public key of a repository (`get_repository_public_key`)
"""

import logging
from base64 import b64encode
from typing import TypedDict

import requests
from nacl import encoding, public

log = logging.getLogger(__name__)
GitHubPublicKey = TypedDict("GitHubPublicKey", {"key": str, "key_id": str})
GITHUB_DOT_COM_API_BASE = "https://api.github.com"


def get_organization_public_key(
    organization: str,
    github_token: str,
    github_api_base_url: str,
) -> GitHubPublicKey:
    """Get the public key of an organization."""

    endpoint = (
        f"{github_api_base_url}/orgs/" f"{organization}/actions/secrets/public-key"
    )
    log.info("Fetching organization public key: %s", endpoint)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response_for_get_organization_public_key = requests.get(
        url=endpoint,
        headers=headers,
        timeout=5,
    )

    response_for_get_organization_public_key.raise_for_status()
    log.info("Successfully fetched organization public key")

    return response_for_get_organization_public_key.json()


def get_repository_public_key(
    repository_owner: str,
    repository: str,
    github_token: str,
    github_api_base_url: str,
) -> GitHubPublicKey:
    """Get the public key of a repository."""

    endpoint = f"{github_api_base_url}/repos/{repository_owner}/{repository}/actions/secrets/public-key"
    log.info("Fetching repository public key: %s", endpoint)

    response_for_get_repository_public_key = requests.get(
        url=endpoint,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=5,
    )

    response_for_get_repository_public_key.raise_for_status()
    log.info("Successfully fetched repository public key")

    return response_for_get_repository_public_key.json()


def get_environment_public_key(
    repository_id: str,
    environment: str,
    github_token: str,
    github_api_base_url: str,
) -> GitHubPublicKey:
    """Get the public key of an environment."""

    endpoint = (
        f"{github_api_base_url}/repositories/{repository_id}"
        f"/environments/{environment}/secrets/public-key"
    )
    log.info("Fetching environment public key: %s", endpoint)

    response_for_get_environment_public_key = requests.get(
        url=endpoint,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=5,
    )

    response_for_get_environment_public_key.raise_for_status()
    log.info("Successfully fetched environment public key")

    return response_for_get_environment_public_key.json()


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""

    sealed_box = public.SealedBox(
        public.PublicKey(
            public_key.encode("utf-8"), encoding.Base64Encoder()  # type: ignore
        )
    )

    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))

    log.info("Secret encryption completed successfully")

    return b64encode(encrypted).decode("utf-8")
