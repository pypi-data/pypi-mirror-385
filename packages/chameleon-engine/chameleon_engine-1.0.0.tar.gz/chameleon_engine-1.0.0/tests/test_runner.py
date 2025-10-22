"""
Test runner for Chameleon Engine test suite.

Provides comprehensive test execution with reporting, coverage analysis,
and performance benchmarking.
"""

import os
import sys
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestRunner:
    """Comprehensive test runner for Chameleon Engine."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.src_dir = project_root / "src"
        self.results_dir = project_root / "test_results"
        self.coverage_dir = project_root / "coverage"

        # Create results directories
        self.results_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)

        self.results = {
            "timestamp": time.time(),
            "python_version": sys.version,
            "platform": sys.platform,
            "test_results": {},
            "coverage": {},
            "performance": {},
            "summary": {}
        }

    def run_tests(self, test_pattern: str = "test_*.py",
                  coverage: bool = True,
                  performance: bool = True,
                  verbose: bool = False) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        print(f"🚀 Starting Chameleon Engine Test Suite")
        print(f"📁 Project Root: {self.project_root}")
        print(f"🧪 Test Directory: {self.test_dir}")
        print(f"📊 Results Directory: {self.results_dir}")
        print()

        # Run unit tests
        print("🔬 Running Unit Tests...")
        unit_results = self._run_unit_tests(test_pattern, verbose)
        self.results["test_results"]["unit"] = unit_results
        print(f"✅ Unit Tests: {unit_results['passed']}/{unit_results['total']} passed")

        # Run integration tests
        print("🔗 Running Integration Tests...")
        integration_results = self._run_integration_tests(verbose)
        self.results["test_results"]["integration"] = integration_results
        print(f"✅ Integration Tests: {integration_results['passed']}/{integration_results['total']} passed")

        # Run performance tests
        if performance:
            print("⚡ Running Performance Tests...")
            perf_results = self._run_performance_tests(verbose)
            self.results["performance"] = perf_results
            print("✅ Performance Tests completed")

        # Run coverage analysis
        if coverage:
            print("📈 Running Coverage Analysis...")
            coverage_results = self._run_coverage_analysis(test_pattern, verbose)
            self.results["coverage"] = coverage_results
            print(f"✅ Coverage: {coverage_results['total_coverage']:.1f}%")

        # Generate summary
        self._generate_summary()

        # Save results
        self._save_results()

        print()
        print("📋 Test Summary:")
        print(f"   Total Tests: {self.results['summary']['total_tests']}")
        print(f"   Passed: {self.results['summary']['passed_tests']}")
        print(f"   Failed: {self.results['summary']['failed_tests']}")
        print(f"   Success Rate: {self.results['summary']['success_rate']:.1f}%")
        print(f"   Coverage: {self.results['summary']['coverage']:.1f}%")
        print(f"   Duration: {self.results['summary']['duration']:.2f}s")

        return self.results

    def _run_unit_tests(self, pattern: str, verbose: bool) -> Dict[str, Any]:
        """Run unit tests."""
        unit_test_files = [
            "test_core_profiles.py",
            "test_database_models.py",
            "test_fingerprint_services.py",
            "test_proxy_binary_services.py",
            "test_behavior_and_orchestrator.py"
        ]

        cmd = [
            sys.executable, "-m", "pytest",
            "-v" if verbose else "-q",
            "--tb=short",
            "--json-report",
            f"--json-report-file={self.results_dir / 'unit_tests.json'}"
        ]

        # Add specific test files
        for test_file in unit_test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))

        # Add coverage if available
        try:
            import pytest_cov
            cmd.extend([
                "--cov=chameleon_engine",
                f"--cov-report=html:{self.coverage_dir}",
                f"--cov-report=xml:{self.coverage_dir / 'coverage.xml'}",
                "--cov-report=term-missing"
            ])
        except ImportError:
            pass

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        # Parse results
        results = {
            "duration": duration,
            "command": " ".join(cmd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": {}
        }

        # Try to parse JSON report
        json_report_path = self.results_dir / "unit_tests.json"
        if json_report_path.exists():
            try:
                with open(json_report_path) as f:
                    json_data = json.load(f)

                if "summary" in json_data:
                    summary = json_data["summary"]
                    results["passed"] = summary.get("passed", 0)
                    results["failed"] = summary.get("failed", 0)
                    results["total"] = summary.get("total", 0)
                    results["details"] = json_data.get("tests", [])
            except (json.JSONDecodeError, KeyError):
                pass

        # Fallback: parse from stdout
        if results["total"] == 0 and result.stdout:
            import re
            # Look for pytest summary format
            match = re.search(r'(\d+)\s+passed,\s+(\d+)\s+failed', result.stdout)
            if match:
                results["passed"] = int(match.group(1))
                results["failed"] = int(match.group(2))
                results["total"] = results["passed"] + results["failed"]

        return results

    def _run_integration_tests(self, verbose: bool) -> Dict[str, Any]:
        """Run integration tests."""
        integration_test_files = [
            "test_integration_comprehensive.py"
        ]

        cmd = [
            sys.executable, "-m", "pytest",
            "-v" if verbose else "-q",
            "--tb=short",
            "--json-report",
            f"--json-report-file={self.results_dir / 'integration_tests.json'}"
        ]

        for test_file in integration_test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                cmd.append(str(test_path))

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        results = {
            "duration": duration,
            "command": " ".join(cmd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": {}
        }

        # Parse JSON report if available
        json_report_path = self.results_dir / "integration_tests.json"
        if json_report_path.exists():
            try:
                with open(json_report_path) as f:
                    json_data = json.load(f)

                if "summary" in json_data:
                    summary = json_data["summary"]
                    results["passed"] = summary.get("passed", 0)
                    results["failed"] = summary.get("failed", 0)
                    results["total"] = summary.get("total", 0)
            except (json.JSONDecodeError, KeyError):
                pass

        return results

    def _run_performance_tests(self, verbose: bool) -> Dict[str, Any]:
        """Run performance benchmarks."""
        # Create performance test script
        perf_script = self.test_dir / "performance_benchmarks.py"
        if not perf_script.exists():
            # Create a basic performance test
            self._create_performance_test_script(perf_script)

        cmd = [
            sys.executable, str(perf_script),
            "--output", str(self.results_dir / "performance_results.json")
        ]

        if verbose:
            cmd.append("--verbose")

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        results = {
            "duration": duration,
            "command": " ".join(cmd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "benchmarks": {}
        }

        # Parse performance results
        perf_results_path = self.results_dir / "performance_results.json"
        if perf_results_path.exists():
            try:
                with open(perf_results_path) as f:
                    perf_data = json.load(f)
                results["benchmarks"] = perf_data.get("benchmarks", {})
            except (json.JSONDecodeError, KeyError):
                pass

        return results

    def _run_coverage_analysis(self, pattern: str, verbose: bool) -> Dict[str, Any]:
        """Run coverage analysis."""
        results = {
            "total_coverage": 0.0,
            "file_coverage": {},
            "missing_lines": {},
            "html_report": str(self.coverage_dir / "index.html"),
            "xml_report": str(self.coverage_dir / "coverage.xml")
        }

        try:
            # Try to read coverage from XML report
            xml_report_path = self.coverage_dir / "coverage.xml"
            if xml_report_path.exists():
                import xml.etree.ElementTree as ET
                tree = ET.parse(xml_report_path)
                root = tree.getroot()

                # Find overall coverage
                coverage_elem = root.find(".//coverage")
                if coverage_elem is not None:
                    line_rate = coverage_elem.get("line-rate", "0")
                    results["total_coverage"] = float(line_rate) * 100

                # Find per-file coverage
                for class_elem in root.findall(".//class"):
                    filename = class_elem.get("filename", "")
                    line_rate = class_elem.get("line-rate", "0")
                    if filename and line_rate:
                        results["file_coverage"][filename] = float(line_rate) * 100

        except Exception as e:
            results["error"] = str(e)

        return results

    def _create_performance_test_script(self, script_path: Path):
        """Create a basic performance test script."""
        script_content = '''#!/usr/bin/env python3
"""
Performance benchmarks for Chameleon Engine.
"""

import asyncio
import time
import json
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

async def benchmark_profile_generation():
    """Benchmark profile generation performance."""
    from chameleon_engine.services.fingerprint.models import FingerprintRequest

    times = []
    iterations = 100

    for _ in range(iterations):
        start_time = time.time()
        request = FingerprintRequest(
            browser_type="chrome",
            operating_system="windows",
            min_quality=0.8
        )
        end_time = time.time()
        times.append(end_time - start_time)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    return {
        "iterations": iterations,
        "average_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
        "throughput": iterations / sum(times)
    }

async def benchmark_bezier_curves():
    """Benchmark Bezier curve calculation performance."""
    from chameleon_engine.behavior.mouse import BezierCurve

    times = []
    iterations = 1000

    for _ in range(iterations):
        start_time = time.time()
        curve = BezierCurve((0, 0), (50, 100), (150, -100), (200, 0))
        curve.get_length()
        curve.get_point(0.5)
        end_time = time.time()
        times.append(end_time - start_time)

    avg_time = sum(times) / len(times)

    return {
        "iterations": iterations,
        "average_time": avg_time,
        "throughput": iterations / sum(times)
    }

async def benchmark_database_operations():
    """Benchmark database operation performance."""
    try:
        from chameleon_engine.services.database.models import FingerprintRecord
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Use in-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:")
        Session = sessionmaker(bind=engine)
        session = Session()

        times = []
        iterations = 100

        for _ in range(iterations):
            start_time = time.time()

            # Simulate database operations
            record = FingerprintRecord(
                fingerprint_id=f"test_{_}",
                browser_type="chrome",
                operating_system="windows",
                profile_data={"user_agent": "test"},
                coherence_score=0.8,
                uniqueness_score=0.7,
                detection_risk=0.1,
                generation_method="test",
                quality_score=0.75
            )

            end_time = time.time()
            times.append(end_time - start_time)

        avg_time = sum(times) / len(times)

        return {
            "iterations": iterations,
            "average_time": avg_time,
            "throughput": iterations / sum(times)
        }

    except Exception as e:
        return {"error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Run performance benchmarks")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        print("Running performance benchmarks...")

    benchmarks = {}

    # Run benchmarks
    if args.verbose:
        print("  Benchmarking profile generation...")
    benchmarks["profile_generation"] = await benchmark_profile_generation()

    if args.verbose:
        print("  Benchmarking Bezier curves...")
    benchmarks["bezier_curves"] = await benchmark_bezier_curves()

    if args.verbose:
        print("  Benchmarking database operations...")
    benchmarks["database_operations"] = await benchmark_database_operations()

    results = {
        "timestamp": time.time(),
        "benchmarks": benchmarks
    }

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    if args.verbose:
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
'''
        script_path.write_text(script_content)
        script_path.chmod(0o755)

    def _generate_summary(self):
        """Generate test summary."""
        unit_tests = self.results["test_results"].get("unit", {})
        integration_tests = self.results["test_results"].get("integration", {})
        coverage_data = self.results.get("coverage", {})

        total_passed = unit_tests.get("passed", 0) + integration_tests.get("passed", 0)
        total_failed = unit_tests.get("failed", 0) + integration_tests.get("failed", 0)
        total_tests = total_passed + total_failed

        duration = (
            unit_tests.get("duration", 0) +
            integration_tests.get("duration", 0) +
            self.results.get("performance", {}).get("duration", 0)
        )

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": total_passed,
            "failed_tests": total_failed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "coverage": coverage_data.get("total_coverage", 0),
            "duration": duration,
            "status": "PASSED" if total_failed == 0 else "FAILED"
        }

    def _save_results(self):
        """Save test results to files."""
        # Save comprehensive results
        results_file = self.results_dir / f"test_results_{int(self.results['timestamp'])}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Save latest results (for easy access)
        latest_file = self.results_dir / "latest_test_results.json"
        with open(latest_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        # Generate HTML report
        self._generate_html_report()

        print(f"📄 Results saved to: {results_file}")
        print(f"🌐 HTML report: {self.results_dir / 'test_report.html'}")

    def _generate_html_report(self):
        """Generate HTML test report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chameleon Engine Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .passed {{ color: green; }}
        .failed {{ color: red; }}
        .coverage {{ color: blue; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-pass {{ background-color: #d4edda; }}
        .status-fail {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Chameleon Engine Test Report</h1>
        <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.results['timestamp']))}</p>
        <p>Python: {self.results['python_version'].split()[0]} | Platform: {self.results['platform']}</p>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Tests:</strong> {self.results['summary']['total_tests']}</p>
        <p><strong>Passed:</strong> <span class="passed">{self.results['summary']['passed_tests']}</span></p>
        <p><strong>Failed:</strong> <span class="failed">{self.results['summary']['failed_tests']}</span></p>
        <p><strong>Success Rate:</strong> {self.results['summary']['success_rate']:.1f}%</p>
        <p><strong>Coverage:</strong> <span class="coverage">{self.results['summary']['coverage']:.1f}%</span></p>
        <p><strong>Duration:</strong> {self.results['summary']['duration']:.2f}s</p>
        <p><strong>Status:</strong> <span class="{'passed' if self.results['summary']['status'] == 'PASSED' else 'failed'}">{self.results['summary']['status']}</span></p>
    </div>

    <h2>Test Results</h2>
    <table>
        <tr>
            <th>Test Type</th>
            <th>Total</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Duration</th>
            <th>Status</th>
        </tr>
"""

        # Add unit test results
        unit_tests = self.results["test_results"].get("unit", {})
        html_content += f"""
        <tr class="status-{'pass' if unit_tests.get('failed', 0) == 0 else 'fail'}">
            <td>Unit Tests</td>
            <td>{unit_tests.get('total', 0)}</td>
            <td>{unit_tests.get('passed', 0)}</td>
            <td>{unit_tests.get('failed', 0)}</td>
            <td>{unit_tests.get('duration', 0):.2f}s</td>
            <td>{'PASS' if unit_tests.get('failed', 0) == 0 else 'FAIL'}</td>
        </tr>
"""

        # Add integration test results
        integration_tests = self.results["test_results"].get("integration", {})
        html_content += f"""
        <tr class="status-{'pass' if integration_tests.get('failed', 0) == 0 else 'fail'}">
            <td>Integration Tests</td>
            <td>{integration_tests.get('total', 0)}</td>
            <td>{integration_tests.get('passed', 0)}</td>
            <td>{integration_tests.get('failed', 0)}</td>
            <td>{integration_tests.get('duration', 0):.2f}s</td>
            <td>{'PASS' if integration_tests.get('failed', 0) == 0 else 'FAIL'}</td>
        </tr>
"""

        # Add performance results if available
        perf_data = self.results.get("performance", {})
        if perf_data.get("benchmarks"):
            html_content += f"""
        <tr>
            <td>Performance Tests</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>{perf_data.get('duration', 0):.2f}s</td>
            <td>COMPLETE</td>
        </tr>
"""

        html_content += """
    </table>

    <h2>Coverage Analysis</h2>
"""

        if self.results.get("coverage", {}).get("total_coverage", 0) > 0:
            coverage = self.results["coverage"]
            html_content += f"""
    <p><strong>Total Coverage:</strong> {coverage['total_coverage']:.1f}%</p>

    <h3>Coverage by File</h3>
    <table>
        <tr>
            <th>File</th>
            <th>Coverage</th>
        </tr>
"""

            for filename, cov_percent in coverage.get("file_coverage", {}).items():
                html_content += f"""
        <tr>
            <td>{filename}</td>
            <td>{cov_percent:.1f}%</td>
        </tr>
"""

            html_content += """
    </table>
"""
        else:
            html_content += "<p>No coverage data available. Install pytest-cov to generate coverage reports.</p>"

        html_content += """
</body>
</html>
"""

        # Save HTML report
        html_file = self.results_dir / "test_report.html"
        html_file.write_text(html_content)


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run Chameleon Engine test suite")
    parser.add_argument("--pattern", default="test_*.py", help="Test file pattern")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage analysis")
    parser.add_argument("--no-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    # Determine project root
    if args.project_root:
        project_root = args.project_root
    else:
        # Assume script is in tests/ directory
        project_root = Path(__file__).parent.parent

    # Create and run test runner
    runner = TestRunner(project_root)

    try:
        results = runner.run_tests(
            test_pattern=args.pattern,
            coverage=not args.no_coverage,
            performance=not args.no_performance,
            verbose=args.verbose
        )

        # Exit with appropriate code
        exit_code = 0 if results["summary"]["status"] == "PASSED" else 1
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()