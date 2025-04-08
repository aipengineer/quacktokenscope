"""
Output exporters for QuackTokenScope.

This module provides functions for exporting token analysis results
to various formats (Excel, JSON, CSV).
"""

import json

# Remove direct Path use – we now rely on quackcore.fs for file operations.
from quacktokenscope import get_logger
from quacktokenscope.schemas.token_analysis import (
    TokenAnalysis,
    TokenFrequency,
    TokenSummary,
)

logger = get_logger(__name__)

# Import the quackcore.fs service and its utility functions.
from quackcore.fs import service as fs, split_path, join_path


def export_to_json(
    data: TokenAnalysis | TokenFrequency | TokenSummary, output_path
) -> bool:
    """
    Export data to a JSON file.

    Args:
        data: The data to export
        output_path: The path to the output file

    Returns:
        True if the export was successful, False otherwise
    """
    try:
        # Create parent directories if they don't exist.
        # Use fs.split_path and fs.join_path to get the parent directory.
        parent_dir = join_path(*split_path(str(output_path))[:-1])
        fs.create_directory(parent_dir, exist_ok=True)

        # Convert data to a dictionary and dump to a JSON string.
        json_str = json.dumps(data.model_dump(), indent=2)

        # Write the JSON string atomically.
        write_result = fs.write_text(str(output_path), json_str, encoding="utf-8", atomic=True)
        if not write_result.success:
            logger.error(f"Failed to export data to JSON: {write_result.error}")
            return False

        logger.info(f"Exported data to JSON file: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export data to JSON: {e}")
        return False


def export_to_excel(
    analysis: TokenAnalysis,
    frequencies: dict[str, TokenFrequency],
    summary: TokenSummary,
    output_path
) -> bool:
    """
    Export token analysis data to an Excel file with multiple sheets.

    Args:
        analysis: The token analysis data
        frequencies: Dictionary mapping tokenizer names to TokenFrequency objects
        summary: The token analysis summary
        output_path: The path to the output file

    Returns:
        True if the export was successful, False otherwise
    """
    try:
        # Ensure parent directories exist.
        parent_dir = join_path(*split_path(str(output_path))[:-1])
        fs.create_directory(parent_dir, exist_ok=True)

        # Import pandas here to avoid it being a required dependency.
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is required for Excel export. Install with 'pip install pandas'")
            return False

        # Create a Pandas Excel writer.
        with pd.ExcelWriter(str(output_path), engine='openpyxl') as writer:
            # Sheet 1: Token Table
            token_rows = []
            for row in analysis.token_table:
                flat_row = {"token_index": row.token_index}
                for tokenizer, token_data in row.tokenizer_data.items():
                    flat_row[f"{tokenizer}_id"] = token_data.get("id", "")
                    flat_row[f"{tokenizer}_str"] = token_data.get("str", "")
                token_rows.append(flat_row)

            token_df = pd.DataFrame(token_rows)
            token_df.to_excel(writer, sheet_name="Token Table", index=False)

            # Sheet 2: Frequencies
            for tokenizer_name, freq in frequencies.items():
                freq_df = pd.DataFrame(
                    [{"token": k, "count": v} for k, v in freq.frequencies.items()]
                ).sort_values("count", ascending=False)

                if not freq_df.empty:
                    sheet_name = f"{tokenizer_name[:10]} Freq"  # Truncate long names.
                    freq_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Sheet 3: Reverse Mapping & Stats
            stats_data = []
            for tokenizer, stats in analysis.stats.items():
                stats_data.append({
                    "Tokenizer": tokenizer,
                    "Total Tokens": stats.total_tokens,
                    "Unique Tokens": stats.unique_tokens,
                    "Vocab Size": stats.vocab_size,
                    "Avg Token Length": f"{stats.avg_token_length:.2f}",
                    "Reconstruction Score": f"{stats.reconstruction_score:.4f}",
                    "Status": stats.reconstruction_status,
                })

            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name="Stats", index=False)

            # Sheet 4: Summary
            summary_data = {
                "Tokenizer": summary.tokenizers_used,
                "Total Tokens": [summary.total_tokens.get(t, 0) for t in summary.tokenizers_used],
                "Most Common Token": [summary.most_common_token.get(t, ("", 0))[0] for t in summary.tokenizers_used],
                "Most Common Count": [summary.most_common_token.get(t, ("", 0))[1] for t in summary.tokenizers_used],
                "Rarest Token": [summary.rarest_token.get(t, ("", 0))[0] for t in summary.tokenizers_used],
                "Rarest Count": [summary.rarest_token.get(t, ("", 0))[1] for t in summary.tokenizers_used],
            }

            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        logger.info(f"Exported data to Excel file: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export data to Excel: {e}")
        return False


