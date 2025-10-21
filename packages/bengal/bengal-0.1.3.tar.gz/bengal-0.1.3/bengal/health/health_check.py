"""
Main health check orchestrator.

Coordinates all validators and produces unified health reports.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from bengal.health.base import BaseValidator
from bengal.health.report import HealthReport, ValidatorReport

if TYPE_CHECKING:
    from bengal.core.site import Site
    from bengal.utils.profile import BuildProfile


class HealthCheck:
    """
    Orchestrates health check validators and produces unified health reports.

    By default, registers all standard validators. You can disable auto-registration
    by passing auto_register=False, then manually register validators.

    Usage:
        # Default: auto-registers all validators
        health = HealthCheck(site)
        report = health.run()
        print(report.format_console())

        # Manual registration:
        health = HealthCheck(site, auto_register=False)
        health.register(ConfigValidator())
        health.register(OutputValidator())
        report = health.run()
    """

    def __init__(self, site: Site, auto_register: bool = True):
        """
        Initialize health check system.

        Args:
            site: The Site object to validate
            auto_register: Whether to automatically register all default validators
        """
        self.site = site
        self.validators: list[BaseValidator] = []

        if auto_register:
            self._register_default_validators()

    def _register_default_validators(self) -> None:
        """Register all default validators."""
        from bengal.health.validators import (
            AssetValidator,
            CacheValidator,
            ConfigValidatorWrapper,
            ConnectivityValidator,
            DirectiveValidator,
            FontValidator,
            LinkValidatorWrapper,
            MenuValidator,
            NavigationValidator,
            OutputValidator,
            PerformanceValidator,
            RenderingValidator,
            RSSValidator,
            SitemapValidator,
            TaxonomyValidator,
        )

        # Register in logical order (fast validators first)
        # Phase 1: Basic validation
        self.register(ConfigValidatorWrapper())
        self.register(OutputValidator())

        # Phase 2: Content validation
        self.register(RenderingValidator())
        self.register(DirectiveValidator())
        self.register(NavigationValidator())
        self.register(MenuValidator())
        self.register(TaxonomyValidator())
        self.register(LinkValidatorWrapper())

        # Phase 3: Advanced validation
        self.register(CacheValidator())
        self.register(PerformanceValidator())

        # Phase 4: Production-ready validation
        self.register(RSSValidator())
        self.register(SitemapValidator())
        self.register(FontValidator())
        self.register(AssetValidator())

        # Phase 5: Knowledge graph validation
        self.register(ConnectivityValidator())

    def register(self, validator: BaseValidator) -> None:
        """
        Register a validator to be run.

        Args:
            validator: Validator instance to register
        """
        self.validators.append(validator)

    def run(
        self, build_stats: dict | None = None, verbose: bool = False, profile: BuildProfile = None
    ) -> HealthReport:
        """
        Run all registered validators and produce a health report.

        Args:
            build_stats: Optional build statistics to include in report
            verbose: Whether to show verbose output during validation
            profile: Build profile to use for filtering validators

        Returns:
            HealthReport with results from all validators
        """
        from bengal.utils.profile import is_validator_enabled

        report = HealthReport(build_stats=build_stats)

        for validator in self.validators:
            # Check if validator is enabled by profile
            if profile and not is_validator_enabled(validator.name):
                if verbose:
                    print(f"  Skipping {validator.name} (disabled by profile)")
                continue

            # Check if validator is enabled by config
            if not validator.is_enabled(self.site.config):
                if verbose:
                    print(f"  Skipping {validator.name} (disabled in config)")
                continue

            # Run validator and time it
            start_time = time.time()

            try:
                results = validator.validate(self.site)

                # Set validator name on all results
                for result in results:
                    if not result.validator:
                        result.validator = validator.name

            except Exception as e:
                # If validator crashes, record as error
                from bengal.health.report import CheckResult

                results = [
                    CheckResult.error(
                        f"Validator crashed: {e}",
                        recommendation="This is a bug in the health check system. Please report it.",
                        validator=validator.name,
                    )
                ]

            duration_ms = (time.time() - start_time) * 1000

            # Add to report
            validator_report = ValidatorReport(
                validator_name=validator.name, results=results, duration_ms=duration_ms
            )
            report.validator_reports.append(validator_report)

            if verbose:
                status = "✅" if not validator_report.has_problems else "⚠️"
                print(f"  {status} {validator.name}: {len(results)} checks in {duration_ms:.1f}ms")

        return report

    def run_and_print(self, build_stats: dict | None = None, verbose: bool = False) -> HealthReport:
        """
        Run health checks and print console output.

        Args:
            build_stats: Optional build statistics
            verbose: Whether to show all checks (not just problems)

        Returns:
            HealthReport
        """
        report = self.run(build_stats=build_stats, verbose=verbose)
        print(report.format_console(verbose=verbose))
        return report

    def __repr__(self) -> str:
        return f"<HealthCheck: {len(self.validators)} validators>"
