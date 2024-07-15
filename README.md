# github-secret

A set of GitHub Actions for saving GitHub secret at organisation, repository and environment levels.

- [github-secret/save-to-organization](https://github.com/igwejk/github-secret/blob/main/save-to-organization/action.yml)
- [github-secret/save-to-repository](https://github.com/igwejk/github-secret/blob/main/save-to-repository/action.yml)
- [github-secret/save-to-environment](https://github.com/igwejk/github-secret/blob/main/save-to-environment/action.yml)

## Usage

Secrets can only be decrypted in the context of a workflow run in the repository where they should be accessible.

So, when you have determined the source where you want to copy secrets from, then you can use this set of GitHub Actions as in the following examples.

### Copy an `organization` secret

This example assumes multiple organization secrets should be copied to the destination, and demonstrates how to use GitHub issues as a self-service form for specifying the desired secrets to be copied.

```yaml
name: Migrate One or More Organisation Secrets

on:
  issues:
    types:
      - opened
      - edited
  # expected issue body input should be structured as follows:
  # {
  #     "01": {
  #         "secretname": "01",
  #         "visibility": "all",
  #         "destination": "targetorganization-a",
  #         "destinationPersonalAccessTokenName":"the_pat_a",
  #         "selected-repository-ids": []
  #     },
  #     "02": {
  #         "secretname": "02",
  #         "visibility": "selected",
  #         "destination": "targetorganization-b",
  #         "destinationPersonalAccessTokenName":"the_pat_b" ,
  #         "selected-repository-ids": [ "repo-id-1", "repo-id-2", ...]
  #     },
  #     ...
  # }

jobs:
  migrate-org-secret:
    if: contains(github.event.issue.labels.*.name, 'migrate-org-secret')
    runs-on: ubuntu-latest
    permissions:
      issues: write
    strategy:
      matrix:
        secretname: ${{ fromJSON(github.event.issue.body).*.secretname }} # e.g. [ "01", "02", ...]
      max-parallel: 1
    steps:
      - name: Acknowledgement
        uses: actions/github-script@v6
        with:
          script: |

            const response = github.request (
              'POST /repos/{owner}/{repo}/issues/{issue_number}/comments',
              {
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: '${{ github.event.issue.number }}',
                body: 'Migrating secret: `${{ matrix.secretname }}`...',
                headers: {
                  'X-GitHub-Api-Version': '2022-11-28'
                }
              }
            );
      - name: Save organisation secret
        uses: gh-gei-bells/github-secret/save-to-organization@main
        with:
          secret-name: ${{ matrix.secretname }} # e.g. "01"
          secret-value: ${{ secrets[matrix.secretname] }}
          secret-visibility: ${{ fromJSON(github.event.issue.body)[matrix.secretname].visibility }} # e.g. "all"
          destination-organization: ${{ fromJSON(github.event.issue.body)[matrix.secretname].destination }} # e.g. "targetorganization-a"
          destination-github-token: ${{ secrets[fromJSON(github.event.issue.body)[matrix.secretname].destinationPersonalAccessTokenName] }} # e.g. secret["the_pat_a"]
          destination-selected-repository-ids: ${{ join(fromJSON(github.event.issue.body)[matrix.secretname].selected-repository-ids) }} # e.g. "repo-id-1,repo-id-2",...
```

### Copy a `repository` secret

```yaml
name: Migrate One or More Repository Secrets

on:
  workflow_call:
    inputs:
      json-migration-spec:
        type: string
        required: true
        description: >-
          A JSON structured specification of repositories to be migrated.
  workflow_dispatch:
    inputs:
      json-migration-spec:
        type: string
        required: true
        description: >-
          A JSON structured specification of repositories to be migrated.
          # expected json-migration-spec input should be structured as follows:
          # {
          #     "REPOSITORY_SECRET_01": {
          #         "secretname": "REPOSITORY_SECRET_01",
          #         "destinationRepositoryName": "repo-with-access-to-secret-01",
          #         "destinationRepositoryOwner": "migration-dst",
          #         "destinationPersonalAccessTokenName": "DST_ORG_SECRET_MGT"
          #     },
          #     "REPOSITORY_SECRET_02": {
          #         "secretname": "REPOSITORY_SECRET_02",
          #         "destinationRepositoryName": "repo-with-access-to-secret-02",
          #         "destinationRepositoryOwner": "migration-dst",
          #         "destinationPersonalAccessTokenName": "DST_ORG_SECRET_MGT"
          #     },
          #     "REPOSITORY_SECRET_03": {
          #         "secretname": "REPOSITORY_SECRET_03",
          #         "destinationRepositoryName": "repo-with-access-to-secret-03",
          #         "destinationRepositoryOwner": "migration-dst",
          #         "destinationPersonalAccessTokenName": "DST_ORG_SECRET_MGT"
          #     }
          # }

jobs:
  migrate-repository-secret:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        secretname: ${{ fromJSON(inputs.json-migration-spec).*.secretname }} # e.g. [ "p", "q", ...]
      max-parallel: 1
    steps:
      - name: Save repository secret
        uses: igwejk/github-secret/save-to-repository@main
        with:
          secret-name: ${{ matrix.secretname }} # e.g. "p"
          secret-value: ${{ secrets[matrix.secretname] }}
          destination-repository-name: ${{ fromJSON(inputs.json-migration-spec)[matrix.secretname].destinationRepositoryName }} # e.g. "repo-01"
          destination-repository-owner: ${{ fromJSON(inputs.json-migration-spec)[matrix.secretname].destinationRepositoryOwner }} # e.g. "targetorganization-a"
          destination-github-token: ${{ secrets[fromJSON(inputs.json-migration-spec)[matrix.secretname].destinationPersonalAccessTokenName] }} # e.g. secret["the_pat_a"]
```

### Copy an `environment` secret

```yaml
name: Migrate One or More Environment Secrets

on:
  workflow_call:
  workflow_dispatch:
    inputs:
      json-migration-spec:
        type: string
        required: true
        description: >-
          A JSON structure specification of repositories to be migrated.
          # expected json-migration-spec input should be structured as follows:
          # {
          #     "ENVIRONMENT_SECRET_01": {
          #         "secretname": "ENVIRONMENT_SECRET_01",
          #         "destinationEnvironmentName": "production",
          #         "destinationRepositoryId": "706095692",
          #         "destinationPersonalAccessTokenName": "DST_ORG_SECRET_MGT"
          #     },
          #     "ENVIRONMENT_SECRET_02": {
          #         "secretname": "ENVIRONMENT_SECRET_02",
          #         "destinationEnvironmentName": "production",
          #         "destinationRepositoryId": "706096064",
          #         "destinationPersonalAccessTokenName": "DST_ORG_SECRET_MGT"
          #     },
          #     "ENVIRONMENT_SECRET_03": {
          #         "secretname": "ENVIRONMENT_SECRET_03",
          #         "destinationEnvironmentName": "staging",
          #         "destinationRepositoryId": "706096293",
          #         "destinationPersonalAccessTokenName": "DST_ORG_SECRET_MGT"
          #     }
          # }

jobs:
  migrate-environment-secret:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        secretname: ${{ fromJSON(inputs.json-migration-spec).*.secretname }} # e.g. [ "x", "y", ...]
      max-parallel: 1
    steps:
      - name: Save environment secret
        uses: gh-gei-bells/github-secret/save-to-environment@main
        with:
          secret-name: ${{ matrix.secretname }} # e.g. "x"
          secret-value: ${{ secrets[matrix.secretname] }}
          destination-environment: ${{ fromJSON(inputs.json-migration-spec)[matrix.secretname].destinationEnvironmentName }} # e.g. "env-01"
          destination-repository-id: ${{ fromJSON(inputs.json-migration-spec)[matrix.secretname].destinationRepositoryId }} # e.g. "targetRepoIdA"
          destination-github-token: ${{ secrets[fromJSON(inputs.json-migration-spec)[matrix.secretname].destinationPersonalAccessTokenName] }} # e.g. secret["the_pat_a"]
```
