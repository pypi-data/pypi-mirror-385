"""
Simple SQL parser for EzDB metadata queries.
Supports basic SELECT, WHERE, ORDER BY, and LIMIT clauses.
"""

import re
from typing import Dict, List, Any, Optional, Tuple


class SQLParser:
    """Parse SQL-like queries for EzDB metadata operations."""

    def __init__(self):
        self.query = ""
        self.collection = ""
        self.columns = []
        self.where_conditions = {}
        self.order_by = None
        self.limit = None
        self.offset = 0

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a SQL query string and return structured query information.

        Supported syntax:
        - SELECT * FROM collection_name
        - SELECT column1, column2 FROM collection_name
        - SELECT * FROM collection_name WHERE column = 'value'
        - SELECT * FROM collection_name WHERE column > 10 AND column2 = 'test'
        - SELECT * FROM collection_name ORDER BY column ASC/DESC
        - SELECT * FROM collection_name LIMIT 10
        - SELECT * FROM collection_name OFFSET 5 LIMIT 10

        Supported WHERE operators:
        - = (equals)
        - != or <> (not equals)
        - > (greater than)
        - >= (greater than or equal)
        - < (less than)
        - <= (less than or equal)
        - LIKE (string pattern matching, use % as wildcard)
        - IN (value in list)
        """
        self.query = query.strip()

        # Convert to uppercase for parsing, but preserve original values
        query_upper = self.query.upper()

        # Extract collection name from FROM clause
        from_match = re.search(r'FROM\s+(\w+)', query_upper)
        if not from_match:
            raise ValueError("Missing FROM clause. Syntax: SELECT * FROM collection_name")

        self.collection = re.search(r'FROM\s+(\w+)', self.query, re.IGNORECASE).group(1)

        # Extract columns from SELECT clause
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM', self.query, re.IGNORECASE)
        if not select_match:
            raise ValueError("Missing SELECT clause. Syntax: SELECT * FROM collection_name")

        columns_str = select_match.group(1).strip()
        if columns_str == '*':
            self.columns = ['*']
        else:
            self.columns = [col.strip() for col in columns_str.split(',')]

        # Extract WHERE conditions
        where_match = re.search(r'WHERE\s+(.*?)(?:\s+ORDER\s+BY|\s+LIMIT|\s+OFFSET|$)', self.query, re.IGNORECASE)
        if where_match:
            self.where_conditions = self._parse_where(where_match.group(1).strip())

        # Extract ORDER BY
        order_match = re.search(r'ORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?', self.query, re.IGNORECASE)
        if order_match:
            column = order_match.group(1)
            direction = order_match.group(2).upper() if order_match.group(2) else 'ASC'
            self.order_by = {'column': column, 'direction': direction}

        # Extract LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', query_upper)
        if limit_match:
            self.limit = int(limit_match.group(1))

        # Extract OFFSET
        offset_match = re.search(r'OFFSET\s+(\d+)', query_upper)
        if offset_match:
            self.offset = int(offset_match.group(1))

        return {
            'collection': self.collection,
            'columns': self.columns,
            'where': self.where_conditions,
            'order_by': self.order_by,
            'limit': self.limit,
            'offset': self.offset
        }

    def _parse_where(self, where_clause: str) -> Dict[str, Any]:
        """Parse WHERE clause into filter conditions."""
        filters = {}

        # Split by AND (case insensitive)
        conditions = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)

        for condition in conditions:
            condition = condition.strip()

            # Handle IN operator
            # Support both simple column names and qualified names (e.g., e.column or table.column)
            in_match = re.match(r'([\w.]+)\s+IN\s+\((.*?)\)', condition, re.IGNORECASE)
            if in_match:
                column = in_match.group(1)
                # Strip table qualifier if present (e.g., e2.department -> department)
                if '.' in column:
                    column = column.split('.')[-1]
                values_str = in_match.group(2)
                # Parse values (handle strings and numbers)
                values = []
                for val in re.findall(r"'([^']*)'|\"([^\"]*)\"|(\d+\.?\d*)", values_str):
                    values.append(val[0] or val[1] or (float(val[2]) if '.' in val[2] else int(val[2])))
                filters[column] = {'$in': values}
                continue

            # Handle LIKE operator
            # Support simple column names, qualified names, and function expressions
            # Pattern captures: column_name, table.column, or FUNCTION(args)
            like_match = re.match(r'([\w.]+(?:\([^)]*\))?)\s+LIKE\s+[\'"](.+?)[\'"]', condition, re.IGNORECASE)
            if like_match:
                column = like_match.group(1)
                # Strip table qualifier if present (but preserve function expressions)
                if '.' in column and '(' not in column:
                    column = column.split('.')[-1]
                pattern = like_match.group(2)
                # Convert SQL LIKE pattern to regex (% -> .*, _ -> .)
                regex_pattern = pattern.replace('%', '.*').replace('_', '.')
                filters[column] = {'$regex': regex_pattern}
                continue

            # Handle comparison operators
            # Support both simple column names and qualified names (e.g., e2.department)
            op_match = re.match(r'([\w.]+)\s*(>=|<=|<>|!=|>|<|=)\s*(.+)', condition)
            if op_match:
                column = op_match.group(1)
                # Strip table qualifier if present (e.g., e2.department -> department)
                if '.' in column:
                    column = column.split('.')[-1]
                operator = op_match.group(2)
                value_str = op_match.group(3).strip()

                # Parse value (string or number)
                value = self._parse_value(value_str)

                # Map SQL operators to EzDB operators
                if operator == '=':
                    filters[column] = value
                elif operator in ('!=', '<>'):
                    filters[column] = {'$ne': value}
                elif operator == '>':
                    filters[column] = {'$gt': value}
                elif operator == '>=':
                    filters[column] = {'$gte': value}
                elif operator == '<':
                    filters[column] = {'$lt': value}
                elif operator == '<=':
                    filters[column] = {'$lte': value}

        return filters

    def _parse_value(self, value_str: str) -> Any:
        """Parse a value string into appropriate Python type."""
        value_str = value_str.strip()

        # Subquery (starts with parenthesis and SELECT)
        # Keep as string for later evaluation by expression evaluator
        if value_str.startswith('(') and 'SELECT' in value_str.upper():
            return value_str  # Return as-is, will be evaluated by executor

        # String (quoted)
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Boolean
        if value_str.upper() == 'TRUE':
            return True
        if value_str.upper() == 'FALSE':
            return False

        # NULL
        if value_str.upper() == 'NULL':
            return None

        # Number (int or float)
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            # If all else fails, treat as string
            return value_str


class SQLExecutor:
    """Execute parsed SQL queries on EzDB collections."""

    def __init__(self, db_manager):
        """Initialize with database manager."""
        self.db_manager = db_manager

    def execute(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query and return results.

        Returns:
            {
                'columns': ['col1', 'col2', ...],
                'rows': [
                    {'col1': val1, 'col2': val2, ...},
                    ...
                ],
                'total': <total_count>,
                'returned': <returned_count>
            }
        """
        parser = SQLParser()
        parsed = parser.parse(query)

        # Get collection
        collection_name = parsed['collection']
        db = self.db_manager.get_collection(collection_name)

        if db is None:
            raise ValueError(f"Collection '{collection_name}' not found")

        # Get all vectors with metadata
        vectors = db.get_all_vectors()

        # Apply WHERE filters
        if parsed['where']:
            vectors = self._apply_filters(vectors, parsed['where'])

        # Apply ORDER BY
        if parsed['order_by']:
            vectors = self._apply_order(vectors, parsed['order_by'])

        # Apply OFFSET and LIMIT
        total_count = len(vectors)
        if parsed['offset']:
            vectors = vectors[parsed['offset']:]
        if parsed['limit']:
            vectors = vectors[:parsed['limit']]

        # Select columns
        rows = []
        for vec in vectors:
            row = {'id': vec['id']}
            if vec.get('metadata'):
                if parsed['columns'] == ['*']:
                    # Return all metadata columns + id
                    row.update(vec['metadata'])
                else:
                    # Return only specified columns
                    for col in parsed['columns']:
                        if col == 'id':
                            continue
                        if col in vec['metadata']:
                            row[col] = vec['metadata'][col]
                        else:
                            row[col] = None
            rows.append(row)

        # Determine columns
        if parsed['columns'] == ['*'] and rows:
            columns = list(rows[0].keys())
        else:
            columns = ['id'] + [col for col in parsed['columns'] if col != 'id']

        return {
            'columns': columns,
            'rows': rows,
            'total': total_count,
            'returned': len(rows)
        }

    def _apply_filters(self, vectors: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply WHERE filters to vectors."""
        filtered = []

        for vec in vectors:
            metadata = vec.get('metadata', {})
            matches = True

            for column, condition in filters.items():
                if column not in metadata:
                    matches = False
                    break

                value = metadata[column]

                # Handle operators
                if isinstance(condition, dict):
                    for op, target in condition.items():
                        if op == '$gt' and not (value > target):
                            matches = False
                        elif op == '$gte' and not (value >= target):
                            matches = False
                        elif op == '$lt' and not (value < target):
                            matches = False
                        elif op == '$lte' and not (value <= target):
                            matches = False
                        elif op == '$ne' and not (value != target):
                            matches = False
                        elif op == '$in' and value not in target:
                            matches = False
                        elif op == '$regex':
                            import re
                            if not re.search(target, str(value), re.IGNORECASE):
                                matches = False
                else:
                    # Direct equality
                    if value != condition:
                        matches = False

                if not matches:
                    break

            if matches:
                filtered.append(vec)

        return filtered

    def _apply_order(self, vectors: List[Dict], order_by: Dict[str, str]) -> List[Dict]:
        """Apply ORDER BY to vectors."""
        column = order_by['column']
        reverse = (order_by['direction'] == 'DESC')

        def get_sort_key(vec):
            metadata = vec.get('metadata', {})
            value = metadata.get(column)
            # Handle None values by putting them at the end
            if value is None:
                return (1, 0) if not reverse else (0, 0)
            return (0, value)

        return sorted(vectors, key=get_sort_key, reverse=reverse)
