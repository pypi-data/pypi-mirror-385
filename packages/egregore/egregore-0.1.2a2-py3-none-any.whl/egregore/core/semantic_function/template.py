"""Jinja2-powered template engine for semantic functions."""

from typing import Dict, Any
from jinja2 import Template, Environment, StrictUndefined, meta
from jinja2.exceptions import TemplateError, UndefinedError

def render_template(template: str, **kwargs) -> str:
    """Render Jinja2 template with variable substitution.
    
    Args:
        template: Jinja2 template string
        **kwargs: Variables to substitute
        
    Returns:
        Rendered template with variables substituted
        
    Raises:
        ValueError: If template contains undefined variables or syntax errors
    """
    if not template:
        return template
    
    try:
        # Create Jinja2 template with strict undefined checking
        env = Environment(undefined=StrictUndefined)
        jinja_template = env.from_string(template)
        
        # Render with provided variables
        return jinja_template.render(**kwargs)
        
    except UndefinedError as e:
        # Use enhanced error messaging system
        try:
            from ..errors.enhanced_messages import ErrorMessageEnhancer, format_enhanced_error
            
            enhancer = ErrorMessageEnhancer()
            available_vars = list(kwargs.keys()) if kwargs else []
            
            enhanced_error = enhancer.enhance_template_error(
                error_msg=str(e),
                template=template,
                available_vars=available_vars,
                context={"template": template, "provided_vars": kwargs}
            )
            
            formatted_error = format_enhanced_error(enhanced_error)
            raise ValueError(f"\n{formatted_error}")
            
        except ImportError:
            # Fallback to improved simple error handling
            error_msg = str(e)
            if "'" in error_msg:
                # Try to extract variable name from error like "'variable_name' is undefined"
                parts = error_msg.split("'")
                if len(parts) >= 2:
                    undefined_var = parts[1]
                    available_vars = list(kwargs.keys()) if kwargs else []
                    if available_vars:
                        raise ValueError(f"Template variable '{undefined_var}' is undefined. Available variables: {available_vars}")
                    else:
                        raise ValueError(f"Template variable '{undefined_var}' is undefined. No variables provided.")
            # Fallback to generic error
            raise ValueError(f"Template contains undefined variables: {error_msg}")
    except TemplateError as e:
        # Handle other Jinja2 template errors
        raise ValueError(f"Template syntax error: {str(e)}")
    except Exception as e:
        # Handle any other rendering errors
        raise ValueError(f"Template rendering failed: {str(e)}")

def extract_template_variables(template: str) -> list[str]:
    """Extract variable names from Jinja2 template.
    
    Args:
        template: Jinja2 template string
        
    Returns:
        List of variable names found in template
        
    Raises:
        ValueError: If template has invalid Jinja2 syntax
    """
    if not template:
        return []
    
    try:
        # Use Jinja2's meta module to extract variable names - strict compliance only
        env = Environment()
        ast = env.parse(template)
        variables = meta.find_undeclared_variables(ast)
        return list(variables)
    except TemplateError as e:
        # Strict Jinja2 compliance - raise error if parsing fails
        raise ValueError(f"Invalid Jinja2 template syntax: {str(e)}")
    except Exception as e:
        raise ValueError(f"Template parsing failed: {str(e)}")

def validate_template(template: str) -> tuple[bool, list[str]]:
    """Validate Jinja2 template syntax.
    
    Args:
        template: Jinja2 template string to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    if not template:
        return True, []
    
    errors = []
    
    try:
        # Use Jinja2 to validate template syntax
        env = Environment(undefined=StrictUndefined)
        env.from_string(template)
        
        # Additional validation: ensure we can extract variables
        try:
            extract_template_variables(template)
        except Exception as e:
            errors.append(f"Variable extraction failed: {str(e)}")
            
    except TemplateError as e:
        errors.append(f"Jinja2 template syntax error: {str(e)}")
    except Exception as e:
        errors.append(f"Template validation failed: {str(e)}")
    
    return len(errors) == 0, errors