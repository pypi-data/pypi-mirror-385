"""Parsing service for handling result parsing operations."""

import json
from typing import Any

from ..models.schema import StructuredResults
from ..services.base import BaseService
from ..services.workload_service import WorkloadService


class ParsingService(BaseService):
    """Service for handling result parsing operations."""

    def __init__(self, workload_service: WorkloadService | None = None) -> None:
        """Initialize the parsing service.

        Args:
            workload_service: Workload service instance
        """
        super().__init__()
        self.workload_service = workload_service or WorkloadService()

    def initialize(self) -> None:
        """Initialize the parsing service."""
        self.workload_service.initialize()

    def cleanup(self) -> None:
        """Cleanup parsing service resources."""
        self.workload_service.cleanup()

    def _health_check(self) -> bool:
        """Check if parsing service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self.workload_service.is_healthy()

    async def parse_results(
        self,
        input_path: str,
        workload_name: str,
    ) -> StructuredResults:
        """Parse results using workload-specific extraction tools.

        Args:
            input_path: Path to file or directory to parse
            workload_name: Name of the workload (for tool selection)

        Returns:
            StructuredResults with extracted data or empty results on failure
        """
        if not input_path:
            self.logger.error("❌ No input_path provided to parse_results.")
            return StructuredResults(iterations=[])

        if not workload_name:
            self.logger.error(
                "❌ No workload_name provided. Cannot select extraction tool."
            )
            return StructuredResults(iterations=[])

        try:
            extracted_results = await self._try_workload_extraction(
                workload_name, input_path
            )
            if not extracted_results or not extracted_results.get("success"):
                self.logger.warning(
                    f"⚠️ Extraction failed or returned no results for workload '{workload_name}': "
                    f"{extracted_results.get('error') if extracted_results else 'No result'}"
                )
                return StructuredResults(iterations=[])

            # Attempt to parse the raw output into StructuredResults
            raw_output = extracted_results.get("raw_output")
            if not raw_output:
                self.logger.error("❌ No raw_output found in extraction results.")
                return StructuredResults(iterations=[])

            try:
                # If raw_output is already a dict, use it; else, try to parse as JSON
                if isinstance(raw_output, dict):
                    structured_data = raw_output
                else:
                    structured_data = json.loads(raw_output)

                # Validate/parse with StructuredResults
                results = StructuredResults.parse_obj(structured_data)
                self.logger.info("✅ Successfully parsed structured results.")
                return results
            except Exception as parse_exc:
                self.logger.error(f"❌ Failed to parse structured results: {parse_exc}")
                return StructuredResults(iterations=[])

        except Exception as e:
            self.logger.error(f"❌ Error in parse_results: {e}")
            self.logger.warning(
                "🔄 Returning empty results due to error in results parsing"
            )
            return StructuredResults(iterations=[])

    async def _try_workload_extraction(
        self, workload_name: str, input_path: str
    ) -> dict[str, Any]:
        """Try to extract data using workload-specific tool.

        Args:
            workload_name: Name of the workload
            input_path: Path to input file or directory

        Returns:
            Extraction result dictionary
        """
        try:
            self.logger.info(f"🔧 Attempting data extraction for: {workload_name}")

            tool_info = self.workload_service.get_workload_tool(workload_name)

            if not tool_info:
                self.logger.info(
                    f"📝 No tool found for data extraction: {workload_name}"
                )
                return {"success": False, "error": f"No tool found for {workload_name}"}

            self.logger.info(f"🛠️  Using existing tool: {tool_info['script']}")
            result = self.workload_service.execute_extraction_tool(
                workload_name, input_path
            )

            if result.get("success"):
                self.logger.info(f"✅ Data extraction successful for {workload_name}")
                return result
            else:
                self.logger.warning(f"⚠️  Data extraction failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}

        except Exception as e:
            self.logger.error(f"❌ Error in data extraction: {e}")
            return {"success": False, "error": str(e)}

    def validate_extraction_completeness(
        self, results: StructuredResults, requested_metrics: list[str]
    ) -> bool:
        """Validate that data for all requested metrics was extracted.

        Args:
            results: Parsed results
            requested_metrics: List of requested metrics

        Returns:
            True if all metrics were extracted, False otherwise
        """
        if not results.iterations:
            self.logger.warning("⚠️  No iterations found in results")
            return False

        captured_metrics = set()
        for iteration in results.iterations:
            for instance in iteration.instances:
                for stat in instance.statistics:
                    captured_metrics.add(stat.metricName)

        missing_metrics = set(requested_metrics) - captured_metrics
        if missing_metrics:
            self.logger.warning(f"⚠️  Missing metrics: {missing_metrics}")
            return False

        self.logger.info(f"✅ All requested metrics captured: {list(captured_metrics)}")
        return True

    def get_extracted_metrics(self, results: StructuredResults) -> list[str]:
        """Get list of extracted metrics from results.

        Args:
            results: Parsed results

        Returns:
            List of extracted metric names
        """
        if not results.iterations:
            return []

        extracted_metrics = set()
        for iteration in results.iterations:
            for instance in iteration.instances:
                for stat in instance.statistics:
                    extracted_metrics.add(stat.metricName)

        return sorted(extracted_metrics)

    def analyze_results(
        self, results: StructuredResults, expected_metrics: list[str]
    ) -> dict[str, Any]:
        """Analyze extraction results and return analysis.

        Args:
            results: Parsed results
            expected_metrics: List of expected metrics

        Returns:
            Analysis dictionary
        """
        analysis = {
            "total_iterations": len(results.iterations),
            "total_instances": sum(len(iter.instances) for iter in results.iterations),
            "total_metrics": sum(
                len(inst.statistics)
                for iter in results.iterations
                for inst in iter.instances
            ),
            "extracted_metrics": self.get_extracted_metrics(results),
            "expected_metrics": expected_metrics,
        }

        # Check for missing metrics
        if expected_metrics:
            extracted_metrics = analysis["extracted_metrics"]
            assert isinstance(
                extracted_metrics, list
            ), "extracted_metrics should be a list"
            missing_metrics = set(expected_metrics) - set(extracted_metrics)
            unexpected_metrics = set(extracted_metrics) - set(expected_metrics)

            analysis["missing_metrics"] = list(missing_metrics)
            analysis["unexpected_metrics"] = list(unexpected_metrics)
            analysis["all_expected_found"] = len(missing_metrics) == 0

        return analysis
