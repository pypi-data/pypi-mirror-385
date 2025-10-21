"""Security Auditor perspective - Audits security vulnerabilities.

This perspective focuses on:
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting)
- Authentication and authorization issues
- Sensitive data exposure
- Insecure cryptography
- Command injection
"""

import re
from typing import List

from coffee_maker.code_reviewer.perspectives.base_perspective import BasePerspective
from coffee_maker.code_reviewer.models import ReviewIssue


class SecurityAuditor(BasePerspective):
    """Audits code for security vulnerabilities and weaknesses.

    Uses specialized security analysis to identify:
    - Injection vulnerabilities
    - Authentication issues
    - Sensitive data exposure
    - Cryptographic weaknesses
    - Access control problems

    Example:
        >>> auditor = SecurityAuditor()
        >>> issues = auditor.analyze(code_content, "auth.py")
        >>> critical_sec_issues = [i for i in issues if i.severity == "critical"]
    """

    def __init__(self, model_name: str = "security-specialized"):
        """Initialize Security Auditor.

        Args:
            model_name: Model to use for security analysis
        """
        super().__init__(model_name=model_name, perspective_name="Security Auditor")

    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code for security vulnerabilities.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of security issues found
        """
        issues = []

        # Mock analysis - In production, this would use specialized security tools
        issues.extend(self._check_sql_injection(code_content))
        issues.extend(self._check_command_injection(code_content))
        issues.extend(self._check_hardcoded_secrets(code_content))
        issues.extend(self._check_insecure_random(code_content))
        issues.extend(self._check_path_traversal(code_content))

        self.last_analysis_summary = (
            f"Analyzed {len(code_content.splitlines())} lines, found {len(issues)} security concerns"
        )

        return issues

    async def analyze_async(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        """Analyze code asynchronously.

        Args:
            code_content: Source code to analyze
            file_path: Path to file being analyzed

        Returns:
            List of security issues found
        """
        return self.analyze(code_content, file_path)

    def _check_sql_injection(self, code: str) -> List[ReviewIssue]:
        """Check for SQL injection vulnerabilities.

        Args:
            code: Code to analyze

        Returns:
            List of SQL injection issues
        """
        issues = []

        # Check for string formatting in SQL queries
        sql_patterns = [
            (r'execute\(["\'].*%s.*["\'].*%', "String formatting in SQL"),
            (r'execute\(f["\'].*\{.*\}.*["\']', "F-string in SQL query"),
            (r'execute\(["\'].*\+.*["\']', "String concatenation in SQL"),
            (r"cursor\.execute\(.*\.format\(", ".format() in SQL query"),
        ]

        for i, line in enumerate(code.splitlines(), 1):
            for pattern, description in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        self._create_issue(
                            severity="critical",
                            category="security",
                            title="SQL Injection vulnerability",
                            description=f"{description} - Direct string interpolation can lead to SQL injection",
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion="Use parameterized queries: execute(query, (param1, param2))",
                        )
                    )

        return issues

    def _check_command_injection(self, code: str) -> List[ReviewIssue]:
        """Check for command injection vulnerabilities.

        Args:
            code: Code to analyze

        Returns:
            List of command injection issues
        """
        issues = []

        # Check for shell=True or string-based subprocess calls
        for i, line in enumerate(code.splitlines(), 1):
            if "subprocess" in line or "os.system" in line or "os.popen" in line:
                if "shell=True" in line or "os.system(" in line or "os.popen(" in line:
                    # Check if user input is involved
                    if any(
                        keyword in line
                        for keyword in [
                            "input(",
                            "request.",
                            "args.",
                            "form.",
                            "data.",
                            "params.",
                        ]
                    ):
                        issues.append(
                            self._create_issue(
                                severity="critical",
                                category="security",
                                title="Command Injection vulnerability",
                                description="Executing shell commands with user input can lead to command injection",
                                line_number=i,
                                code_snippet=line.strip(),
                                suggestion="Use subprocess with list arguments and shell=False, or sanitize input",
                            )
                        )
                    elif "shell=True" in line:
                        issues.append(
                            self._create_issue(
                                severity="high",
                                category="security",
                                title="Shell execution enabled",
                                description="shell=True allows shell injection if input is not properly sanitized",
                                line_number=i,
                                code_snippet=line.strip(),
                                suggestion="Use shell=False and pass command as list",
                            )
                        )

        return issues

    def _check_hardcoded_secrets(self, code: str) -> List[ReviewIssue]:
        """Check for hardcoded passwords, API keys, and secrets.

        Args:
            code: Code to analyze

        Returns:
            List of hardcoded secret issues
        """
        issues = []

        # Patterns for common secrets
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
            (r'aws_secret_access_key\s*=\s*["\']', "Hardcoded AWS secret"),
            (r'private_key\s*=\s*["\']', "Hardcoded private key"),
        ]

        for i, line in enumerate(code.splitlines(), 1):
            # Skip comments and empty values
            if line.strip().startswith("#") or '""' in line or "''" in line:
                continue

            for pattern, description in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(
                        self._create_issue(
                            severity="critical",
                            category="security",
                            title="Hardcoded secret detected",
                            description=f"{description} - Secrets should never be hardcoded in source code",
                            line_number=i,
                            code_snippet=line.strip()[:50] + "...",  # Truncate to avoid exposing secret
                            suggestion="Use environment variables, secret management services, or config files",
                        )
                    )

        return issues

    def _check_insecure_random(self, code: str) -> List[ReviewIssue]:
        """Check for insecure random number generation.

        Args:
            code: Code to analyze

        Returns:
            List of insecure random issues
        """
        issues = []

        # Check for random.random() used in security contexts
        security_contexts = ["token", "password", "secret", "key", "salt", "nonce", "session"]

        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            if "random.random()" in line or "random.randint(" in line or "random.choice(" in line:
                # Check surrounding context
                context = " ".join(lines[max(0, i - 3) : min(len(lines), i + 2)])

                if any(ctx in context.lower() for ctx in security_contexts):
                    issues.append(
                        self._create_issue(
                            severity="high",
                            category="security",
                            title="Insecure random number generation",
                            description="random module is not cryptographically secure and should not be used for security purposes",
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion="Use secrets module: secrets.token_bytes(), secrets.token_hex(), or secrets.choice()",
                        )
                    )

        return issues

    def _check_path_traversal(self, code: str) -> List[ReviewIssue]:
        """Check for path traversal vulnerabilities.

        Args:
            code: Code to analyze

        Returns:
            List of path traversal issues
        """
        issues = []

        # Check for file operations with user input
        file_operations = ["open(", "Path(", "os.path.join(", "pathlib.Path("]
        user_input_indicators = ["request.", "args.", "form.", "data.", "params.", "input("]

        for i, line in enumerate(code.splitlines(), 1):
            # Check if line has file operation
            has_file_op = any(op in line for op in file_operations)
            has_user_input = any(ui in line for ui in user_input_indicators)

            if has_file_op and has_user_input:
                # Check if there's path validation
                if "realpath" not in line and "abspath" not in line and "normpath" not in line:
                    issues.append(
                        self._create_issue(
                            severity="high",
                            category="security",
                            title="Path traversal vulnerability",
                            description="File operations with unsanitized user input can lead to path traversal attacks",
                            line_number=i,
                            code_snippet=line.strip(),
                            suggestion="Validate and sanitize file paths, use os.path.realpath() to resolve paths",
                        )
                    )

        return issues
