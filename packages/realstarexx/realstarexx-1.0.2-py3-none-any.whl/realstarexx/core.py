from typing import Any, List, Dict, Optional, Union, Sequence
import ast
import sys


class Node:
    _VALID_TYPES = {
        'src', 'var', 'p', 'if', 'for', 'while', 'function', 'call', 
        'get', 'set', 'return', 'list', 'dict', 'add', 'subtract', 
        'multiply', 'divide', 'modulo', 'power', 'eq', 'neq', 'gt', 
        'lt', 'gte', 'lte', 'and_', 'or_', 'not_', 'in_', 'not_in'
    }
    
    def __init__(self, node_type: str, *children: Any, **props: Any) -> None:
        """
        Initialize a Node.
        
        Args:
            node_type: Type of the node
            *children: Child nodes
            **props: Properties for the node
            
        Raises:
            ValueError: If node_type is invalid
        """
        if node_type not in self._VALID_TYPES:
            raise ValueError(f"Invalid node type: {node_type}. Valid types: {sorted(self._VALID_TYPES)}")
        
        self.type = node_type
        self.children = list(children)
        self.props = props
        
        # Validate required properties based on node type
        self._validate_props()

    def _validate_props(self) -> None:
        """Validate required properties for each node type."""
        required_props = {
            'var': ['name', 'value'],
            'if': ['condition', 'then'],
            'for': ['item', 'in_', 'do'],
            'while': ['condition', 'do'],
            'function': ['name', 'params'],
            'call': ['name', 'args'],
            'get': ['name'],
            'set': ['name', 'value'],
            'return': ['value'],
            'add': ['a', 'b'],
            'subtract': ['a', 'b'],
            'multiply': ['a', 'b'],
            'divide': ['a', 'b'],
            'modulo': ['a', 'b'],
            'power': ['a', 'b'],
            'eq': ['a', 'b'],
            'neq': ['a', 'b'],
            'gt': ['a', 'b'],
            'lt': ['a', 'b'],
            'gte': ['a', 'b'],
            'lte': ['a', 'b'],
            'and_': ['a', 'b'],
            'or_': ['a', 'b'],
            'not_': ['a'],
            'in_': ['a', 'b'],
            'not_in': ['a', 'b']
        }
        
        if self.type in required_props:
            missing = [prop for prop in required_props[self.type] if prop not in self.props]
            if missing:
                raise ValueError(f"Missing required properties for {self.type}: {missing}")

    def src(self) -> str:
        """
        Generate Python source code from the node.
        
        Returns:
            Generated Python code as string
            
        Raises:
            ValueError: If node type is not supported
        """
        try:
            return self._generate_code()
        except Exception as e:
            raise ValueError(f"Error generating code for node type '{self.type}': {e}") from e

    def _generate_code(self) -> str:
        """Internal method to generate code based on node type."""
        handlers = {
            'src': self._handle_src,
            'var': self._handle_var,
            'p': self._handle_print,
            'if': self._handle_if,
            'for': self._handle_for,
            'while': self._handle_while,
            'function': self._handle_function,
            'call': self._handle_call,
            'get': self._handle_get,
            'set': self._handle_set,
            'return': self._handle_return,
            'list': self._handle_list,
            'dict': self._handle_dict,
            'add': self._handle_binary_op('+'),
            'subtract': self._handle_binary_op('-'),
            'multiply': self._handle_binary_op('*'),
            'divide': self._handle_binary_op('/'),
            'modulo': self._handle_binary_op('%'),
            'power': self._handle_binary_op('**'),
            'eq': self._handle_binary_op('=='),
            'neq': self._handle_binary_op('!='),
            'gt': self._handle_binary_op('>'),
            'lt': self._handle_binary_op('<'),
            'gte': self._handle_binary_op('>='),
            'lte': self._handle_binary_op('<='),
            'and_': self._handle_binary_op('and'),
            'or_': self._handle_binary_op('or'),
            'not_': self._handle_not,
            'in_': self._handle_binary_op('in'),
            'not_in': self._handle_binary_op('not in')
        }
        
        handler = handlers.get(self.type)
        if handler is None:
            return self._handle_default()
        
        if callable(handler):
            return handler()
        
        return handler

    def _handle_src(self) -> str:
        """Handle source code generation."""
        return '\n'.join(child.src() for child in self.children if child.src().strip())

    def _handle_var(self) -> str:
        """Handle variable declaration."""
        return f"{self.props['name']} = {self._value_repr(self.props['value'])}"

    def _handle_print(self) -> str:
        """Handle print statement."""
        values = [self._value_repr(child) for child in self.children]
        return f"print({', '.join(values)})"

    def _handle_if(self) -> str:
        """Handle if statement."""
        condition = self._ensure_expression(self.props['condition'])
        then_code = self.props['then'].src()
        else_code = self.props.get('else_', Node('src')).src()
        
        result = f"if {condition}:\n{self._indent(then_code)}"
        if else_code.strip():
            result += f"\nelse:\n{self._indent(else_code)}"
        return result

    def _handle_for(self) -> str:
        """Handle for loop."""
        iterable = self._ensure_expression(self.props['in_'])
        return f"for {self.props['item']} in {iterable}:\n{self._indent(self.props['do'].src())}"

    def _handle_while(self) -> str:
        """Handle while loop."""
        condition = self._ensure_expression(self.props['condition'])
        return f"while {condition}:\n{self._indent(self.props['do'].src())}"

    def _handle_function(self) -> str:
        """Handle function definition."""
        body_lines = []
        for child in self.children:
            child_code = child.src()
            if child_code.strip():
                body_lines.append(child_code)
        
        body = '\n'.join(body_lines)
        params_str = ', '.join(self.props['params'])
        return f"def {self.props['name']}({params_str}):\n{self._indent(body) if body else '    pass'}"

    def _handle_call(self) -> str:
        """Handle function call."""
        args = ', '.join(self._value_repr(arg) for arg in self.props['args'])
        return f"{self.props['name']}({args})"

    def _handle_get(self) -> str:
        """Handle variable get."""
        return self.props['name']

    def _handle_set(self) -> str:
        """Handle variable assignment."""
        return f"{self.props['name']} = {self._value_repr(self.props['value'])}"

    def _handle_return(self) -> str:
        """Handle return statement."""
        return f"return {self._value_repr(self.props['value'])}"

    def _handle_list(self) -> str:
        """Handle list literal."""
        items = ', '.join(self._value_repr(item) for item in self.children)
        return f"[{items}]"

    def _handle_dict(self) -> str:
        """Handle dictionary literal."""
        items = ', '.join(f"{self._value_repr(k)}: {self._value_repr(v)}" 
                         for k, v in self.props.items())
        return f"{{{items}}}"

    def _handle_binary_op(self, operator: str):
        """Create handler for binary operations."""
        def handler():
            a = self._ensure_expression(self.props['a'])
            b = self._ensure_expression(self.props['b'])
            return f"({a} {operator} {b})"
        return handler

    def _handle_not(self) -> str:
        """Handle not operation."""
        a = self._ensure_expression(self.props['a'])
        return f"(not {a})"

    def _handle_default(self) -> str:
        """Handle default case."""
        if self.children:
            return str(self.children[0])
        return ""

    def _value_repr(self, value: Any) -> str:
        """
        Convert value to Python code representation.
        
        Args:
            value: Value to convert
            
        Returns:
            String representation suitable for Python code
        """
        if isinstance(value, Node):
            return value.src()
        elif isinstance(value, str):
            # Proper string escaping
            return repr(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return str(value)
        elif value is None:
            return "None"
        else:
            return repr(value)

    def _ensure_expression(self, value: Any) -> str:
        """
        Ensure value is a valid expression.
        
        Args:
            value: Value to convert to expression
            
        Returns:
            Valid Python expression string
        """
        if isinstance(value, Node):
            return value.src()
        elif isinstance(value, str):
            return value
        else:
            return self._value_repr(value)

    def _indent(self, code: str) -> str:
        """
        Indent code block.
        
        Args:
            code: Code to indent
            
        Returns:
            Indented code
        """
        if not code.strip():
            return "    pass"
        return '\n'.join('    ' + line for line in code.split('\n'))

    def run(self, globals_dict: Optional[Dict[str, Any]] = None, locals_dict: Optional[Dict[str, Any]] = None) -> None:
        """
        Execute the generated code.
        
        Args:
            globals_dict: Global context for execution
            locals_dict: Local context for execution
            
        Raises:
            SyntaxError: If generated code has syntax errors
            Exception: Any exception during execution
        """
        code = self.src()
        
        # Validate syntax before execution
        try:
            ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Generated code has syntax error: {e}\nGenerated code:\n{code}") from e
        
        # Execute with proper context
        context = globals_dict or {}
        if locals_dict is None:
            locals_dict = context
        
        try:
            exec(code, context, locals_dict)
        except Exception as e:
            raise RuntimeError(f"Error executing generated code: {e}\nGenerated code:\n{code}") from e

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Node(type={self.type}, children={len(self.children)}, props={list(self.props.keys())})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.src()


# Factory functions with proper type hints

def src(*children: Node) -> Node:
    """Create a source code block."""
    return Node('src', *children)

def var(name: str, value: Any) -> Node:
    """Create a variable declaration."""
    return Node('var', name=name, value=value)

def p(*values: Any) -> Node:
    """Create a print statement."""
    return Node('p', *values)

def if_(condition: Any, then: Node, else_: Optional[Node] = None) -> Node:
    """Create an if statement."""
    return Node('if', condition=condition, then=then, else_=else_)

def for_(item: str, in_: Any, do: Node) -> Node:
    """Create a for loop."""
    return Node('for', item=item, in_=in_, do=do)

def while_(condition: Any, do: Node) -> Node:
    """Create a while loop."""
    return Node('while', condition=condition, do=do)

def function(name: str, params: List[str], *body: Node) -> Node:
    """Create a function definition."""
    return Node('function', *body, name=name, params=params)

def call(name: str, args: List[Any]) -> Node:
    """Create a function call."""
    return Node('call', name=name, args=args)

def get(name: str) -> Node:
    """Create a variable reference."""
    return Node('get', name=name)

def set_(name: str, value: Any) -> Node:
    """Create a variable assignment."""
    return Node('set', name=name, value=value)

def return_(value: Any) -> Node:
    """Create a return statement."""
    return Node('return', value=value)

def list_(*items: Any) -> Node:
    """Create a list literal."""
    return Node('list', *items)

def dict_(**items: Any) -> Node:
    """Create a dictionary literal."""
    return Node('dict', **items)

def add(a: Any, b: Any) -> Node:
    """Create an addition operation."""
    return Node('add', a=a, b=b)

def subtract(a: Any, b: Any) -> Node:
    """Create a subtraction operation."""
    return Node('subtract', a=a, b=b)

def multiply(a: Any, b: Any) -> Node:
    """Create a multiplication operation."""
    return Node('multiply', a=a, b=b)

def divide(a: Any, b: Any) -> Node:
    """Create a division operation."""
    return Node('divide', a=a, b=b)

def modulo(a: Any, b: Any) -> Node:
    """Create a modulo operation."""
    return Node('modulo', a=a, b=b)

def power(a: Any, b: Any) -> Node:
    """Create a power operation."""
    return Node('power', a=a, b=b)

def eq(a: Any, b: Any) -> Node:
    """Create an equality comparison."""
    return Node('eq', a=a, b=b)

def neq(a: Any, b: Any) -> Node:
    """Create an inequality comparison."""
    return Node('neq', a=a, b=b)

def gt(a: Any, b: Any) -> Node:
    """Create a greater than comparison."""
    return Node('gt', a=a, b=b)

def lt(a: Any, b: Any) -> Node:
    """Create a less than comparison."""
    return Node('lt', a=a, b=b)

def gte(a: Any, b: Any) -> Node:
    """Create a greater than or equal comparison."""
    return Node('gte', a=a, b=b)

def lte(a: Any, b: Any) -> Node:
    """Create a less than or equal comparison."""
    return Node('lte', a=a, b=b)

def and_(a: Any, b: Any) -> Node:
    """Create a logical AND operation."""
    return Node('and_', a=a, b=b)

def or_(a: Any, b: Any) -> Node:
    """Create a logical OR operation."""
    return Node('or_', a=a, b=b)

def not_(a: Any) -> Node:
    """Create a logical NOT operation."""
    return Node('not_', a=a)

def in_(a: Any, b: Any) -> Node:
    """Create an 'in' membership test."""
    return Node('in_', a=a, b=b)

def not_in(a: Any, b: Any) -> Node:
    """Create a 'not in' membership test."""
    return Node('not_in', a=a, b=b)


# Built-in function wrappers with proper error handling

def range_(start: int, stop: Optional[int] = None, step: Optional[int] = None) -> str:
    """Generate range() function call."""
    if stop is None and step is None:
        return f"range({start})"
    elif step is None:
        return f"range({start}, {stop})"
    else:
        return f"range({start}, {stop}, {step})"

def len_(obj: Any) -> str:
    """Generate len() function call."""
    obj_str = obj.src() if hasattr(obj, 'src') else str(obj)
    return f"len({obj_str})"

def sum_(iterable: Any) -> str:
    """Generate sum() function call."""
    iterable_str = iterable.src() if hasattr(iterable, 'src') else str(iterable)
    return f"sum({iterable_str})"

def min_(*args: Any) -> str:
    """Generate min() function call."""
    args_str = ', '.join(arg.src() if hasattr(arg, 'src') else str(arg) for arg in args)
    return f"min({args_str})"

def max_(*args: Any) -> str:
    """Generate max() function call."""
    args_str = ', '.join(arg.src() if hasattr(arg, 'src') else str(arg) for arg in args)
    return f"max({args_str})"

def abs_(x: Any) -> str:
    """Generate abs() function call."""
    x_str = x.src() if hasattr(x, 'src') else str(x)
    return f"abs({x_str})"

def round_(x: Any, ndigits: int = 0) -> str:
    """Generate round() function call."""
    x_str = x.src() if hasattr(x, 'src') else str(x)
    return f"round({x_str}, {ndigits})"

def str_(obj: Any) -> str:
    """Generate str() function call."""
    obj_str = obj.src() if hasattr(obj, 'src') else str(obj)
    return f"str({obj_str})"

def int_(obj: Any) -> str:
    """Generate int() function call."""
    obj_str = obj.src() if hasattr(obj, 'src') else str(obj)
    return f"int({obj_str})"

def float_(obj: Any) -> str:
    """Generate float() function call."""
    obj_str = obj.src() if hasattr(obj, 'src') else str(obj)
    return f"float({obj_str})"

def bool_(obj: Any) -> str:
    """Generate bool() function call."""
    obj_str = obj.src() if hasattr(obj, 'src') else str(obj)
    return f"bool({obj_str})"

def type_(obj: Any) -> str:
    """Generate type() function call."""
    obj_str = obj.src() if hasattr(obj, 'src') else str(obj)
    return f"type({obj_str})"

def all_(iterable: Any) -> str:
    """Generate all() function call."""
    iterable_str = iterable.src() if hasattr(iterable, 'src') else str(iterable)
    return f"all({iterable_str})"

def any_(iterable: Any) -> str:
    """Generate any() function call."""
    iterable_str = iterable.src() if hasattr(iterable, 'src') else str(iterable)
    return f"any({iterable_str})"

def sorted_(iterable: Any, reverse: bool = False, key: Optional[str] = None) -> str:
    """Generate sorted() function call."""
    iterable_str = iterable.src() if hasattr(iterable, 'src') else str(iterable)
    params = [iterable_str]
    if key:
        params.append(f"key={key}")
    if reverse:
        params.append("reverse=True")
    return f"sorted({', '.join(params)})"

def reversed_(iterable: Any) -> str:
    """Generate reversed() function call."""
    iterable_str = iterable.src() if hasattr(iterable, 'src') else str(iterable)
    return f"reversed({iterable_str})"

def enumerate_(iterable: Any, start: int = 0) -> str:
    """Generate enumerate() function call."""
    iterable_str = iterable.src() if hasattr(iterable, 'src') else str(iterable)
    if start != 0:
        return f"enumerate({iterable_str}, {start})"
    return f"enumerate({iterable_str})"

def zip_(*iterables: Any) -> str:
    """Generate zip() function call."""
    iterables_str = ', '.join(iterable.src() if hasattr(iterable, 'src') else str(iterable) 
                            for iterable in iterables)
    return f"zip({iterables_str})"

def owner():
    return print("Owner: Starexx")
def creator():
    return print("Creator: Starexx")
def gay():
    return print("You're Gay!")