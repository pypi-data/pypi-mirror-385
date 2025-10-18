"""
Simplified pipeline runner for the framework.

This module provides a clean, focused pipeline runner that delegates
execution to the simplified execution engine.

# Depends on:
#   compat
#   execution
#   functions
#   logging
#   models.pipeline
#   models.steps
#   pipeline.models
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from ..compat import DataFrame, SparkSession
from ..execution import ExecutionEngine, ExecutionMode, ExecutionResult
from ..functions import FunctionsProtocol
from ..logging import PipelineLogger
from ..models import BronzeStep, GoldStep, PipelineConfig, PipelineMetrics, SilverStep
from .models import PipelineMode, PipelineReport, PipelineStatus


class SimplePipelineRunner:
    """
    Simplified pipeline runner that delegates to the execution engine.

    This runner focuses on orchestration and reporting, delegating
    actual execution to the simplified ExecutionEngine.
    """

    def __init__(
        self,
        spark: SparkSession,
        config: PipelineConfig,
        bronze_steps: Dict[str, BronzeStep] | None = None,
        silver_steps: Dict[str, SilverStep] | None = None,
        gold_steps: Dict[str, GoldStep] | None = None,
        logger: PipelineLogger | None = None,
        functions: FunctionsProtocol | None = None,
    ):
        """
        Initialize the simplified pipeline runner.

        Args:
            spark: Active SparkSession instance
            config: Pipeline configuration
            bronze_steps: Bronze steps dictionary
            silver_steps: Silver steps dictionary
            gold_steps: Gold steps dictionary
            logger: Optional logger instance
            functions: Optional functions object for PySpark operations
        """
        self.spark = spark
        self.config = config
        self.bronze_steps = bronze_steps or {}
        self.silver_steps = silver_steps or {}
        self.gold_steps = gold_steps or {}
        self.logger = logger or PipelineLogger()
        self.functions = functions
        self.execution_engine = ExecutionEngine(spark, config, self.logger, functions)

    def run_pipeline(
        self,
        steps: list[BronzeStep | SilverStep | GoldStep],
        mode: PipelineMode = PipelineMode.INITIAL,
        bronze_sources: Dict[str, DataFrame] | None = None,
    ) -> PipelineReport:
        """
        Run a complete pipeline.

        Args:
            steps: List of pipeline steps to execute
            mode: Pipeline execution mode
            bronze_sources: Optional bronze source data

        Returns:
            PipelineReport with execution results
        """
        start_time = datetime.now()
        pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Convert PipelineMode to ExecutionMode
        execution_mode = self._convert_mode(mode)

        try:
            self.logger.info(f"Starting pipeline execution: {pipeline_id}")

            # Prepare bronze sources if provided
            if bronze_sources:
                # Add bronze sources to context for execution
                context = {}
                for step in steps:
                    if isinstance(step, BronzeStep) and step.name in bronze_sources:
                        context[step.name] = bronze_sources[step.name]
            else:
                context = {}

            # Execute pipeline using the execution engine
            result = self.execution_engine.execute_pipeline(
                steps, execution_mode, context=context
            )

            # Convert execution result to pipeline report
            report = self._create_pipeline_report(
                pipeline_id=pipeline_id,
                mode=mode,
                start_time=start_time,
                execution_result=result,
            )

            self.logger.info(f"Completed pipeline execution: {pipeline_id}")
            return report

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            return self._create_error_report(
                pipeline_id=pipeline_id, mode=mode, start_time=start_time, error=str(e)
            )

    def run_initial_load(
        self,
        steps: list[BronzeStep | SilverStep | GoldStep] | None = None,
        bronze_sources: Dict[str, DataFrame] | None = None,
    ) -> PipelineReport:
        """Run initial load pipeline."""
        if steps is None:
            # Use stored steps
            steps = (
                list(self.bronze_steps.values())
                + list(self.silver_steps.values())
                + list(self.gold_steps.values())
            )
        return self.run_pipeline(steps, PipelineMode.INITIAL, bronze_sources)

    def run_incremental(
        self,
        steps: list[BronzeStep | SilverStep | GoldStep],
        bronze_sources: Dict[str, DataFrame] | None = None,
    ) -> PipelineReport:
        """Run incremental pipeline."""
        return self.run_pipeline(steps, PipelineMode.INCREMENTAL, bronze_sources)

    def run_full_refresh(
        self,
        steps: list[BronzeStep | SilverStep | GoldStep],
        bronze_sources: Dict[str, DataFrame] | None = None,
    ) -> PipelineReport:
        """Run full refresh pipeline."""
        return self.run_pipeline(steps, PipelineMode.FULL_REFRESH, bronze_sources)

    def run_validation_only(
        self,
        steps: list[BronzeStep | SilverStep | GoldStep],
        bronze_sources: Dict[str, DataFrame] | None = None,
    ) -> PipelineReport:
        """Run validation-only pipeline."""
        return self.run_pipeline(steps, PipelineMode.VALIDATION_ONLY, bronze_sources)

    def _convert_mode(self, mode: PipelineMode) -> ExecutionMode:
        """Convert PipelineMode to ExecutionMode."""
        mode_map = {
            PipelineMode.INITIAL: ExecutionMode.INITIAL,
            PipelineMode.INCREMENTAL: ExecutionMode.INCREMENTAL,
            PipelineMode.FULL_REFRESH: ExecutionMode.FULL_REFRESH,
            PipelineMode.VALIDATION_ONLY: ExecutionMode.VALIDATION_ONLY,
        }
        return mode_map.get(mode, ExecutionMode.INITIAL)

    def _create_pipeline_report(
        self,
        pipeline_id: str,
        mode: PipelineMode,
        start_time: datetime,
        execution_result: ExecutionResult,
    ) -> PipelineReport:
        """Create a pipeline report from execution result."""
        end_time = execution_result.end_time or datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Count successful and failed steps
        steps = execution_result.steps or []
        successful_steps = [s for s in steps if s.status.value == "completed"]
        failed_steps = [s for s in steps if s.status.value == "failed"]

        # Import StepType for layer filtering
        from ..execution import StepType

        # Organize step results by layer (bronze/silver/gold)
        bronze_results = {}
        silver_results = {}
        gold_results = {}

        for step_result in steps:
            step_info = {
                "status": step_result.status.value,
                "duration": step_result.duration,
                "rows_processed": step_result.rows_processed,
                "output_table": step_result.output_table,
                "start_time": step_result.start_time.isoformat(),
                "end_time": step_result.end_time.isoformat() if step_result.end_time else None,
            }

            # Add error if present
            if step_result.error:
                step_info["error"] = step_result.error

            # Add dataframe if available in context (for users who want to access output)
            if hasattr(execution_result, 'context') and execution_result.context:
                if step_result.step_name in execution_result.context:
                    step_info["dataframe"] = execution_result.context[step_result.step_name]

            # Categorize by step type
            if step_result.step_type.value == "bronze":
                bronze_results[step_result.step_name] = step_info
            elif step_result.step_type.value == "silver":
                silver_results[step_result.step_name] = step_info
            elif step_result.step_type.value == "gold":
                gold_results[step_result.step_name] = step_info

        # Aggregate row counts from step results
        total_rows_processed = sum(s.rows_processed or 0 for s in steps)
        # For rows_written, only count Silver/Gold steps (those with output_table)
        total_rows_written = sum(s.rows_processed or 0 for s in steps if s.output_table is not None)

        # Calculate durations by layer
        bronze_duration = sum(s.duration or 0 for s in steps if s.step_type == StepType.BRONZE)
        silver_duration = sum(s.duration or 0 for s in steps if s.step_type == StepType.SILVER)
        gold_duration = sum(s.duration or 0 for s in steps if s.step_type == StepType.GOLD)

        return PipelineReport(
            pipeline_id=pipeline_id,
            execution_id=execution_result.execution_id,
            status=(
                PipelineStatus.COMPLETED
                if execution_result.status == "completed"
                else PipelineStatus.FAILED
            ),
            mode=mode,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            metrics=PipelineMetrics(
                total_steps=len(steps),
                successful_steps=len(successful_steps),
                failed_steps=len(failed_steps),
                total_duration=duration,
                bronze_duration=bronze_duration,
                silver_duration=silver_duration,
                gold_duration=gold_duration,
                total_rows_processed=total_rows_processed,
                total_rows_written=total_rows_written,
                parallel_efficiency=execution_result.parallel_efficiency,
            ),
            bronze_results=bronze_results,
            silver_results=silver_results,
            gold_results=gold_results,
            errors=[s.error for s in failed_steps if s.error],
            warnings=[],
            execution_groups_count=execution_result.execution_groups_count,
            max_group_size=execution_result.max_group_size,
        )

    def _create_error_report(
        self, pipeline_id: str, mode: PipelineMode, start_time: datetime, error: str
    ) -> PipelineReport:
        """Create an error pipeline report."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return PipelineReport(
            pipeline_id=pipeline_id,
            execution_id=f"error_{pipeline_id}",
            status=PipelineStatus.FAILED,
            mode=mode,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            metrics=PipelineMetrics(
                total_steps=0,
                successful_steps=0,
                failed_steps=0,
                total_duration=duration,
            ),
            errors=[error],
            warnings=[],
        )


# Alias for backward compatibility
PipelineRunner = SimplePipelineRunner
