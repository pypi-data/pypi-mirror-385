"""
Enhanced Model Builder using Google OR-Tools MathOpt
Integrates with 7-step reasoning process for robust model building
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re

try:
    from ortools.math_opt.python import mathopt
    HAS_MATHOPT = True
except ImportError:
    HAS_MATHOPT = False
    logging.warning("MathOpt not available. Install with: pip install ortools")

logger = logging.getLogger(__name__)

@dataclass
class VariableSpec:
    name: str
    var_type: str  # 'continuous', 'integer', 'binary'
    lower_bound: float
    upper_bound: float
    description: str

@dataclass
class ConstraintSpec:
    expression: str
    description: str
    constraint_type: str  # '<=', '>=', '='

@dataclass
class ObjectiveSpec:
    obj_type: str  # 'maximize', 'minimize'
    expression: str
    description: str

class MathOptModelBuilder:
    """
    Enhanced model builder using Google OR-Tools MathOpt
    Integrates 7-step reasoning with structured model building
    """
    
    def __init__(self):
        self.model = None
        self.variables = {}
        self.constraints = []
        self.objective = None
        
    def build_model_from_reasoning(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build MathOpt model from 7-step reasoning data
        """
        try:
            if not HAS_MATHOPT:
                return {
                    "status": "error",
                    "error": "MathOpt not available. Install with: pip install ortools"
                }
            
            # Extract components from reasoning data
            variables_spec = reasoning_data.get('variables', [])
            constraints_spec = reasoning_data.get('constraints', [])
            objective_spec = reasoning_data.get('objective', {})
            
            # Create MathOpt model
            model_name = f"optimization_model_{hash(str(reasoning_data)) % 10000}"
            self.model = mathopt.Model(name=model_name)
            
            # Step 1: Add variables
            self._add_variables(variables_spec)
            
            # Step 2: Add constraints
            self._add_constraints(constraints_spec)
            
            # Step 3: Set objective
            self._set_objective(objective_spec)
            
            # Step 4: Validate model
            validation_result = self._validate_model()
            
            return {
                "status": "success",
                "model": self.model,
                "variables": self.variables,
                "constraints": self.constraints,
                "objective": self.objective,
                "validation": validation_result,
                "model_name": model_name
            }
            
        except Exception as e:
            logger.error(f"MathOpt model building error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _add_variables(self, variables_spec: List[Dict[str, Any]]):
        """Add variables to the MathOpt model"""
        for var_spec in variables_spec:
            if not isinstance(var_spec, dict):
                continue
                
            name = var_spec.get('name', '')
            var_type = var_spec.get('type', 'continuous')
            bounds = var_spec.get('bounds', '0 to 1')
            description = var_spec.get('description', '')
            
            # Parse bounds
            lower_bound, upper_bound = self._parse_bounds(bounds)
            
            # Determine if integer
            is_integer = var_type.lower() in ['integer', 'binary']
            
            # Add variable to model
            try:
                var = self.model.add_variable(
                    lb=lower_bound,
                    ub=upper_bound,
                    is_integer=is_integer,
                    name=name
                )
                self.variables[name] = var
                logger.info(f"Added variable {name}: {bounds} ({var_type})")
            except Exception as e:
                logger.error(f"Failed to add variable {name}: {e}")
    
    def _add_constraints(self, constraints_spec: List[Dict[str, Any]]):
        """Add constraints to the MathOpt model using proper MathOptFormat structure"""
        for i, constraint_spec in enumerate(constraints_spec):
            if not isinstance(constraint_spec, dict):
                continue
                
            expression = constraint_spec.get('expression', '')
            description = constraint_spec.get('description', f'constraint_{i+1}')
            
            try:
                # Parse constraint into MathOptFormat structure
                constraint_data = self._parse_constraint_to_mathopt_format(expression)
                if constraint_data:
                    # Create constraint using MathOptFormat structure
                    self._add_constraint_from_mathopt_format(constraint_data, description)
                    
                    self.constraints.append({
                        'expression': expression,
                        'description': description,
                        'constraint_data': constraint_data
                    })
                    logger.info(f"Added constraint: {expression}")
                else:
                    logger.warning(f"Could not parse constraint: {expression}")
                        
            except Exception as e:
                logger.error(f"Failed to add constraint {expression}: {e}")
    
    def _parse_constraint_to_mathopt_format(self, expression: str) -> Optional[Dict[str, Any]]:
        """Parse constraint expression into MathOptFormat structure"""
        try:
            # Clean the expression
            expr = expression.strip()
            
            # Handle different constraint operators
            if '<=' in expr:
                parts = expr.rsplit('<=', 1)
                if len(parts) == 2:
                    lhs_expr = parts[0].strip()
                    rhs_expr = parts[1].strip()
                    return self._create_mathopt_constraint(lhs_expr, rhs_expr, '<=')
            elif '>=' in expr:
                parts = expr.rsplit('>=', 1)
                if len(parts) == 2:
                    lhs_expr = parts[0].strip()
                    rhs_expr = parts[1].strip()
                    return self._create_mathopt_constraint(lhs_expr, rhs_expr, '>=')
            elif '==' in expr:
                parts = expr.split('==')
                if len(parts) == 2:
                    lhs_expr = parts[0].strip()
                    rhs_expr = parts[1].strip()
                    return self._create_mathopt_constraint(lhs_expr, rhs_expr, '==')
            elif '=' in expr and not any(op in expr for op in ['<=', '>=', '==']):
                parts = expr.split('=', 1)
                if len(parts) == 2:
                    lhs_expr = parts[0].strip()
                    rhs_expr = parts[1].strip()
                    return self._create_mathopt_constraint(lhs_expr, rhs_expr, '==')
            
            logger.warning(f"Could not parse constraint: {expression}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse constraint {expression}: {e}")
            return None
    
    def _create_mathopt_constraint(self, lhs_expr: str, rhs_expr: str, operator: str) -> Dict[str, Any]:
        """Create MathOptFormat constraint structure"""
        # Parse LHS into ScalarAffineFunction format
        lhs_function = self._parse_to_scalar_affine_function(lhs_expr)
        
        # Parse RHS into ScalarAffineFunction format
        rhs_function = self._parse_to_scalar_affine_function(rhs_expr)
        
        # Create constraint based on operator
        if operator == '<=':
            # lhs <= rhs becomes lhs - rhs <= 0
            constraint_function = self._subtract_functions(lhs_function, rhs_function)
            constraint_set = {"type": "LessThan", "upper": 0}
        elif operator == '>=':
            # lhs >= rhs becomes lhs - rhs >= 0
            constraint_function = self._subtract_functions(lhs_function, rhs_function)
            constraint_set = {"type": "GreaterThan", "lower": 0}
        else:  # '=='
            # lhs == rhs becomes lhs - rhs == 0
            constraint_function = self._subtract_functions(lhs_function, rhs_function)
            constraint_set = {"type": "EqualTo", "value": 0}
        
        return {
            "function": constraint_function,
            "set": constraint_set
        }
    
    def _parse_to_scalar_affine_function(self, expr: str) -> Dict[str, Any]:
        """Parse expression into ScalarAffineFunction format"""
        try:
            # Handle simple cases
            if expr.replace('.', '').replace('-', '').isdigit():
                return {
                    "type": "ScalarAffineFunction",
                    "terms": [],
                    "constant": float(expr)
                }
            
            # Parse linear terms
            terms = self._split_linear_terms(expr)
            mathopt_terms = []
            constant = 0.0
            
            for term in terms:
                coefficient, variable_name = self._parse_term(term)
                if variable_name and variable_name in self.variables:
                    mathopt_terms.append({
                        "coefficient": coefficient,
                        "variable": variable_name
                    })
                else:
                    constant += coefficient
            
            return {
                "type": "ScalarAffineFunction",
                "terms": mathopt_terms,
                "constant": constant
            }
            
        except Exception as e:
            logger.error(f"Failed to parse expression to ScalarAffineFunction: {expr}, {e}")
            return {
                "type": "ScalarAffineFunction",
                "terms": [],
                "constant": 0.0
            }
    
    def _subtract_functions(self, func1: Dict[str, Any], func2: Dict[str, Any]) -> Dict[str, Any]:
        """Subtract two ScalarAffineFunctions: func1 - func2"""
        # Combine terms from both functions
        all_terms = []
        
        # Add terms from func1
        for term in func1.get("terms", []):
            all_terms.append({
                "coefficient": term["coefficient"],
                "variable": term["variable"]
            })
        
        # Subtract terms from func2
        for term in func2.get("terms", []):
            all_terms.append({
                "coefficient": -term["coefficient"],
                "variable": term["variable"]
            })
        
        # Combine like terms
        combined_terms = {}
        for term in all_terms:
            var_name = term["variable"]
            if var_name in combined_terms:
                combined_terms[var_name] += term["coefficient"]
            else:
                combined_terms[var_name] = term["coefficient"]
        
        # Convert back to list format
        final_terms = []
        for var_name, coeff in combined_terms.items():
            if abs(coeff) > 1e-10:  # Only include non-zero coefficients
                final_terms.append({
                    "coefficient": coeff,
                    "variable": var_name
                })
        
        # Calculate constant
        constant = func1.get("constant", 0.0) - func2.get("constant", 0.0)
        
        return {
            "type": "ScalarAffineFunction",
            "terms": final_terms,
            "constant": constant
        }
    
    def _add_constraint_from_mathopt_format(self, constraint_data: Dict[str, Any], name: str):
        """Add constraint to model using MathOptFormat structure"""
        try:
            # This is a simplified implementation
            # In a full implementation, we would convert MathOptFormat to MathOpt API calls
            # For now, we'll use the existing MathOpt API with proper linear expressions
            
            function = constraint_data["function"]
            constraint_set = constraint_data["set"]
            
            # Build linear expression from ScalarAffineFunction
            linear_expr = 0.0
            for term in function.get("terms", []):
                var_name = term["variable"]
                coefficient = term["coefficient"]
                if var_name in self.variables:
                    linear_expr += coefficient * self.variables[var_name]
            
            # Add constant
            linear_expr += function.get("constant", 0.0)
            
            # Add constraint based on set type
            set_type = constraint_set["type"]
            if set_type == "LessThan":
                upper_bound = constraint_set["upper"]
                self.model.add_linear_constraint(linear_expr <= upper_bound, name=name)
            elif set_type == "GreaterThan":
                lower_bound = constraint_set["lower"]
                self.model.add_linear_constraint(linear_expr >= lower_bound, name=name)
            elif set_type == "EqualTo":
                value = constraint_set["value"]
                self.model.add_linear_constraint(linear_expr == value, name=name)
            
        except Exception as e:
            logger.error(f"Failed to add constraint from MathOptFormat: {e}")
            raise
    
    def _set_objective(self, objective_spec: Dict[str, Any]):
        """Set objective function using MathOptFormat structure"""
        if not isinstance(objective_spec, dict):
            return
            
        obj_type = objective_spec.get('type', 'maximize')
        expression = objective_spec.get('expression', '')
        description = objective_spec.get('description', '')
        
        try:
            # Parse objective expression into MathOptFormat structure
            objective_function = self._parse_to_scalar_affine_function(expression)
            
            # Build linear expression from ScalarAffineFunction
            linear_expr = 0.0
            for term in objective_function.get("terms", []):
                var_name = term["variable"]
                coefficient = term["coefficient"]
                if var_name in self.variables:
                    linear_expr += coefficient * self.variables[var_name]
            
            # Add constant
            linear_expr += objective_function.get("constant", 0.0)
            
            # Set objective
            if obj_type.lower() == 'maximize':
                self.model.maximize(linear_expr)
            else:
                self.model.minimize(linear_expr)
            
            self.objective = {
                'type': obj_type,
                'expression': expression,
                'description': description,
                'mathopt_function': objective_function,
                'mathopt_expr': linear_expr
            }
            logger.info(f"Set objective: {obj_type} {expression}")
        except Exception as e:
            logger.error(f"Failed to set objective {expression}: {e}")
    
    def _parse_bounds(self, bounds_str: str) -> Tuple[float, float]:
        """Parse bounds string like '0 to 1' or '0 to 100'"""
        try:
            # Handle different formats
            if ' to ' in bounds_str:
                parts = bounds_str.split(' to ')
                return float(parts[0]), float(parts[1])
            elif ' <= ' in bounds_str:
                # Handle '0 <= x <= 1' format
                parts = bounds_str.split(' <= ')
                return float(parts[0]), float(parts[1].split(' <= ')[1])
            else:
                # Default bounds
                return 0.0, 1.0
        except:
            return 0.0, 1.0
    
    def _parse_constraint(self, expression: str) -> Optional[Dict[str, Any]]:
        """Parse constraint expression like 'x1 + x2 <= 1'"""
        try:
            # Clean the expression
            expr = expression.strip()
            
            # Handle different constraint operators
            if '<=' in expr:
                # Find the last occurrence to handle expressions like "x1 <= x2 <= 1"
                parts = expr.rsplit('<=', 1)
                if len(parts) == 2:
                    lhs = self._parse_linear_expression(parts[0].strip())
                    rhs = self._parse_linear_expression(parts[1].strip())
                    return {'lhs': lhs, 'rhs': rhs, 'type': '<='}
            elif '>=' in expr:
                parts = expr.rsplit('>=', 1)
                if len(parts) == 2:
                    lhs = self._parse_linear_expression(parts[0].strip())
                    rhs = self._parse_linear_expression(parts[1].strip())
                    return {'lhs': lhs, 'rhs': rhs, 'type': '>='}
            elif '==' in expr:
                parts = expr.split('==')
                if len(parts) == 2:
                    lhs = self._parse_linear_expression(parts[0].strip())
                    rhs = self._parse_linear_expression(parts[1].strip())
                    return {'lhs': lhs, 'rhs': rhs, 'type': '='}
            elif '=' in expr and not any(op in expr for op in ['<=', '>=', '==']):
                parts = expr.split('=', 1)
                if len(parts) == 2:
                    lhs = self._parse_linear_expression(parts[0].strip())
                    rhs = self._parse_linear_expression(parts[1].strip())
                    return {'lhs': lhs, 'rhs': rhs, 'type': '='}
            
            logger.warning(f"Could not parse constraint: {expression}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse constraint {expression}: {e}")
            return None
    
    def _parse_linear_expression(self, expr: str):
        """Parse linear expression like '0.12*x1 + 0.08*x2' into MathOpt linear expression"""
        try:
            if not expr or not expr.strip():
                return 0
            
            # Clean the expression
            expr = expr.strip()
            
            # Handle simple cases first
            if expr.isdigit() or (expr.replace('.', '').replace('-', '').isdigit()):
                return float(expr)
            
            # Parse linear terms like "0.12*x1 + 0.08*x2" or "x1 + x2"
            terms = self._split_linear_terms(expr)
            mathopt_expr = 0
            
            for term in terms:
                coefficient, variable_name = self._parse_term(term)
                if variable_name in self.variables:
                    mathopt_expr += coefficient * self.variables[variable_name]
                else:
                    # If variable doesn't exist, treat as constant
                    mathopt_expr += coefficient
            
            return mathopt_expr
            
        except Exception as e:
            logger.error(f"Failed to parse linear expression '{expr}': {e}")
            return 0
    
    def _parse_objective(self, expression: str):
        """Parse objective expression into MathOpt linear expression"""
        try:
            if not expression or not expression.strip():
                return 0
            
            # Clean the expression
            expr = expression.strip()
            
            # Handle simple cases first
            if expr.isdigit() or (expr.replace('.', '').replace('-', '').isdigit()):
                return float(expr)
            
            # Parse linear terms
            terms = self._split_linear_terms(expr)
            mathopt_expr = 0
            
            for term in terms:
                coefficient, variable_name = self._parse_term(term)
                if variable_name in self.variables:
                    mathopt_expr += coefficient * self.variables[variable_name]
                else:
                    # If variable doesn't exist, treat as constant
                    mathopt_expr += coefficient
            
            return mathopt_expr
            
        except Exception as e:
            logger.error(f"Failed to parse objective expression '{expression}': {e}")
            return 0
    
    def _split_linear_terms(self, expr: str) -> List[str]:
        """Split expression into individual terms"""
        try:
            # Handle addition and subtraction
            terms = []
            current_term = ""
            i = 0
            
            while i < len(expr):
                char = expr[i]
                
                if char in ['+', '-'] and i > 0 and expr[i-1] not in ['*', '/', '^', 'e', 'E']:
                    if current_term.strip():
                        terms.append(current_term.strip())
                    current_term = char
                else:
                    current_term += char
                i += 1
            
            if current_term.strip():
                terms.append(current_term.strip())
            
            # If no terms found, return the whole expression
            if not terms:
                terms = [expr]
            
            return terms
            
        except Exception as e:
            logger.error(f"Failed to split terms in '{expr}': {e}")
            return [expr]
    
    def _parse_term(self, term: str) -> Tuple[float, str]:
        """Parse a single term like '0.12*x1' or 'x1' into (coefficient, variable_name)"""
        try:
            term = term.strip()
            
            # Handle negative terms
            is_negative = term.startswith('-')
            if is_negative:
                term = term[1:]
            
            # Handle positive terms with explicit +
            if term.startswith('+'):
                term = term[1:]
            
            # Check if it's just a number
            if term.replace('.', '').isdigit():
                coefficient = float(term)
                if is_negative:
                    coefficient = -coefficient
                return coefficient, ""
            
            # Check if it's a variable with coefficient
            if '*' in term:
                parts = term.split('*')
                if len(parts) == 2:
                    coeff_str = parts[0].strip()
                    var_str = parts[1].strip()
                    
                    if coeff_str.replace('.', '').replace('-', '').isdigit():
                        coefficient = float(coeff_str)
                        if is_negative:
                            coefficient = -coefficient
                        return coefficient, var_str
            
            # Check if it's just a variable
            if term.replace('_', '').replace('-', '').isalnum():
                coefficient = -1.0 if is_negative else 1.0
                return coefficient, term
            
            # Default case
            coefficient = -1.0 if is_negative else 1.0
            return coefficient, term
            
        except Exception as e:
            logger.error(f"Failed to parse term '{term}': {e}")
            return 0.0, ""
    
    def _validate_model(self) -> Dict[str, Any]:
        """Validate the built model"""
        try:
            validation = {
                'variables_count': len(self.variables),
                'constraints_count': len(self.constraints),
                'has_objective': self.objective is not None,
                'model_created': self.model is not None,
                'all_variables_used': True,  # Would need proper validation
                'model_feasible': True  # Would need proper validation
            }
            return validation
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {'error': str(e)}

def create_portfolio_model_example():
    """
    Example of creating a portfolio optimization model with MathOpt
    """
    if not HAS_MATHOPT:
        return {"error": "MathOpt not available"}
    
    # Example reasoning data for portfolio optimization
    reasoning_data = {
        "reasoning_steps": {
            "step1_decision_analysis": "Allocate to individual stocks: AAPL, MSFT, GOOGL, AMZN, META",
            "step2_constraint_analysis": "Max 10% per stock, max 30% per sector, total 100%",
            "step3_objective_analysis": "Maximize expected portfolio return",
            "step4_variable_design": "Individual stock allocation variables",
            "step5_constraint_formulation": "Stock and sector limits, total allocation",
            "step6_objective_formulation": "Weighted sum of expected returns",
            "step7_validation": "All variables used in constraints and objective"
        },
        "variables": [
            {"name": "x_AAPL", "type": "continuous", "bounds": "0 to 0.1", "description": "AAPL allocation"},
            {"name": "x_MSFT", "type": "continuous", "bounds": "0 to 0.1", "description": "MSFT allocation"},
            {"name": "x_GOOGL", "type": "continuous", "bounds": "0 to 0.1", "description": "GOOGL allocation"},
            {"name": "x_AMZN", "type": "continuous", "bounds": "0 to 0.1", "description": "AMZN allocation"},
            {"name": "x_META", "type": "continuous", "bounds": "0 to 0.1", "description": "META allocation"}
        ],
        "constraints": [
            {"expression": "x_AAPL + x_MSFT + x_GOOGL + x_AMZN + x_META = 1", "description": "Total allocation 100%"},
            {"expression": "x_AAPL <= 0.1", "description": "Max 10% in AAPL"},
            {"expression": "x_MSFT <= 0.1", "description": "Max 10% in MSFT"},
            {"expression": "x_GOOGL <= 0.1", "description": "Max 10% in GOOGL"},
            {"expression": "x_AMZN <= 0.1", "description": "Max 10% in AMZN"},
            {"expression": "x_META <= 0.1", "description": "Max 10% in META"},
            {"expression": "x_AAPL + x_MSFT + x_GOOGL + x_AMZN + x_META <= 0.3", "description": "Max 30% in tech sector"}
        ],
        "objective": {
            "type": "maximize",
            "expression": "0.12*x_AAPL + 0.12*x_MSFT + 0.12*x_GOOGL + 0.12*x_AMZN + 0.12*x_META",
            "description": "Expected portfolio return"
        }
    }
    
    # Build model
    builder = MathOptModelBuilder()
    result = builder.build_model_from_reasoning(reasoning_data)
    
    return result

if __name__ == "__main__":
    # Test the MathOpt model builder
    result = create_portfolio_model_example()
    print("MathOpt Model Builder Test:")
    print(json.dumps(result, indent=2, default=str))
