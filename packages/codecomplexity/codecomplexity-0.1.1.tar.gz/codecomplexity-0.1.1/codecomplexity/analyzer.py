"""
codecomplexity - A Python library for analyzing code complexity metrics
"""

import ast
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ComplexityMetrics:
    """Container for complexity metrics of a code unit"""
    name: str
    type: str  # 'function', 'class', 'module'
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    nesting_depth: int
    parameters: int
    returns: int
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'type': self.type,
            'lines_of_code': self.lines_of_code,
            'cyclomatic_complexity': self.cyclomatic_complexity,
            'cognitive_complexity': self.cognitive_complexity,
            'nesting_depth': self.nesting_depth,
            'parameters': self.parameters,
            'returns': self.returns
        }


class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyzes Python code complexity using AST traversal"""
    
    def __init__(self):
        self.results: List[ComplexityMetrics] = []
        self.current_function = None
        self.current_class = None
        
    def analyze(self, code: str, filename: str = '<string>') -> List[ComplexityMetrics]:
        """Analyze Python code and return complexity metrics"""
        try:
            tree = ast.parse(code, filename=filename)
            self.visit(tree)
            return self.results
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definition and calculate complexity"""
        metrics = self._calculate_function_metrics(node)
        self.results.append(metrics)
        
        old_function = self.current_function
        self.current_function = node
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definition"""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definition"""
        old_class = self.current_class
        self.current_class = node
        self.generic_visit(node)
        self.current_class = old_class
    
    def _calculate_function_metrics(self, node: ast.FunctionDef) -> ComplexityMetrics:
        """Calculate all metrics for a function"""
        name = node.name
        if self.current_class:
            name = f"{self.current_class.name}.{name}"
        
        return ComplexityMetrics(
            name=name,
            type='function',
            lines_of_code=self._count_lines(node),
            cyclomatic_complexity=self._cyclomatic_complexity(node),
            cognitive_complexity=self._cognitive_complexity(node),
            nesting_depth=self._max_nesting_depth(node),
            parameters=len(node.args.args),
            returns=self._count_returns(node)
        )
    
    def _count_lines(self, node: ast.AST) -> int:
        """Count lines of code (excluding blank lines and comments)"""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 0
    
    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity (number of decision points + 1)"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler,)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                complexity += len(child.ifs)
        
        return complexity
    
    def _cognitive_complexity(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate cognitive complexity (weighted by nesting)"""
        complexity = 0
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try)):
                complexity += 1 + depth
                complexity += self._cognitive_complexity(child, depth + 1)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler,)):
                # The ExceptHandler itself also adds complexity
                complexity += 1 + depth 
                complexity += self._cognitive_complexity(child, depth + 1)
            else:
                complexity += self._cognitive_complexity(child, depth)
                
        return complexity
    
    def _max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                 ast.With, ast.AsyncWith, ast.Try)):
                depth = self._max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
            else:
                depth = self._max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _count_returns(self, node: ast.AST) -> int:
        """Count return statements"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                count += 1
        return count


def analyze_file(filepath: str) -> List[ComplexityMetrics]:
    """Analyze a Python file and return complexity metrics"""
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    analyzer = ComplexityAnalyzer()
    return analyzer.analyze(code, filename=filepath)


def analyze_code(code: str) -> List[ComplexityMetrics]:
    """Analyze Python code string and return complexity metrics"""
    analyzer = ComplexityAnalyzer()
    return analyzer.analyze(code)


def format_report(metrics: List[ComplexityMetrics], threshold: Optional[int] = None) -> str:
    """Format complexity metrics into a readable report"""
    if not metrics:
        return "No functions found to analyze."
    
    report = []
    report.append("Code Complexity Analysis Report")
    report.append("=" * 80)
    report.append("")
    
    for m in metrics:
        if threshold and m.cyclomatic_complexity < threshold:
            continue
            
        report.append(f"Function: {m.name}")
        report.append(f"  Lines of Code: {m.lines_of_code}")
        report.append(f"  Cyclomatic Complexity: {m.cyclomatic_complexity}")
        report.append(f"  Cognitive Complexity: {m.cognitive_complexity}")
        report.append(f"  Max Nesting Depth: {m.nesting_depth}")
        report.append(f"  Parameters: {m.parameters}")
        report.append(f"  Return Statements: {m.returns}")
        report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    sample_code = """
def complex_function(a, b, c):
    if a > 0:
        for i in range(10):
            if b > i:
                while c > 0:
                    c -= 1
                    if c % 2 == 0:
                        return c
    return 0

def simple_function(x):
    return x * 2
"""
    
    metrics = analyze_code(sample_code)
    print(format_report(metrics))