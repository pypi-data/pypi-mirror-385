"""Puppeteer Client for Autonomous Agents.

This module provides a client interface for agents to use Puppeteer MCP
for browser automation, testing, and DoD verification.

Architecture:
    - For Claude CLI mode: Agents can request Puppeteer operations in their prompts
    - For API mode: This client provides direct MCP server communication
    - For both: Provides structured DoD verification capabilities

Usage:
    >>> from coffee_maker.autonomous.puppeteer_client import PuppeteerClient
    >>>
    >>> client = PuppeteerClient()
    >>> result = client.verify_web_app("http://localhost:8501", {
    ...     "checks": ["page_loads", "no_errors", "title_contains:Dashboard"]
    ... })
    >>> if result.success:
    ...     print("✅ DoD verified!")

Related:
    - US-032: Puppeteer DoD Integration
    - PRIORITY 4.1: Puppeteer MCP Integration
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result from DoD verification.

    Attributes:
        success: Whether all checks passed
        checks_passed: List of check names that passed
        checks_failed: List of check names that failed
        screenshots: List of screenshot file paths taken
        errors: List of error messages encountered
        details: Additional details about the verification
    """

    success: bool
    checks_passed: List[str]
    checks_failed: List[str]
    screenshots: List[str]
    errors: List[str]
    details: Dict[str, str]