def export_to_csv(
    data: TokenAnalysis | TokenFrequency | TokenSummary, output_path
) -> bool:
    """
    Export data to a CSV file.

    This function tries to flatten the data structure and export it to CSV.
    Some complex structures may not be fully represented in the CSV format.

    Args:
        data: The data to export
        output_path: The path to the output file

    Returns:
        True if the export was successful, False otherwise
    """
    try:
        # Ensure parent directories exist.
        parent_dir = join_path(*split_path(str(output_path))[:-1])
        fs.create_directory(parent_dir, exist_ok=True)

        # Import pandas here to avoid it being a required dependency.
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas is required for CSV export. Install with 'pip install pandas'")
            return False

        # Convert to a DataFrame based on the type.
        if isinstance(data, TokenAnalysis):
            # For TokenAnalysis, export the token table.
            rows = []
            for row in data.token_table:
                flat_row = {"token_index": row.token_index}
                for tokenizer, token_data in row.tokenizer_data.items():
                    flat_row[f"{tokenizer}_id"] = token_data.get("id", "")
                    flat_row[f"{tokenizer}_str"] = token_data.get("str", "")
                rows.append(flat_row)
            df = pd.DataFrame(rows)
        elif isinstance(data, TokenFrequency):
            # For TokenFrequency, export the frequency counts.
            df = pd.DataFrame(
                [{"token": k, "count": v} for k, v in data.frequencies.items()]
            ).sort_values("count", ascending=False)
        elif isinstance(data, TokenSummary):
            # For TokenSummary, create a simple summary table.
            df = pd.DataFrame({
                "tokenizer": data.tokenizers_used,
                "total_tokens": [data.total_tokens.get(t, 0) for t in data.tokenizers_used],
            })
        else:
            # Generic fallback.
            df = pd.DataFrame([data.model_dump()])

        # Write the DataFrame to CSV.
        df.to_csv(str(output_path), index=False)

        logger.info(f"Exported data to CSV file: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export data to CSV: {e}")
        return False


def export_results(
    analysis: TokenAnalysis,
    frequencies: dict[str, TokenFrequency],
    summary: TokenSummary,
    output_dir,
    file_stem: str,
    format_type: str = "excel"
) -> dict[str, str]:
    """
    Export token analysis results to the specified format(s).

    Args:
        analysis: The token analysis data
        frequencies: Dictionary mapping tokenizer names to TokenFrequency objects
        summary: The token analysis summary
        output_dir: The directory to write output files to
        file_stem: The base filename (without extension)
        format_type: The output format ("excel", "json", "csv", or "all")

    Returns:
        Dictionary mapping file types to their paths as strings.
    """
    try:
        # Ensure the output directory exists.
        fs.create_directory(str(output_dir), exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}")
        return {}

    exported_files: dict[str, str] = {}

    # Normalize format type.
    format_type = format_type.lower()
    all_formats = format_type == "all"

    # Export to Excel.
    if all_formats or format_type == "excel":
        excel_path = join_path(str(output_dir), f"{file_stem}.xlsx")
        if export_to_excel(analysis, frequencies, summary, excel_path):
            exported_files["excel"] = str(excel_path)

    # Export to JSON.
    if all_formats or format_type == "json":
        # Export analysis.
        analysis_path = join_path(str(output_dir), f"{file_stem}.json")
        if export_to_json(analysis, analysis_path):
            exported_files["json_analysis"] = str(analysis_path)

        # Export summary.
        summary_path = join_path(str(output_dir), f"{file_stem}_summary.json")
        if export_to_json(summary, summary_path):
            exported_files["json_summary"] = str(summary_path)

        # Export frequencies (one file per tokenizer).
        for tokenizer_name, freq in frequencies.items():
            freq_path = join_path(str(output_dir), f"{file_stem}_{tokenizer_name}_frequency.json")
            if export_to_json(freq, freq_path):
                exported_files[f"json_freq_{tokenizer_name}"] = str(freq_path)

    # Export to CSV.
    if all_formats or format_type == "csv":
        # Export token table.
        table_path = join_path(str(output_dir), f"{file_stem}_token_table.csv")
        if export_to_csv(analysis, table_path):
            exported_files["csv_table"] = str(table_path)

        # Export frequencies (one file per tokenizer).
        for tokenizer_name, freq in frequencies.items():
            freq_path = join_path(str(output_dir), f"{file_stem}_{tokenizer_name}_frequency.csv")
            if export_to_csv(freq, freq_path):
                exported_files[f"csv_freq_{tokenizer_name}"] = str(freq_path)

    return exported_files
