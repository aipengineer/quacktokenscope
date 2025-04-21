# src/quacktokenscope/plugins/token_scope.py
"""
QuackTokenScope plugin for token analysis.

This module implements the token analysis plugin that integrates with QuackCore
to analyze text files using different tokenizers, compare their outputs, and
optionally upload results to Google Drive.
"""

import logging
import os
from typing import Any

from quackcore.integrations.core.results import IntegrationResult
from quackcore.integrations.google.drive import GoogleDriveService

from quackcore.logging import get_logger
from quacktokenscope.outputs.exporter import export_results
from quacktokenscope.protocols import QuackToolPluginProtocol
from quacktokenscope.schemas.token_analysis import (
    TokenAnalysis,
    TokenFrequency,
    TokenizerStats,
    TokenRow,
    TokenSummary,
)
from quacktokenscope.utils.frequency import analyze_token_frequency
from quacktokenscope.utils.reverse_mapping import evaluate_reconstruction
from quacktokenscope.utils.tokenizers import TOKENIZER_REGISTRY, BaseTokenizer

# Import the FS service and helper functions from quackcore.fs
from quackcore.fs.service import get_service

fs = get_service()

logger = get_logger(__name__)


class TokenScopePluginError(Exception):
    """Exception raised for errors in the TokenScopePlugin."""
    pass


