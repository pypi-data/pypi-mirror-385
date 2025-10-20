"""
Command-line interface for codecomplexity
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List
from codecomplexity.analyzer import analyze_file, format_report, ComplexityMetrics


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze Python code complexity metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codecomplexity script.py
  codecomplexity src/ --recursive
  codecomplexity script.py --threshold 10
  codecomplexity script.py --format json
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="codecomplexity 0.1.1"
    )
    
    parser.add_argument(
        "path",
        help="Python file or directory to analyze"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively analyze all Python files in directory"
    )
    
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=None,
        help="Only show functions with cyclomatic complexity above threshold"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Collect files to analyze
    path = Path(args.path)
    files = []
    
    if path.is_file():
        if path.suffix == ".py":
            files.append(path)
        else:
            print(f"Error: {path} is not a Python file", file=sys.stderr)
            sys.exit(1)
    elif path.is_dir():
        if args.recursive:
            files = list(path.rglob("*.py"))
        else:
            files = list(path.glob("*.py"))
        
        if not files:
            print(f"No Python files found in {path}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Analyze files
    all_metrics: List[ComplexityMetrics] = []
    errors = []
    
    for file in files:
        try:
            metrics = analyze_file(str(file))
            for m in metrics:
                # Add file info to function name for multi-file analysis
                if len(files) > 1:
                    m.name = f"{file.name}::{m.name}"
            all_metrics.extend(metrics)
        except Exception as e:
            errors.append(f"{file}: {str(e)}")
    
    # Format output
    if args.format == "json":
        output = json.dumps(
            {
                "files_analyzed": len(files),
                "functions_found": len(all_metrics),
                "metrics": [m.to_dict() for m in all_metrics],
                "errors": errors
            },
            indent=2
        )
    else:
        if len(files) > 1:
            header = f"Analyzed {len(files)} files, found {len(all_metrics)} functions\n\n"
        else:
            header = ""
        
        output = header + format_report(all_metrics, threshold=args.threshold)
        
        if errors:
            output += "\n\nErrors:\n"
            output += "\n".join(f"  - {e}" for e in errors)
    
    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
    
    # Exit with error code if high complexity found
    if args.threshold:
        high_complexity = [m for m in all_metrics if m.cyclomatic_complexity > args.threshold]
        if high_complexity:
            sys.exit(1)


if __name__ == "__main__":
    main()