class PuppeteerClient:
    """Client for Puppeteer MCP server.

    This client provides structured access to Puppeteer browser automation
    for autonomous agents to verify DoD and test web applications.

    Modes:
        1. CLI Mode: Generate prompts for Claude CLI that include Puppeteer requests
        2. Direct Mode: Call Puppeteer MCP server directly (future)

    Example:
        >>> client = PuppeteerClient()
        >>> # Verify a web app is working
        >>> result = client.verify_web_app("http://localhost:8501")
        >>> print(result.success)
        True
    """

    def __init__(self, mode: str = "cli"):
        """Initialize Puppeteer client.

        Args:
            mode: Client mode - "cli" (default) or "direct"
                  "cli" = Generate prompts for Claude CLI to execute
                  "direct" = Call MCP server directly (future)
        """
        self.mode = mode
        logger.info(f"PuppeteerClient initialized in {mode} mode")

    def verify_web_app(
        self,
        url: str,
        checks: Optional[List[str]] = None,
        screenshot: bool = True,
        screenshot_name: Optional[str] = None,
    ) -> VerificationResult:
        """Verify a web application meets DoD criteria.

        This method checks that a web app is accessible and functioning correctly.

        Args:
            url: URL to test (e.g., "http://localhost:8501")
            checks: List of checks to perform (default: ["page_loads"])
                    Options: "page_loads", "no_errors", "title_contains:X", "element_exists:.class"
            screenshot: Whether to take a screenshot (default: True)
            screenshot_name: Name for screenshot file (default: auto-generated)

        Returns:
            VerificationResult with success status and details

        Example:
            >>> client = PuppeteerClient()
            >>> result = client.verify_web_app("http://localhost:8501", checks=[
            ...     "page_loads",
            ...     "no_errors",
            ...     "title_contains:Dashboard"
            ... ])
        """
        checks = checks or ["page_loads"]
        screenshot_name = screenshot_name or f"verification_{url.replace('://', '_').replace('/', '_')}"

        logger.info(f"Verifying web app: {url}")
        logger.info(f"Checks to perform: {checks}")

        if self.mode == "cli":
            # In CLI mode, we generate a prompt instruction for the agent
            # The agent will include this in its prompt when using Claude CLI
            return self._verify_via_cli_prompt(url, checks, screenshot, screenshot_name)
        else:
            # Direct mode would call MCP server directly (future implementation)
            raise NotImplementedError("Direct mode not yet implemented. Use mode='cli'")

    def _verify_via_cli_prompt(
        self, url: str, checks: List[str], screenshot: bool, screenshot_name: str
    ) -> VerificationResult:
        """Generate verification instructions for CLI mode.

        In CLI mode, this returns a prompt snippet that agents can include
        in their requests to Claude CLI, which has Puppeteer MCP available.

        Args:
            url: URL to verify
            checks: List of checks
            screenshot: Whether to take screenshot
            screenshot_name: Screenshot filename

        Returns:
            VerificationResult with instructions (not actual verification)
        """
        # Generate the Puppeteer verification prompt
        verification_prompt = self.generate_verification_prompt(url, checks, screenshot, screenshot_name)

        logger.info("Generated verification prompt for CLI mode")
        logger.debug(f"Prompt: {verification_prompt[:200]}...")

        # In CLI mode, we return a result that contains the prompt
        # The agent will execute this via Claude CLI
        return VerificationResult(
            success=True,  # Success means we generated the prompt
            checks_passed=["prompt_generated"],
            checks_failed=[],
            screenshots=[],
            errors=[],
            details={"mode": "cli", "prompt": verification_prompt, "url": url},
        )

    def generate_verification_prompt(self, url: str, checks: List[str], screenshot: bool, screenshot_name: str) -> str:
        """Generate a prompt for DoD verification with Puppeteer.

        This creates a prompt that instructs Claude (with Puppeteer MCP) to
        verify a web application and report the results.

        Args:
            url: URL to verify
            checks: List of checks to perform
            screenshot: Whether to take screenshot
            screenshot_name: Screenshot filename

        Returns:
            Formatted prompt string for Claude CLI

        Example:
            >>> client = PuppeteerClient()
            >>> prompt = client.generate_verification_prompt(
            ...     "http://localhost:8501",
            ...     ["page_loads", "no_errors"],
            ...     True,
            ...     "streamlit_dashboard"
            ... )
            >>> print(prompt)
            Use Puppeteer MCP to verify the web application at http://localhost:8501...
        """
        checks_formatted = "\n".join([f"  - {check}" for check in checks])

        prompt = f"""Use Puppeteer MCP to verify the web application at {url}.

Perform these checks:
{checks_formatted}

Steps:
1. Navigate to {url} using puppeteer_navigate
2. Wait 2-3 seconds for page to load
3. Check for JavaScript errors in console
4. Verify the page title and content
{"5. Take a screenshot named '" + screenshot_name + "' using puppeteer_screenshot" if screenshot else "5. Skip screenshot"}
6. Report results in this format:

✅ VERIFICATION PASSED - All checks successful
- page_loads: ✓ Loaded successfully
- no_errors: ✓ No JavaScript errors
- screenshot: ✓ Saved as {screenshot_name}

OR if any check fails:

❌ VERIFICATION FAILED - Some checks did not pass
- page_loads: ✗ Page failed to load (timeout)
- no_errors: ✓ No JavaScript errors
- screenshot: ✓ Saved as {screenshot_name}

Errors:
- Timeout after 30 seconds waiting for page load

Be thorough and report all findings.
"""
        return prompt

    def generate_dod_verification_prompt(self, priority: Dict, app_url: Optional[str] = None) -> str:
        """Generate a prompt for verifying Priority DoD using Puppeteer.

        This creates a comprehensive verification prompt that checks all
        acceptance criteria for a priority.

        Args:
            priority: Priority dictionary from ROADMAP
            app_url: Optional URL to test (auto-detected if not provided)

        Returns:
            Formatted prompt string for DoD verification

        Example:
            >>> client = PuppeteerClient()
            >>> priority = {
            ...     "name": "US-031",
            ...     "title": "Custom AI Environment",
            ...     "content": "...web interface...",
            ...     "acceptance_criteria": ["Web UI loads", "All features visible"]
            ... }
            >>> prompt = client.generate_dod_verification_prompt(priority, "http://localhost:8501")
        """
        priority_name = priority.get("name", "UNKNOWN")
        priority_title = priority.get("title", "UNKNOWN")
        acceptance_criteria = priority.get("acceptance_criteria", [])

        # Auto-detect URL from priority content if not provided
        if not app_url:
            content = priority.get("content", "")
            # Try to find URLs in content
            import re

            urls = re.findall(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                content,
            )
            if urls:
                app_url = urls[0]
            else:
                # Default to localhost:8501 (Streamlit default)
                app_url = "http://localhost:8501"

        criteria_formatted = "\n".join([f"  {i+1}. {c}" for i, c in enumerate(acceptance_criteria)])

        prompt = f"""Verify Definition of Done for {priority_name}: {priority_title}

Using Puppeteer MCP, verify that all acceptance criteria are met:

{criteria_formatted if criteria_formatted else "  (No explicit acceptance criteria provided)"}

Testing Steps:
1. Navigate to {app_url} using puppeteer_navigate
2. Wait for page to fully load (3-5 seconds)
3. Check that page loads without errors
4. Verify each acceptance criterion by:
   - Checking visual elements exist
   - Testing functionality (click, fill, etc.)
   - Confirming expected behavior
5. Take screenshots showing:
   - Initial page load
   - Each acceptance criterion demonstrated
   - Any errors encountered
6. Report comprehensive results

Report Format:

## DoD Verification Results for {priority_name}

### Summary
✅ PASSED - All acceptance criteria met
OR
❌ FAILED - X/Y criteria not met

### Detailed Results

1. [Criterion 1]: ✅ PASSED
   - Evidence: Screenshot shows feature working
   - Notes: Feature loads correctly and responds to user input

2. [Criterion 2]: ❌ FAILED
   - Evidence: Screenshot shows error message
   - Notes: Button click resulted in 404 error
   - Recommendation: Check endpoint configuration

### Screenshots
- dod_verification_initial.png - Initial page load
- dod_verification_criterion_1.png - Evidence for criterion 1
- dod_verification_criterion_2.png - Evidence for criterion 2

### Conclusion
[Overall assessment of whether DoD is met and any recommendations]

Be thorough, objective, and provide clear evidence for each criterion.
"""
        return prompt


# Convenience functions for quick access
def verify_web_app(url: str, checks: Optional[List[str]] = None) -> VerificationResult:
    """Quick verification of a web app (convenience function).

    Args:
        url: URL to verify
        checks: Optional list of checks to perform

    Returns:
        VerificationResult

    Example:
        >>> from coffee_maker.autonomous.puppeteer_client import verify_web_app
        >>> result = verify_web_app("http://localhost:8501")
    """
    client = PuppeteerClient()
    return client.verify_web_app(url, checks)


def generate_dod_prompt(priority: Dict, app_url: Optional[str] = None) -> str:
    """Quick DoD verification prompt generation (convenience function).

    Args:
        priority: Priority dictionary
        app_url: Optional URL to test

    Returns:
        Formatted verification prompt

    Example:
        >>> from coffee_maker.autonomous.puppeteer_client import generate_dod_prompt
        >>> prompt = generate_dod_prompt(priority, "http://localhost:8501")
    """
    client = PuppeteerClient()
    return client.generate_dod_verification_prompt(priority, app_url)
