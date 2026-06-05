# Security Notes

- Configuration is environment-driven and `.env` is intentionally not committed.
- Kubernetes Secrets are represented as placeholders and should be replaced by a cloud secret manager or sealed secret workflow.
- The container runs as an unprivileged user.
- Kubernetes manifests drop capabilities and disable privilege escalation.
- FastAPI/Pydantic validation rejects malformed requests before scoring.
- Dependency scanning is included through `pip-audit` in `requirements.txt`; run `python -m pip_audit`.
- Production deployments should add TLS, authentication, rate limiting, network policies, and private image registry scanning.
