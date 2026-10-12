"""Deployment, Containerization, and Environment Configuration Tests for ShopQ.

Validates:
1. Production Dockerfile specifications (multi-stage, non-root user, uvicorn server, healthcheck).
2. Render blueprint configuration (render.yaml).
3. Vercel frontend configuration (frontend/vercel.json).
4. Environment variable templates (.env.example for root, backend, frontend).
5. CORS and environment configuration separation logic in app.core.config.
"""

import json
import os
from pathlib import Path
import unittest


class TestShopQDevOpsConfiguration(unittest.TestCase):
    """Test suite for ShopQ cloud, container, and environment configurations."""

    @classmethod
    def setUpClass(cls):
        cls.backend_dir = Path(__file__).resolve().parent.parent
        cls.repo_root = cls.backend_dir.parent
        cls.frontend_dir = cls.repo_root / "frontend"

    def test_dockerfile_specifications(self):
        """Verifies multi-stage Dockerfile meets production and security standards."""
        dockerfile_path = self.backend_dir / "Dockerfile"
        self.assertTrue(dockerfile_path.exists(), "backend/Dockerfile must exist")

        content = dockerfile_path.read_text()

        # 1. Base image must be python:3.11-slim
        self.assertIn("FROM python:3.11-slim AS builder", content)
        self.assertIn("FROM python:3.11-slim AS runner", content)

        # 2. Multi-stage build requirement
        self.assertIn("COPY --from=builder", content)

        # 3. Non-root user requirement
        self.assertIn("useradd", content)
        self.assertIn("shopq", content)
        self.assertIn("USER shopq", content)

        # 4. Uvicorn server execution
        self.assertIn("uvicorn app.main:app", content)

        # 5. Healthcheck instruction
        self.assertIn("HEALTHCHECK", content)
        self.assertIn("/health", content)

    def test_backend_dockerignore_exists(self):
        """Verifies .dockerignore exists to prevent leaking cache/secrets into image."""
        dockerignore = self.backend_dir / ".dockerignore"
        self.assertTrue(dockerignore.exists())
        content = dockerignore.read_text()
        self.assertIn("__pycache__", content)
        self.assertIn(".env", content)

    def test_render_blueprint_config(self):
        """Verifies render.yaml blueprint exists and defines required production parameters."""
        render_paths = [
            self.repo_root / "render.yaml",
            self.backend_dir / "render.yaml",
        ]
        for p in render_paths:
            self.assertTrue(p.exists(), f"{p} must exist")
            content = p.read_text()
            self.assertIn("services:", content)
            self.assertIn("type: web", content)
            self.assertIn("name: shopq-backend", content)
            self.assertIn("env: docker", content)
            self.assertIn("healthCheckPath: /health", content)
            self.assertIn("ENVIRONMENT", content)
            self.assertIn("ALLOWED_ORIGINS", content)

    def test_vercel_frontend_config(self):
        """Verifies frontend/vercel.json is valid JSON and configures SPA rewrites & security headers."""
        vercel_json_path = self.frontend_dir / "vercel.json"
        self.assertTrue(vercel_json_path.exists(), "frontend/vercel.json must exist")

        with open(vercel_json_path, "r") as f:
            data = json.load(f)

        self.assertEqual(data.get("framework"), "vite")
        self.assertEqual(data.get("outputDirectory"), "dist")

        # Must have SPA rewrites for React Router (e.g. /search, /analyze/:id)
        rewrites = data.get("rewrites", [])
        self.assertTrue(len(rewrites) > 0, "Vercel config must include rewrites for SPA routing")
        has_spa_rewrite = any(r.get("destination") == "/index.html" for r in rewrites)
        self.assertTrue(has_spa_rewrite, "SPA rewrites must direct unmatched routes to /index.html")

        # Security headers
        headers = data.get("headers", [])
        self.assertTrue(len(headers) > 0, "Vercel config must include security headers")

    def test_env_example_templates(self):
        """Verifies all required environment templates exist with necessary keys."""
        root_env = self.repo_root / ".env.example"
        backend_env = self.backend_dir / ".env.example"
        frontend_env = self.frontend_dir / ".env.example"

        self.assertTrue(root_env.exists(), "Root .env.example must exist")
        self.assertTrue(backend_env.exists(), "backend/.env.example must exist")
        self.assertTrue(frontend_env.exists(), "frontend/.env.example must exist")

        b_content = backend_env.read_text()
        self.assertIn("ENVIRONMENT=", b_content)
        self.assertIn("ALLOWED_ORIGINS=", b_content)
        self.assertIn("SECRET_KEY=", b_content)
        self.assertIn("GEMINI_API_KEY=", b_content)
        self.assertIn("RATE_LIMIT_ANALYZE_RPM=", b_content)

        f_content = frontend_env.read_text()
        self.assertIn("VITE_API_BASE_URL=", f_content)

    def test_cors_and_environment_separation(self):
        """Verifies app.core.config separates local vs production CORS correctly."""
        from app.core.config import SecuritySettings

        # Test local development defaults
        os.environ["ENVIRONMENT"] = "development"
        os.environ.pop("ALLOWED_ORIGINS", None)
        dev_settings = SecuritySettings()
        self.assertFalse(dev_settings.IS_PRODUCTION)
        self.assertTrue(dev_settings.DEBUG)
        self.assertIn("http://localhost:5173", dev_settings.ALLOWED_ORIGINS)

        # Test production explicit origins
        os.environ["ENVIRONMENT"] = "production"
        os.environ["ALLOWED_ORIGINS"] = "https://shopq.vercel.app/, https://shopq-preview.vercel.app"
        prod_settings = SecuritySettings()
        self.assertTrue(prod_settings.IS_PRODUCTION)
        # Should strip whitespace and trailing slashes
        self.assertIn("https://shopq.vercel.app", prod_settings.ALLOWED_ORIGINS)
        self.assertIn("https://shopq-preview.vercel.app", prod_settings.ALLOWED_ORIGINS)
        self.assertNotIn("https://shopq.vercel.app/", prod_settings.ALLOWED_ORIGINS)

        # Clean up test env
        os.environ["ENVIRONMENT"] = "development"
        os.environ.pop("ALLOWED_ORIGINS", None)


if __name__ == "__main__":
    unittest.main()
