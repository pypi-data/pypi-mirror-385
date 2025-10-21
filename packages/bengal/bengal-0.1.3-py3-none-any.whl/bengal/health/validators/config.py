"""
Configuration validator wrapper.

Integrates the existing ConfigValidator into the health check system.
"""


from __future__ import annotations

from typing import TYPE_CHECKING, override

from bengal.health.base import BaseValidator
from bengal.health.report import CheckResult

if TYPE_CHECKING:
    from bengal.core.site import Site


class ConfigValidatorWrapper(BaseValidator):
    """
    Wrapper for config validation.

    Note: Config validation happens at load time, so by the time we get to
    health checks, the config has already been validated. This validator
    confirms that validation occurred and reports any config-related concerns.
    """

    name = "Configuration"
    description = "Validates site configuration"
    enabled_by_default = True

    @override
    def validate(self, site: Site) -> list[CheckResult]:
        """Validate configuration."""
        results = []

        # Config is already validated at load time, so we just do sanity checks
        config = site.config

        # Check essential fields are present
        results.extend(self._check_essential_fields(config))

        # Check for common misconfigurations
        results.extend(self._check_common_issues(config))

        return results

    def _check_essential_fields(self, config: dict) -> list[CheckResult]:
        """Check that essential config fields are present."""
        results = []

        # These fields should always be present (with defaults)
        essential_fields = ["output_dir", "theme"]

        missing = [f for f in essential_fields if f not in config]

        if missing:
            results.append(
                CheckResult.warning(
                    f"Missing configuration fields: {', '.join(missing)}",
                    recommendation="Add these fields to your bengal.toml for better control.",
                )
            )
        else:
            results.append(CheckResult.success("All essential configuration fields present"))

        return results

    def _check_common_issues(self, config: dict) -> list[CheckResult]:
        """Check for common configuration issues."""
        results = []

        # Check if baseurl has trailing slash (common mistake)
        baseurl = config.get("baseurl", "")
        if baseurl and baseurl.endswith("/"):
            results.append(
                CheckResult.info(
                    "Base URL has trailing slash",
                    recommendation="Trailing slashes in baseurl can cause double-slash issues in URLs. Consider removing it.",
                )
            )

        # Check if max_workers is very high
        max_workers = config.get("max_workers", 4)
        if max_workers > 20:
            results.append(
                CheckResult.warning(
                    f"max_workers is very high ({max_workers})",
                    recommendation="Very high worker counts may cause resource exhaustion. Consider reducing to 8-12.",
                )
            )

        # Check if incremental build is enabled without parallel
        if config.get("incremental") and not config.get("parallel", True):
            results.append(
                CheckResult.info(
                    "Incremental builds work best with parallel processing",
                    recommendation="Consider enabling parallel=true for faster incremental builds.",
                )
            )

        # All checks passed
        if not any(r.is_problem() for r in results):
            results.append(CheckResult.success("Configuration validated successfully"))

        return results
