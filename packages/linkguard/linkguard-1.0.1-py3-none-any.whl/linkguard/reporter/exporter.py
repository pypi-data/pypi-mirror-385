"""Result export functionality for LinkGuard scan reports.

This module provides export capabilities to multiple formats:
- JSON: Machine-readable with full metadata and structured data
- CSV: Spreadsheet-compatible tabular format
- Markdown: Human-readable formatted reports with tables

Classes:
    Exporter: Static methods for exporting scan results to different formats.

Example:
    >>> from linkguard.scanner.link_checker import LinkResult
    >>> from linkguard.scanner.rules import RuleViolation
    >>>
    >>> results = [...]  # List of LinkResult objects
    >>> violations = [...]  # List of RuleViolation objects
    >>>
    >>> # Export to JSON
    >>> Exporter.export_to_json(
    ...     results, violations, Path("report.json"),
    ...     metadata={"directory": "/path", "mode": "prod"}
    ... )
    >>>
    >>> # Export to CSV
    >>> Exporter.export_to_csv(results, violations, Path("report.csv"))
    >>>
    >>> # Export to Markdown
    >>> Exporter.export_to_markdown(
    ...     results, violations, Path("report.md"),
    ...     metadata={"directory": "/path", "mode": "prod"}
    ... )
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from linkguard.scanner.link_checker import LinkResult
from linkguard.scanner.rules import RuleViolation


class Exporter:
    """Static utility class for exporting scan results to multiple formats.

    Supports JSON (machine-readable), CSV (spreadsheet), and Markdown (human-readable)
    exports. All exports include timestamps, metadata, and comprehensive result details.

    Methods:
        export_to_json: Export to structured JSON with full metadata.
        export_to_csv: Export to CSV spreadsheet format.
        export_to_markdown: Export to formatted Markdown report.

    Example:
        >>> Exporter.export_to_json(
        ...     results, violations, Path("output.json"),
        ...     metadata={"directory": "/my/project", "mode": "prod"}
        ... )
    """

    @staticmethod
    def export_to_json(
        results: List[LinkResult],
        violations: List[RuleViolation],
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Export scan results to JSON format with full metadata.

        Creates a JSON file with three main sections:
        - metadata: Scan statistics, timestamp, and custom metadata
        - results: Detailed link check results with timing and errors
        - violations: Environment rule violations (dev URLs in prod mode)

        Args:
            results: List of link validation results.
            violations: List of environment rule violations.
            output_path: Path where JSON file will be saved.
            metadata: Optional additional metadata (directory, mode, timeout, etc.).

        Example:
            >>> metadata = {"directory": "/path", "mode": "prod", "timeout": 10}
            >>> Exporter.export_to_json(results, violations, Path("report.json"), metadata)

        Output Structure:
            {
              "metadata": {
                "timestamp": "2025-01-15T10:30:00",
                "total_links": 100,
                "broken_links": 5,
                "working_links": 95,
                "violations": 2,
                ...custom metadata...
              },
              "results": [...],
              "violations": [...]
            }
        """
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_links": len(results),
                "broken_links": sum(1 for r in results if r.is_broken),
                "working_links": sum(1 for r in results if not r.is_broken),
                "violations": len(violations),
                **(metadata or {}),
            },
            "results": [
                {
                    "url": r.url,
                    "status_code": r.status_code,
                    "is_broken": r.is_broken,
                    "error": r.error,
                    "response_time": r.response_time,
                    "file_path": str(r.file_path),
                    "line_number": r.line_number,
                }
                for r in results
            ],
            "violations": [
                {
                    "url": v.url,
                    "rule": v.rule,
                    "severity": v.severity,
                    "message": v.message,
                    "file_path": str(v.file_path),
                    "line_number": v.line_number,
                }
                for v in violations
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_csv(
        results: List[LinkResult],
        violations: List[RuleViolation],
        output_path: Path,
    ) -> None:
        """Export scan results to CSV spreadsheet format.

        Creates a CSV file with columns for URL, status, errors, timing,
        and rule violations. Violations are merged with results by URL
        for a denormalized view suitable for spreadsheet analysis.

        Args:
            results: List of link validation results.
            violations: List of environment rule violations.
            output_path: Path where CSV file will be saved.

        CSV Columns:
            - URL: The checked URL
            - Status Code: HTTP status code (or N/A)
            - Is Broken: "Yes" or "No"
            - Error: Error message if failed
            - Response Time (s): Request duration
            - File Path: Source file containing the URL
            - Line Number: Line in source file
            - Rule Violation: Rule name if violated
            - Violation Severity: Severity level (warning/error)

        Example:
            >>> Exporter.export_to_csv(results, violations, Path("report.csv"))
        """

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header row
            writer.writerow(
                [
                    "URL",
                    "Status Code",
                    "Is Broken",
                    "Error",
                    "Response Time (s)",
                    "File Path",
                    "Line Number",
                    "Rule Violation",
                    "Violation Severity",
                ]
            )

            # Create a map for quick violation lookup by URL
            violation_map = {v.url: v for v in violations}

            # Write data rows - one per result, with violation data if present
            for r in results:
                violation = violation_map.get(r.url)

                writer.writerow(
                    [
                        r.url,
                        r.status_code or "N/A",
                        "Yes" if r.is_broken else "No",
                        r.error or "N/A",
                        f"{r.response_time:.2f}" if r.response_time else None,
                        r.file_path,
                        r.line_number or "N/A",
                        violation.rule if violation else None,
                        violation.severity if violation else None,
                    ]
                )

    @staticmethod
    def export_to_markdown(
        results: List[LinkResult],
        violations: List[RuleViolation],
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Export scan results to formatted Markdown report.

        Creates a human-readable Markdown report with:
        - Summary statistics (total, broken, working, violations)
        - Scan details (directory, mode, timeout from metadata)
        - Rule violations table (if any)
        - Broken links table (if any)
        - Working links table (if any)

        Args:
            results: List of link validation results.
            violations: List of environment rule violations.
            output_path: Path where Markdown file will be saved.
            metadata: Optional scan metadata (directory, mode, timeout, etc.).

        Report Structure:
            # LinkGuard Scan Report
            ## Summary
            - Statistics
            ## Scan Details
            - Metadata
            ## Rule Violations
            - Table of violations (if any)
            ## Broken Links
            - Table of broken links (if any)
            ## Working Links
            - Table of working links (if any)

        Example:
            >>> metadata = {"directory": "/my/project", "mode": "prod"}
            >>> Exporter.export_to_markdown(results, violations, Path("report.md"), metadata)
        """

        # Separate results into broken and working
        broken = [r for r in results if r.is_broken]
        working = [r for r in results if not r.is_broken]

        # Build Markdown content as list of lines
        lines = [
            "# Linkguard Scan Report\n",
            "",
            f"**Generated on:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            "",
            f"- Total Links Checked: {len(results)}",
            f"- Working Links: {len(working)}",
            f"- Broken Links: {len(broken)}",
            f"- Rule Violations: {len(violations)}",
            "",
        ]

        # Add scan details section if metadata provided
        if metadata:
            lines.extend(
                [
                    "## Scan Details",
                    "",
                    f"- **Directory:** `{metadata.get('directory', 'N/A')}`",
                    f"- **Mode:** `{metadata.get('mode', 'N/A')}`",
                    f"- **Timeout:** `{metadata.get('timeout', 'N/A')} seconds`",
                    "",
                ]
            )

        # Add rule violations table if any violations found
        if violations:
            lines.extend(
                [
                    "## Rule Violations",
                    "",
                    "| URL | Rule | Severity | Message | File Path | Line Number |",
                    "|-----|------|----------|---------|-----------|-------------|",
                ]
            )

            for v in violations:
                lines.append(
                    f"| {v.url} | {v.rule} | {v.severity} | "
                    f"{v.message} | {v.file_path} | "
                    f"{v.line_number or 'N/A'} |"
                )

            lines.append("")

        # Add broken links table if any broken links found
        if broken:
            lines.extend(
                [
                    "## Broken Links",
                    "",
                    "| URL | Status Code | Error | Response Time (s) | File Path | Line Number |",
                    "|-----|-------------|-------|-------------------|-----------|-------------|",
                ]
            )

            for r in broken:
                time_str = f"{r.response_time:.2f}" if r.response_time else "N/A"
                lines.append(
                    f"| {r.url} | {r.status_code or 'N/A'} | "
                    f"{r.error or 'N/A'} | {time_str} | "
                    f"{r.file_path} | {r.line_number or 'N/A'} |"
                )

            lines.append("")

        # Add working links table if any working links found
        if working:
            lines.extend(
                [
                    "## Working Links",
                    "",
                    "| URL | Status Code | Response Time (s) | File Path | Line Number |",
                    "|-----|-------------|-------------------|-----------|-------------|",
                ]
            )

            for r in working:
                time_str = f"{r.response_time:.2f}" if r.response_time else "N/A"
                lines.append(
                    f"| {r.url} | {r.status_code or 'N/A'} | "
                    f"{time_str} | {r.file_path} | "
                    f"{r.line_number or 'N/A'} |"
                )

            lines.append("")

        # Write all lines to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
