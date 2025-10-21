"""
Dependency license checker.

Checks license compatibility with project license (Apache 2.0) using PyPI API.
"""

import logging
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


class LicenseChecker:
    """
    Checks license compatibility with project license (Apache 2.0).

    Uses PyPI JSON API to fetch package metadata and license information.
    """

    # License compatibility mappings
    PERMISSIVE_LICENSES = {
        "MIT",
        "BSD",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "Apache-2.0",
        "Apache 2.0",
        "ISC",
        "Unlicense",
        "CC0",
        "Python Software Foundation",
        "PSF",
        "0BSD",
        "Zlib",
        "X11",
        "WTFPL",
        "Public Domain",
    }

    COPYLEFT_LICENSES = {
        "GPL",
        "GPL-2.0",
        "GPL-3.0",
        "AGPL",
        "AGPL-3.0",
        "LGPL",
        "LGPL-2.1",
        "LGPL-3.0",
        "MPL",
        "MPL-2.0",
        "EPL",
        "EPL-1.0",
        "EPL-2.0",
        "EUPL",
    }

    # Known problematic packages with alternatives
    LICENSE_ALTERNATIVES = {
        "mysql-connector-python": ["pymysql", "aiomysql", "mysqlclient"],
        "PyQt5": ["PySide6", "tkinter (built-in)", "PyQt6 (LGPL)"],
        "PyQt6": ["PySide6", "tkinter (built-in)"],
        "rdkit": ["openbabel", "deepchem"],
    }

    def __init__(self):
        """Initialize checker with PyPI API client."""
        self.pypi_base_url = "https://pypi.org/pypi"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MonolithicCoffeeMakerAgent/1.0"})
        logger.debug("LicenseChecker initialized")

    def check_license(self, package_name: str) -> "LicenseInfo":  # noqa: F821
        """
        Check license compatibility for package.

        Args:
            package_name: Package to check

        Returns:
            LicenseInfo with compatibility details

        Implementation:
        1. Fetch package metadata from PyPI: GET /pypi/{package}/json
        2. Extract license from metadata["info"]["license"]
        3. Normalize license name (handle variations)
        4. Classify license type (permissive/copyleft/proprietary)
        5. Check compatibility with Apache 2.0
        6. Suggest alternatives if incompatible
        """
        logger.info(f"Checking license for {package_name}")

        # Fetch PyPI metadata
        metadata = self._fetch_pypi_metadata(package_name)

        # Extract license
        license_string = metadata.get("info", {}).get("license", "")
        classifiers = metadata.get("info", {}).get("classifiers", [])

        # Try to extract license from classifiers if license field is empty
        if not license_string or license_string.lower() in ["unknown", "none", ""]:
            for classifier in classifiers:
                if "License ::" in classifier:
                    license_string = classifier.split("::")[-1].strip()
                    break

        # Normalize license name
        license_name = self._normalize_license_name(license_string)

        # Classify license type
        license_type = self._classify_license_type(license_name)

        # Check compatibility with Apache 2.0
        compatible = self._is_compatible_with_apache2(license_name, license_type)

        # Generate issues list
        issues = []
        if not compatible:
            if license_type == "copyleft":
                issues.append(f"{license_name} is a copyleft license - may conflict with Apache 2.0")
            elif license_type == "proprietary":
                issues.append(f"{license_name} is proprietary - check licensing terms carefully")
            elif license_type == "unknown":
                issues.append("License type unknown - manual review required")

        # Get alternatives if incompatible
        alternatives = self._suggest_alternatives(package_name) if not compatible else []

        # Import here to avoid circular imports
        from coffee_maker.utils.dependency_analyzer import LicenseInfo

        license_info = LicenseInfo(
            license_name=license_name if license_name else "Unknown",
            license_type=license_type,
            compatible_with_apache2=compatible,
            issues=issues,
            alternatives=alternatives,
        )

        if compatible:
            logger.info(f"License check for {package_name}: {license_name} (compatible)")
        else:
            logger.warning(f"License check for {package_name}: {license_name} (INCOMPATIBLE)")

        return license_info

    def _fetch_pypi_metadata(self, package_name: str) -> Dict[str, Any]:
        """
        Fetch package metadata from PyPI JSON API.

        Args:
            package_name: Package name

        Returns:
            Dict with package metadata

        Raises:
            PackageNotFoundError: If package doesn't exist
        """
        try:
            url = f"{self.pypi_base_url}/{package_name}/json"
            logger.debug(f"Fetching PyPI metadata: {url}")

            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                from coffee_maker.utils.dependency_analyzer import PackageNotFoundError

                raise PackageNotFoundError(f"Package '{package_name}' not found on PyPI")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to fetch PyPI metadata for {package_name}: {str(e)}")
            # Return empty metadata on error
            return {"info": {"license": "Unknown"}}

    def _normalize_license_name(self, license_string: str) -> str:
        """
        Normalize license name (handle variations).

        Examples:
        - "MIT License" → "MIT"
        - "Apache-2.0" → "Apache 2.0"
        - "GPL v3" → "GPL-3.0"

        Args:
            license_string: Raw license string

        Returns:
            Normalized license name
        """
        if not license_string:
            return "Unknown"

        # Convert to upper case for matching
        upper = license_string.upper().strip()

        # MIT variations
        if "MIT" in upper:
            return "MIT"

        # BSD variations
        if "BSD" in upper:
            if "2-CLAUSE" in upper or "2 CLAUSE" in upper:
                return "BSD-2-Clause"
            elif "3-CLAUSE" in upper or "3 CLAUSE" in upper:
                return "BSD-3-Clause"
            return "BSD"

        # Apache variations
        if "APACHE" in upper:
            if "2.0" in upper or "2" in upper:
                return "Apache 2.0"
            return "Apache"

        # GPL variations
        if "GPL" in upper:
            if "AGPL" in upper:
                if "3" in upper:
                    return "AGPL-3.0"
                return "AGPL"
            elif "LGPL" in upper:
                if "2.1" in upper:
                    return "LGPL-2.1"
                elif "3" in upper:
                    return "LGPL-3.0"
                return "LGPL"
            else:
                if "2" in upper:
                    return "GPL-2.0"
                elif "3" in upper:
                    return "GPL-3.0"
                return "GPL"

        # ISC
        if "ISC" in upper:
            return "ISC"

        # MPL
        if "MPL" in upper or "MOZILLA" in upper:
            if "2.0" in upper or "2" in upper:
                return "MPL-2.0"
            return "MPL"

        # PSF (Python Software Foundation)
        if "PSF" in upper or "PYTHON SOFTWARE" in upper:
            return "Python Software Foundation"

        # Public Domain / Unlicense
        if "PUBLIC DOMAIN" in upper or "UNLICENSE" in upper:
            return "Public Domain"

        # CC0
        if "CC0" in upper:
            return "CC0"

        # If nothing matched, return original (cleaned)
        return license_string.strip()

    def _classify_license_type(self, license_name: str) -> str:
        """
        Classify license type.

        Returns: "permissive", "copyleft", "proprietary", or "unknown"

        Args:
            license_name: Normalized license name

        Returns:
            License type string
        """
        upper_name = license_name.upper()

        # Check permissive
        for perm_license in self.PERMISSIVE_LICENSES:
            if perm_license.upper() in upper_name:
                return "permissive"

        # Check copyleft
        for copyleft_license in self.COPYLEFT_LICENSES:
            if copyleft_license.upper() in upper_name:
                return "copyleft"

        # Check for proprietary indicators
        if any(word in upper_name for word in ["PROPRIETARY", "COMMERCIAL", "RESTRICTED"]):
            return "proprietary"

        # Default to unknown
        return "unknown"

    def _is_compatible_with_apache2(self, license_name: str, license_type: str) -> bool:
        """
        Check if license is compatible with Apache 2.0.

        Compatible:
        - MIT, BSD, Apache 2.0, ISC, Unlicense, CC0, PSF

        Incompatible:
        - GPL, AGPL, LGPL (copyleft)
        - Proprietary licenses

        Args:
            license_name: Normalized license name
            license_type: License type

        Returns:
            True if compatible, False otherwise
        """
        # Permissive licenses are compatible
        if license_type == "permissive":
            return True

        # Copyleft licenses are incompatible
        if license_type == "copyleft":
            return False

        # Proprietary licenses are incompatible
        if license_type == "proprietary":
            return False

        # Unknown licenses require manual review (mark as incompatible for safety)
        if license_type == "unknown":
            return False

        # Default to compatible if nothing else matched
        return True

    def _suggest_alternatives(self, package_name: str) -> List[str]:
        """
        Suggest alternative packages with compatible licenses.

        Uses hardcoded mapping for common cases:
        - mysql-connector-python (GPL) → pymysql, aiomysql
        - PyQt5 (GPL) → PySide6 (LGPL), tkinter (built-in)

        Args:
            package_name: Package name

        Returns:
            List of alternative package names
        """
        return self.LICENSE_ALTERNATIVES.get(package_name, [])
