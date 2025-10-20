"""
PL/SQL Engine
Main interface for PL/SQL execution in EzDB
"""

from typing import Any, Dict, Optional
from .parser import PLSQLParser
from .executor import PLSQLExecutor


class PLSQLEngine:
    """
    Complete PL/SQL engine for EzDB
    Parses and executes PL/SQL code
    """

    def __init__(self, rdbms_engine=None):
        """
        Initialize PL/SQL engine

        Args:
            rdbms_engine: RDBMSEngine instance for SQL execution
        """
        self.parser = PLSQLParser()
        self.executor = PLSQLExecutor(rdbms_engine)
        self.rdbms_engine = rdbms_engine

    def execute(self, plsql_code: str) -> Dict[str, Any]:
        """
        Execute PL/SQL code

        Args:
            plsql_code: PL/SQL source code

        Returns:
            Dict with status, output, and results
        """
        try:
            # Parse
            ast = self.parser.parse(plsql_code)

            # Execute
            result = self.executor.execute(ast)

            return result

        except SyntaxError as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': 'SyntaxError',
                'phase': 'parsing'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'phase': 'execution'
            }

    def execute_with_output(self, plsql_code: str) -> str:
        """
        Execute PL/SQL code and return formatted output

        Args:
            plsql_code: PL/SQL source code

        Returns:
            Formatted output string
        """
        result = self.execute(plsql_code)

        if result['status'] == 'success':
            output_lines = result.get('output', [])
            if output_lines:
                return '\n'.join(output_lines)
            else:
                return 'PL/SQL block executed successfully (no output)'
        else:
            error_type = result.get('error_type', 'Error')
            error_msg = result.get('error', 'Unknown error')
            phase = result.get('phase', 'unknown')
            return f'{error_type} during {phase}: {error_msg}'