class TokenScopePlugin(QuackToolPluginProtocol):
    """
    Plugin for analyzing text using different tokenizers.

    This plugin can:
    1. Download a text file from Google Drive
    2. Tokenize the text using multiple tokenizers
    3. Compare tokenization results
    4. Analyze token frequencies
    5. Check reconstruction fidelity
    6. Export results to various formats
    7. Upload results back to Google Drive
    """

    def __init__(self) -> None:
        """Initialize the token scope plugin."""
        self._logger = get_logger(__name__)
        self._drive_service = None
        self._initialized = False
        # Use the FS utility to create a temporary directory
        self._temp_dir = fs.create_temp_directory(prefix="quacktokenscope_")
        # Initialize output directory using FS; store as string.
        output_result = fs.create_directory("output", exist_ok=True)
        self._output_dir = str(output_result.path) if output_result.success else "output"
        self._tokenizers: dict[str, BaseTokenizer] = {}

    @property
    def logger(self) -> logging.Logger:
        """Get the logger for the plugin."""
        return self._logger

    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return "tokenscope"

    @property
    def version(self) -> str:
        """Get the version of the plugin."""
        return "0.1.0"

    def initialize(self) -> IntegrationResult:
        """
        Initialize the plugin and its dependencies.

        Returns:
            IntegrationResult indicating success or failure
        """
        if self._initialized:
            return IntegrationResult.success_result(
                message="TokenScopePlugin already initialized"
            )

        try:
            # Initialize environment from config
            self._initialize_environment()

            # Initialize Google Drive integration
            try:
                self._drive_service = GoogleDriveService()
                drive_result = self._drive_service.initialize()
                if not drive_result.success:
                    self.logger.warning(
                        f"Google Drive integration not available: {drive_result.error}"
                    )
                    self.logger.info(
                        "QuackTokenScope will continue without Google Drive functionality"
                    )
                    self._drive_service = None
            except Exception as e:
                self.logger.warning(f"Failed to initialize Google Drive: {e}")
                self.logger.info(
                    "QuackTokenScope will continue without Google Drive functionality"
                )
                self._drive_service = None

            # Initialize tokenizers
            tokenizers_to_load = ["tiktoken", "huggingface", "sentencepiece"]

            # Check if we should use mock tokenizers
            from quacktokenscope.config import get_tool_config
            config = get_tool_config()
            use_mock = config.get("use_mock_tokenizers", False)

            if use_mock:
                self.logger.warning("Using mock tokenizers for testing purposes")
                self._tokenizers["mock"] = TOKENIZER_REGISTRY["mock"]()
                self._tokenizers["mock"].initialize()
            else:
                # Try to initialize each tokenizer
                for tokenizer_name in tokenizers_to_load:
                    try:
                        if tokenizer_name in TOKENIZER_REGISTRY:
                            tokenizer_cls = TOKENIZER_REGISTRY[tokenizer_name]
                            tokenizer = tokenizer_cls()
                            if tokenizer.initialize():
                                self._tokenizers[tokenizer_name] = tokenizer
                                self.logger.info(
                                    f"Initialized {tokenizer_name} tokenizer"
                                )
                            else:
                                self.logger.warning(
                                    f"Failed to initialize {tokenizer_name} tokenizer"
                                )
                        else:
                            self.logger.warning(f"Unknown tokenizer: {tokenizer_name}")
                    except Exception as e:
                        self.logger.exception(
                            f"Error initializing {tokenizer_name} tokenizer: {e}"
                        )

            # If no tokenizers were initialized, fall back to the mock tokenizer
            if not self._tokenizers:
                self.logger.warning(
                    "No tokenizers could be initialized, falling back to mock tokenizer"
                )
                self._tokenizers["mock"] = TOKENIZER_REGISTRY["mock"]()
                self._tokenizers["mock"].initialize()

            self._initialized = True
            return IntegrationResult.success_result(
                message="TokenScopePlugin initialized successfully"
            )

        except Exception as e:
            self.logger.exception("Failed to initialize TokenScopePlugin")
            return IntegrationResult.error_result(
                f"Failed to initialize TokenScopePlugin: {str(e)}"
            )

    def _initialize_environment(self) -> None:
        """
        Initialize environment variables from configuration.
        """
        try:
            # Import quacktokenscope's environment initialization
            from quacktokenscope import initialize
            initialize()
        except Exception as e:
            self.logger.warning(f"Failed to initialize environment: {e}")

    def is_available(self) -> bool:
        """
        Check if the plugin is available.

        Returns:
            True if the plugin is available, False otherwise
        """
        return self._initialized

    def process_file(
        self,
        file_path: str,
        output_path: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> IntegrationResult:
        """
        Process a file using the token scope plugin.

        Args:
            file_path: Path to the file to process (local path or Google Drive ID)
            output_path: Optional path for the output directory
            options: Optional processing options
                - tokenizers: List of tokenizers to use (default: all available)
                - output_format: Output format (excel, json, csv, all)
                - limit: Maximum number of characters to process
                - upload: Whether to upload results to Google Drive
                - dry_run: Don't upload results to Google Drive (default: False)
                - verbose: Print detailed processing information (default: False)
                - same_dir: Output results in the same directory as input file (default: False)

        Returns:
            IntegrationResult containing the token analysis result
        """
        if not self._initialized:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        options = options or {}

        try:
            # Check if the file_path is a Google Drive ID.
            # Use a simple check since Drive IDs generally lack path separators.
            is_drive_id = not os.path.exists(file_path) and "/" not in file_path and "\\" not in file_path

            if is_drive_id and 25 <= len(file_path) <= 40:
                if self._drive_service:
                    file_result = self._process_drive_file(file_path, output_path, options)
                else:
                    auth_url = "https://developers.google.com/drive/api/quickstart/python"
                    return IntegrationResult.error_result(
                        f"The file path appears to be a Google Drive ID, but Google Drive integration is not available. "
                        f"To use Google Drive features, please follow the setup instructions at {auth_url}"
                    )
            else:
                file_result = self._process_local_file(file_path, output_path, options)

            return file_result

        except Exception as e:
            self.logger.exception(f"Failed to process file: {e}")
            return IntegrationResult.error_result(f"Failed to process file: {str(e)}")

    def _process_drive_file(
        self,
        file_id: str,
        output_path: str | None,
        options: dict[str, Any],
    ) -> IntegrationResult:
        """
        Process a file from Google Drive.

        Args:
            file_id: Google Drive file ID
            output_path: Optional path for the output directory
            options: Processing options

        Returns:
            IntegrationResult containing the token analysis result
        """
        if not self._drive_service:
            auth_url = "https://developers.google.com/drive/api/quickstart/python"
            self.logger.error(
                "Google Drive integration is not available. Configure credentials in quack_config.yaml."
            )
            return IntegrationResult.error_result(
                f"Google Drive integration is not available. To use Google Drive features, please follow the setup instructions at {auth_url}"
            )

        self.logger.info(f"Downloading file from Google Drive with ID: {file_id}")

        download_result = self._drive_service.download_file(
            remote_id=file_id,
            local_path=self._temp_dir,
        )

        if not download_result.success:
            return IntegrationResult.error_result(
                f"Failed to download file from Google Drive: {download_result.error}"
            )

        local_path = download_result.content
        self.logger.info(f"Downloaded file to: {local_path}")

        file_info_result = self._drive_service.get_file_info(remote_id=file_id)
        if not file_info_result.success:
            return IntegrationResult.error_result(
                f"Failed to get file info from Google Drive: {file_info_result.error}"
            )

        file_info = file_info_result.content
        file_name = file_info.get("name", "unknown")

        result = self._process_local_file(local_path, output_path, options)

        if result.success and options.get("upload", True) and not options.get("dry_run", False) and self._drive_service:
            exported_files = result.content.get("exported_files", {})

            parent_id = file_info.get("parents", [None])[0]

            drive_files = {}
            for file_type, file_path in exported_files.items():
                upload_result = self._drive_service.upload_file(
                    file_path=str(file_path),
                    parent_folder_id=parent_id,
                )

                if upload_result.success:
                    drive_files[file_type] = upload_result.content
                    self.logger.info(
                        f"Uploaded {file_type} file to Google Drive with ID: {upload_result.content}"
                    )
                else:
                    self.logger.error(
                        f"Failed to upload {file_type} file to Google Drive: {upload_result.error}"
                    )

            result.content["drive_files"] = drive_files

        if result.success:
            result.content["original_file_name"] = file_name

        return result

    def _process_local_file(
            self,
            file_path: str,
            output_path: str | None,
            options: dict[str, Any],
    ) -> IntegrationResult:
        """
        Process a local file.

        Args:
            file_path: Path to the local file
            output_path: Optional path for the output directory
            options: Processing options

        Returns:
            IntegrationResult containing the token analysis result
        """
        file_info = fs.get_file_info(file_path)
        if not file_info.success or not file_info.exists:
            return IntegrationResult.error_result(f"File not found: {file_path}")
        if not file_info.is_file:
            return IntegrationResult.error_result(f"Not a file: {file_path}")

        try:
            self.logger.info(f"Reading file: {file_path}")
            read_result = fs.read_text(file_path, encoding="utf-8")
            if not read_result.success:
                return IntegrationResult.error_result(
                    f"Failed to read file: {read_result.error}")
            content = read_result.content

            char_limit = options.get("limit")
            if char_limit and isinstance(char_limit, int) and char_limit > 0:
                original_length = len(content)
                content = content[:char_limit]
                self.logger.info(
                    f"Limited content from {original_length} to {len(content)} characters"
                )

            tokenizer_names = options.get("tokenizers")
            if tokenizer_names:
                if isinstance(tokenizer_names, str):
                    tokenizer_names = [name.strip() for name in
                                       tokenizer_names.split(",")]
                tokenizers = {
                    name: tokenizer for name, tokenizer in self._tokenizers.items()
                    if name in tokenizer_names
                }
                if not tokenizers:
                    self.logger.warning(
                        f"None of the specified tokenizers are available: {tokenizer_names}"
                    )
                    tokenizers = self._tokenizers
            else:
                tokenizers = self._tokenizers

            self.logger.info(f"Using tokenizers: {', '.join(tokenizers.keys())}")

            analysis_result = self._analyze_file(
                content=content,
                tokenizers=tokenizers,
                filename=file_info.path.name,  # using the file name from fs result
                options=options,
            )

            # Compute stem from the file name unconditionally.
            parts = fs.split_path(file_path)
            file_name = parts[-1]
            stem = file_name.rsplit('.', 1)[0]

            # Determine output directory.
            if output_path:
                out_dir = output_path
            elif options.get("same_dir", False):
                parent_dir = fs.join_path(*parts[:-1])
                out_dir = fs.join_path(parent_dir, f"{stem}_tokenscope")
            else:
                out_dir = fs.join_path(self._output_dir, stem)

            # Ensure the output directory exists.
            fs.create_directory(out_dir, exist_ok=True)

            exported_files = export_results(
                analysis=analysis_result["analysis"],
                frequencies=analysis_result["frequencies"],
                summary=analysis_result["summary"],
                output_dir=out_dir,
                file_stem=stem,
                format_type=options.get("output_format", "excel"),
            )

            verbose = options.get("verbose", False)

            if verbose:
                return IntegrationResult.success_result(
                    content={
                        "analysis": analysis_result["analysis"].model_dump(),
                        "summary": analysis_result["summary"].model_dump(),
                        "exported_files": exported_files,
                        "tokenizers_used": list(tokenizers.keys()),
                    },
                    message=f"Successfully analyzed {file_info.path.name} using {len(tokenizers)} tokenizers"
                )
            else:
                return IntegrationResult.success_result(
                    content={
                        "summary": analysis_result["summary"].model_dump(),
                        "exported_files": exported_files,
                        "tokenizers_used": list(tokenizers.keys()),
                    },
                    message=f"Successfully analyzed {file_info.path.name} using {len(tokenizers)} tokenizers"
                )

        except Exception as e:
            self.logger.exception(f"Failed to process local file: {e}")
            return IntegrationResult.error_result(f"Failed to process file: {str(e)}")

    def _analyze_file(
        self,
        content: str,
        tokenizers: dict[str, BaseTokenizer],
        filename: str,
        options: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze a file using multiple tokenizers.

        Args:
            content: The file content
            tokenizers: Dictionary mapping tokenizer names to instances
            filename: Name of the file being analyzed
            options: Processing options

        Returns:
            Dictionary containing analysis results
        """
        self.logger.info(f"Analyzing file {filename} with {len(tokenizers)} tokenizers")

        total_tokens: dict[str, int] = {}
        token_tables: list[TokenRow] = []
        tokenizer_stats: dict[str, TokenizerStats] = {}
        frequencies: dict[str, TokenFrequency] = {}

        most_common_tokens: dict[str, tuple[str, int]] = {}
        rarest_tokens: dict[str, tuple[str, int]] = {}

        max_index = 0

        for tokenizer_name, tokenizer in tokenizers.items():
            self.logger.info(f"Tokenizing with {tokenizer_name}")
            token_ids, token_strs = tokenizer.tokenize(content)
            total_tokens[tokenizer_name] = len(token_ids)
            unique_tokens = len(set(token_ids))
            avg_token_length = (
                sum(len(t) for t in token_strs) / len(token_strs) if token_strs else 0
            )
            max_index = max(max_index, len(token_ids))

            freq_result, most_common, rarest = analyze_token_frequency(
                tokenizer=tokenizer,
                text=content,
                filename=filename,
            )

            frequencies[tokenizer_name] = freq_result
            most_common_tokens[tokenizer_name] = most_common
            rarest_tokens[tokenizer_name] = rarest

            reconstructed, similarity, status = evaluate_reconstruction(
                tokenizer=tokenizer,
                text=content,
            )

            stats = TokenizerStats(
                name=tokenizer_name,
                total_tokens=len(token_ids),
                unique_tokens=unique_tokens,
                vocab_size=tokenizer.get_vocab_size(),
                avg_token_length=avg_token_length,
                reconstruction_score=similarity,
                reconstruction_status=status,
            )

            tokenizer_stats[tokenizer_name] = stats

            for i in range(len(token_ids)):
                if i >= len(token_tables):
                    token_tables.append(TokenRow(token_index=i, tokenizer_data={}))
                token_tables[i].tokenizer_data[tokenizer_name] = {
                    "id": token_ids[i],
                    "str": token_strs[i],
                }

        best_match = max(tokenizer_stats.items(), key=lambda x: x[1].reconstruction_score)[0]

        analysis = TokenAnalysis(
            filename=filename,
            tokenizers_used=list(tokenizers.keys()),
            stats=tokenizer_stats,
            token_table=token_tables,
            best_match=best_match,
        )

        summary = TokenSummary(
            filename=filename,
            tokenizers_used=list(tokenizers.keys()),
            total_tokens=total_tokens,
            best_match=best_match,
            most_common_token=most_common_tokens,
            rarest_token=rarest_tokens,
        )

        return {
            "analysis": analysis,
            "frequencies": frequencies,
            "summary": summary,
        }
