"""ProofOfThought: Main API for Z3-based reasoning."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import traceback
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from z3adapter.reasoning.program_generator import Z3ProgramGenerator

if TYPE_CHECKING:
    from z3adapter.backends.abstract import Backend
    from z3adapter.postprocessors.abstract import Postprocessor

logger = logging.getLogger(__name__)

BackendType = Literal["json", "smt2"]


@dataclass
class QueryResult:
    """Result of a reasoning query."""

    question: str
    answer: bool | None
    json_program: dict[str, Any] | None
    sat_count: int
    unsat_count: int
    output: str
    success: bool
    num_attempts: int
    error: str | None = None


class ProofOfThought:
    """High-level API for Z3-based reasoning.

    Provides a simple interface that hides the complexity of:
    - JSON DSL program generation
    - Z3 solver execution
    - Result parsing and interpretation

    Example:
        >>> from openai import OpenAI
        >>> client = OpenAI(api_key="...")
        >>> pot = ProofOfThought(llm_client=client)
        >>> result = pot.query("Would Nancy Pelosi publicly denounce abortion?")
        >>> print(result.answer)  # False
    """

    def __init__(
        self,
        llm_client: Any,
        model: str = "gpt-5",
        backend: BackendType = "smt2",
        max_attempts: int = 3,
        verify_timeout: int = 10000,
        optimize_timeout: int = 100000,
        cache_dir: str | None = None,
        z3_path: str = "z3",
        postprocessors: Sequence[str | Postprocessor] | None = None,
        postprocessor_configs: dict[str, dict] | None = None,
    ) -> None:
        """Initialize ProofOfThought.

        Args:
            llm_client: LLM client (OpenAI, AzureOpenAI, Anthropic, etc.)
            model: LLM model/deployment name (default: "gpt-5")
            backend: Execution backend ("json" or "smt2", default: "smt2")
            max_attempts: Maximum retry attempts for program generation
            verify_timeout: Z3 verification timeout in milliseconds
            optimize_timeout: Z3 optimization timeout in milliseconds
            cache_dir: Directory to cache generated programs (None = temp dir)
            z3_path: Path to Z3 executable (for SMT2 backend)
            postprocessors: List of postprocessor names or instances to apply
            postprocessor_configs: Configuration for postprocessors (if names provided)

        Example with postprocessors:
            >>> pot = ProofOfThought(
            ...     llm_client=client,
            ...     postprocessors=["self_refine", "self_consistency"],
            ...     postprocessor_configs={"self_refine": {"num_iterations": 3}}
            ... )
        """
        self.backend_type = backend
        self.llm_client = llm_client
        self.generator = Z3ProgramGenerator(llm_client=llm_client, model=model, backend=backend)

        # Initialize appropriate backend (import here to avoid circular imports)
        if backend == "json":
            from z3adapter.backends.json_backend import JSONBackend

            backend_instance: Backend = JSONBackend(
                verify_timeout=verify_timeout, optimize_timeout=optimize_timeout
            )
        else:  # smt2
            from z3adapter.backends.smt2_backend import SMT2Backend

            backend_instance = SMT2Backend(verify_timeout=verify_timeout, z3_path=z3_path)

        self.backend = backend_instance

        self.max_attempts = max_attempts
        self.cache_dir = cache_dir or tempfile.gettempdir()

        # Create cache directory if needed
        os.makedirs(self.cache_dir, exist_ok=True)

        # Initialize postprocessors
        self.postprocessors: list[Postprocessor] = []
        if postprocessors:
            self.postprocessors = self._initialize_postprocessors(
                postprocessors, postprocessor_configs or {}
            )
            logger.info(f"Initialized {len(self.postprocessors)} postprocessors")

    def _initialize_postprocessors(
        self,
        postprocessors: Sequence[str | Postprocessor],
        configs: dict[str, dict],
    ) -> list[Postprocessor]:
        """Initialize postprocessor instances from names or objects.

        Args:
            postprocessors: List of postprocessor names or instances
            configs: Configuration dict for postprocessors

        Returns:
            List of postprocessor instances
        """
        from z3adapter.postprocessors.abstract import Postprocessor
        from z3adapter.postprocessors.registry import PostprocessorRegistry

        initialized = []
        for item in postprocessors:
            if isinstance(item, str):
                # Create from registry
                config = configs.get(item, {})
                postprocessor = PostprocessorRegistry.get(item, **config)
                initialized.append(postprocessor)
            elif isinstance(item, Postprocessor):
                # Already an instance
                initialized.append(item)
            else:
                logger.warning(f"Invalid postprocessor: {item}, skipping")

        return initialized

    def query(
        self,
        question: str,
        temperature: float = 0.1,
        max_tokens: int = 16384,
        save_program: bool = False,
        program_path: str | None = None,
        enable_postprocessing: bool = True,
    ) -> QueryResult:
        """Answer a reasoning question using Z3 theorem proving.

        Args:
            question: Natural language question to answer
            temperature: LLM temperature for program generation
            max_tokens: Maximum tokens for LLM response (default 16384 for GPT-5)
            save_program: Whether to save generated JSON program
            program_path: Path to save program (None = auto-generate)
            enable_postprocessing: Whether to apply postprocessors (if configured)

        Returns:
            QueryResult with answer and execution details
        """
        logger.info(f"Processing question: {question}")

        previous_response: str | None = None
        error_trace: str | None = None

        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"Attempt {attempt}/{self.max_attempts}")

            try:
                # Generate or regenerate program
                if attempt == 1:
                    gen_result = self.generator.generate(
                        question=question,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                else:
                    gen_result = self.generator.generate_with_feedback(
                        question=question,
                        error_trace=error_trace or "",
                        previous_response=previous_response or "",
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                if not gen_result.success or gen_result.program is None:
                    error_trace = (
                        gen_result.error or f"Failed to generate {self.backend_type} program"
                    )
                    previous_response = gen_result.raw_response
                    logger.warning(f"Generation failed: {error_trace}")
                    continue

                # Save program to temporary file
                file_extension = self.backend.get_file_extension()
                if program_path is None:
                    temp_file = tempfile.NamedTemporaryFile(
                        mode="w",
                        suffix=file_extension,
                        dir=self.cache_dir,
                        delete=not save_program,
                    )
                    program_file_path = temp_file.name
                else:
                    program_file_path = program_path

                # Write program to file (format depends on backend)
                with open(program_file_path, "w") as f:
                    if self.backend_type == "json":
                        json.dump(gen_result.program, f, indent=2)
                    else:  # smt2
                        f.write(gen_result.program)  # type: ignore

                logger.info(f"Generated program saved to: {program_file_path}")

                # Execute via backend
                verify_result = self.backend.execute(program_file_path)

                if not verify_result.success:
                    error_trace = verify_result.error or "Z3 verification failed"
                    previous_response = gen_result.raw_response
                    logger.warning(f"Verification failed: {error_trace}")
                    continue

                # Check if we got a definitive answer
                if verify_result.answer is None:
                    error_trace = (
                        f"Ambiguous verification result: "
                        f"SAT={verify_result.sat_count}, UNSAT={verify_result.unsat_count}\n"
                        f"Output:\n{verify_result.output}"
                    )
                    previous_response = gen_result.raw_response
                    logger.warning(f"Ambiguous result: {error_trace}")
                    continue

                # Success!
                logger.info(
                    f"Successfully answered question on attempt {attempt}: {verify_result.answer}"
                )
                initial_result = QueryResult(
                    question=question,
                    answer=verify_result.answer,
                    json_program=gen_result.json_program,  # For backward compatibility
                    sat_count=verify_result.sat_count,
                    unsat_count=verify_result.unsat_count,
                    output=verify_result.output,
                    success=True,
                    num_attempts=attempt,
                )

                # Apply postprocessors if enabled
                if enable_postprocessing and self.postprocessors:
                    logger.info(
                        f"Applying {len(self.postprocessors)} postprocessors to improve result"
                    )
                    return self._apply_postprocessors(
                        question=question,
                        initial_result=initial_result,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                return initial_result

            except Exception as e:
                error_trace = f"Error: {str(e)}\n{traceback.format_exc()}"
                logger.error(f"Exception on attempt {attempt}: {error_trace}")
                if "gen_result" in locals():
                    previous_response = gen_result.raw_response

        # All attempts failed
        logger.error(f"Failed to answer question after {self.max_attempts} attempts")
        return QueryResult(
            question=question,
            answer=None,
            json_program=None,
            sat_count=0,
            unsat_count=0,
            output="",
            success=False,
            num_attempts=self.max_attempts,
            error=f"Failed after {self.max_attempts} attempts. Last error: {error_trace}",
        )

    def _apply_postprocessors(
        self,
        question: str,
        initial_result: QueryResult,
        temperature: float,
        max_tokens: int,
    ) -> QueryResult:
        """Apply all configured postprocessors to improve the result.

        Args:
            question: Original question
            initial_result: Initial QueryResult
            temperature: LLM temperature
            max_tokens: Max tokens

        Returns:
            Enhanced QueryResult after applying all postprocessors
        """
        current_result = initial_result

        for postprocessor in self.postprocessors:
            logger.info(f"Applying postprocessor: {postprocessor.name}")

            try:
                enhanced_result = postprocessor.process(
                    question=question,
                    initial_result=current_result,
                    generator=self.generator,
                    backend=self.backend,
                    llm_client=self.llm_client,
                    cache_dir=self.cache_dir,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                if enhanced_result.success:
                    logger.info(
                        f"Postprocessor {postprocessor.name} completed. "
                        f"Answer: {enhanced_result.answer}"
                    )
                    current_result = enhanced_result
                else:
                    logger.warning(
                        f"Postprocessor {postprocessor.name} failed, keeping previous result"
                    )

            except Exception as e:
                logger.error(f"Error in postprocessor {postprocessor.name}: {e}")
                # Continue with current result if postprocessor fails

        return current_result
