# CI/CD

## GitHub Actions Pipeline
The platform utilizes GitHub Actions for continuous integration and delivery.

### Workflow Stages
1. **Linting & Formatting**: Enforces code style using `ruff` and type-checking via `mypy`.
2. **Testing**: Runs the `pytest` test suite to validate application logic, including the deterministic math execution.
3. **Build & Publish**: Builds the Docker image and publishes it to the GitHub Container Registry (GHCR) using immutable tags (the Git SHA).
4. **Deploy Simulation**: Triggers `./deploy.sh aws` to simulate the production deployment flow.

### Documentation Deployment
A dedicated workflow `.github/workflows/docs.yml` automatically builds and deploys the MkDocs documentation to GitHub Pages on every push to the `main` branch.
