# Example: Docker CI/CD with GitHub Actions

A minimal FastAPI app that is tested, built, and pushed to GitHub Container Registry (GHCR) by GitHub Actions, with an optional SSH deploy to a Linux server running Docker Compose.

This repository accompanies the Seenode guide **How to Build, Push, and Deploy Docker Images With GitHub Actions**.

## What the workflow does

On every push to `main`, pull request, or `v*` tag, the workflow:

1. Installs the Python dependencies and runs the tests.
2. Builds a `linux/amd64` Docker image.
3. Pushes the image to `ghcr.io/<owner>/<repo>` with:
   - `main` for the main branch
   - `pr-<number>` for pull requests
   - `1.2.3` and `1.2` for `v1.2.3` tags
   - `sha-<full-commit>` for every build
4. Optionally deploys the new SHA tag to a VPS over SSH.

The build and push job uses the built-in `GITHUB_TOKEN`; no personal access token is needed for GHCR.

## Run it locally

```bash
docker build --platform linux/amd64 -t example-docker-ci:local .
docker run --rm -p 8000:8000 example-docker-ci:local
```

In another terminal:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

The `linux/amd64` flag matters on Apple Silicon. Without it, Docker builds an `arm64` image that will not run on most VPS hosts or on Seenode.

## GitHub Container Registry

After the first successful workflow run, the package appears under the repository owner's **Packages** tab.

- **Private package:** the VPS or Seenode needs a GitHub PAT with `read:packages`.
- **Public package:** open the package settings and change visibility to public. No registry login is needed on the server.

## Optional: deploy to a VPS

The `deploy` job is skipped unless you enable it.

1. Create a repository variable `ENABLE_VPS_DEPLOY` with the value `true`.
2. Add these repository secrets:
   - `VPS_HOST`
   - `VPS_USER`
   - `VPS_SSH_KEY` (the private key)
   - `GHCR_READ_TOKEN` (a PAT with `read:packages`, or leave it unset to use the workflow `GITHUB_TOKEN` for this same repo's package)
3. Clone this repository on the server at `/opt/example-api`, or change the `cd` path in `.github/workflows/docker-ci.yml`. The workflow passes `IMAGE_OWNER` from the repository owner, so a fork pulls its own image; the compose file falls back to `geosegun` for a manual run. The workflow lowercases `IMAGE_OWNER` because Docker image names cannot contain uppercase letters.
4. Make sure the server user can run `docker compose` without a password prompt.

The deploy job runs:

```bash
docker compose pull
docker compose up -d --remove-orphans
```

The compose file maps host port `8080` to container port `8000` and uses the `IMAGE_TAG` passed by the workflow, so each deploy pins the exact `sha-<commit>` image. To roll back, run the same commands with an older `IMAGE_TAG`.

## Deploy the image on Seenode

You can run the same GHCR image on [Seenode](https://seenode.com) without managing a server.

1. Create a new application and choose **Docker image** as the source.
2. Enter `ghcr.io/geosegun/example-docker-ci` (or your fork's path).
3. For a private package, add a **Pull credential** using a GitHub username and a PAT with `read:packages`.
4. Choose an image tag, set the container port to `8000`, and create the app.

Seenode image-backed apps do not auto-deploy when you push a new image. After the workflow pushes a new tag, open the app, select the tag, and start a deploy. Immutable `sha-<commit>` tags make rollbacks predictable.

See the Seenode docs for [deploying from a Docker image](https://seenode.com/docs/services/docker-image) and [container registry credentials](https://seenode.com/docs/configure/container-registry-credentials).

## Tags and rollbacks

Use the `sha-<commit>` tag for production deploys. It points to exactly one image and can be traced back to a commit.

`latest` is fine for a demo, but two deploys of `latest` can point at different images. Prefer a SHA or a release tag when you need a reliable rollback.

## Project layout

```text
.
├── .github/workflows/docker-ci.yml
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
└── tests/test_main.py
```
