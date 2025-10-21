# Claude Development Guidelines

## Pull Request Workflow

**IMPORTANT:** Always create a feature branch and submit a PR before merging to main.

```bash
# Create a new feature branch
git checkout -b feature/your-feature-name

# Make changes, commit, and push
git add .
git commit -m "Your commit message"
git push origin feature/your-feature-name

# Create PR
gh pr create --title "Your PR title" --body "Description of changes"

# Wait for CI checks to pass before merging
gh pr checks
```

**Never push directly to main.** All changes must go through PR review and CI checks.

## Deploying nexus-server to GCP

The nexus-server runs on a GCP Compute Engine instance at `nexus.sudorouter.ai`.

### Deployment Steps

1. **Authenticate with GCP:**
   ```bash
   gcloud auth login
   ```

2. **SSH into the server and deploy:**
   ```bash
   gcloud compute ssh nexus-server --zone=us-west1-a --command="
     cd ~/nexus && \
     git pull origin main && \
     source .venv/bin/activate && \
     pip install -e . && \
     sudo systemctl restart nexus-rpc
   "
   ```

3. **Verify the deployment:**
   ```bash
   # Check service status
   gcloud compute ssh nexus-server --zone=us-west1-a --command="sudo systemctl status nexus-rpc"

   # Test health endpoint
   curl https://nexus.sudorouter.ai/health
   ```

### Server Configuration

- **Service:** Runs as systemd service `nexus-rpc`
- **Port:** 8080 (internal)
- **Domain:** `nexus.sudorouter.ai` (via Caddy reverse proxy with HTTPS)
- **Code location:** `~/nexus`
- **CORS:** Configured to allow requests from `https://nexus-frontend-f36bf.web.app`

### Troubleshooting

```bash
# View logs
gcloud compute ssh nexus-server --zone=us-west1-a --command="sudo journalctl -u nexus-rpc -f"

# Restart service
gcloud compute ssh nexus-server --zone=us-west1-a --command="sudo systemctl restart nexus-rpc"

# Check if port is listening
gcloud compute ssh nexus-server --zone=us-west1-a --command="sudo lsof -i :8080"
```
