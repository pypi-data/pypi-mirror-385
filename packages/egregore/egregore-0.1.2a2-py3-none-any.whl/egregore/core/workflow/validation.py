"""
Sequence Validation System

This module provides comprehensive validation for sequences before execution,
including cycle detection, dependency validation, and configuration validation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.base import BaseNode
    from egregore.core.workflow.sequence.base import Sequence


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Base class for validation issues"""
    message: str
    severity: ValidationSeverity
    location: Optional[Any] = None
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.severity.value.upper()}: {self.message}"


@dataclass
class ValidationError(ValidationIssue):
    """Validation error that prevents sequence execution"""
    severity: ValidationSeverity = field(default=ValidationSeverity.ERROR, init=False)


@dataclass
class ValidationWarning(ValidationIssue):
    """Validation warning that doesn't prevent execution but indicates potential issues"""
    severity: ValidationSeverity = field(default=ValidationSeverity.WARNING, init=False)


@dataclass
class ValidationSuggestion(ValidationIssue):
    """Validation suggestion for improvement"""
    severity: ValidationSeverity = field(default=ValidationSeverity.INFO, init=False)


@dataclass
class ValidationResult:
    """Result of sequence validation"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    suggestions: List[ValidationSuggestion] = field(default_factory=list)
    
    def raise_if_invalid(self) -> None:
        """Raise exception if validation failed"""
        if not self.is_valid:
            error_messages = [str(error) for error in self.errors]
            raise ValueError(f"Sequence validation failed:\n" + "\n".join(error_messages))
    
    def get_summary(self) -> str:
        """Get a summary of validation results"""
        status = "VALID" if self.is_valid else "INVALID"
        summary = [f"Validation Status: {status}"]
        
        if self.errors:
            summary.append(f"Errors: {len(self.errors)}")
            for error in self.errors:
                summary.append(f"  - {error}")
        
        if self.warnings:
            summary.append(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                summary.append(f"  - {warning}")
        
        if self.suggestions:
            summary.append(f"Suggestions: {len(self.suggestions)}")
            for suggestion in self.suggestions:
                summary.append(f"  - {suggestion}")
        
        return "\n".join(summary)


class BaseValidator(ABC):
    """Base class for all sequence validators"""
    
    @abstractmethod
    def validate(self, sequence: 'Sequence') -> ValidationResult:
        """Validate the sequence and return results"""
        pass
    
    @property
    @abstractmethod
    def validator_name(self) -> str:
        """Name of this validator"""
        pass


class SequenceValidator:
    """Main sequence validation coordinator"""
    
    def __init__(self):
        self.validators: List[BaseValidator] = []
    
    def add_validator(self, validator: BaseValidator) -> None:
        """Add a validator to the validation pipeline"""
        self.validators.append(validator)
    
    def validate_sequence(self, sequence: 'Sequence') -> ValidationResult:
        """Run all validators on the sequence"""
        
        all_errors = []
        all_warnings = []
        all_suggestions = []
        
        for validator in self.validators:
            try:
                result = validator.validate(sequence)
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)
                all_suggestions.extend(result.suggestions)
            except Exception as e:
                all_errors.append(ValidationError(
                    message=str(e) or "Validator failed",
                    suggestion="Check validator implementation or sequence structure"
                ))
        
        final_result = ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            suggestions=all_suggestions
        )
        
        return final_result
    
    def get_validation_report(self, sequence: 'Sequence') -> str:
        """Get a formatted validation report"""
        result = self.validate_sequence(sequence)
        return result.get_summary()


# Convenience function for quick validation
def validate_sequence(sequence: 'Sequence', validators: Optional[List[BaseValidator]] = None) -> ValidationResult:
    """Convenience function to validate a sequence with default or custom validators"""
    validator = SequenceValidator()
    
    if validators:
        for v in validators:
            validator.add_validator(v)
    else:
        # Add default validators
        from egregore.core.workflow.validators import (
            CycleDetectionValidator, DependencyValidator, SchemaValidator
        )
        validator.add_validator(CycleDetectionValidator())
        validator.add_validator(DependencyValidator())
        validator.add_validator(SchemaValidator())
    
    return validator.validate_sequence(sequence)



def create_default_validator() -> SequenceValidator:
    """Create a validator with all default validators enabled"""
    from egregore.core.workflow.validators import (
        CycleDetectionValidator, DependencyValidator, SchemaValidator
    )
    
    validator = SequenceValidator()
    validator.add_validator(CycleDetectionValidator())
    validator.add_validator(DependencyValidator())
    validator.add_validator(SchemaValidator())
    
    return validator