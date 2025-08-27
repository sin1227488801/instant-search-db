"""
Enhanced data models for the generic database system.
Provides flexible Item model with custom field support.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json


@dataclass
class Item:
    """
    Enhanced Item model with flexible field mapping support.
    
    This model supports both standard fields (id, category, name, description)
    and custom fields defined through configuration.
    """
    id: Optional[int] = None
    category: str = ""
    name: str = ""
    description: str = ""
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def get_display_name(self, field_config: Optional[Dict] = None) -> str:
        """
        Get the display name for this item based on configuration.
        
        Args:
            field_config: Field configuration dictionary
            
        Returns:
            Formatted display name string
        """
        if field_config and 'display_format' in field_config:
            # Use configured display format
            format_str = field_config['display_format']
            try:
                return format_str.format(
                    category=self.category,
                    name=self.name,
                    description=self.description,
                    **self.custom_fields
                )
            except (KeyError, ValueError):
                # Fallback to default format if formatting fails
                pass
        
        # Default display format
        if self.category and self.name:
            return f"{self.category} {self.name}"
        elif self.name:
            return self.name
        else:
            return f"Item {self.id}" if self.id else "Unnamed Item"
    
    def get_search_text(self, search_fields: Optional[List[str]] = None) -> str:
        """
        Get searchable text content for this item.
        
        Args:
            search_fields: List of field names to include in search text
            
        Returns:
            Combined search text string
        """
        if search_fields is None:
            search_fields = ['category', 'name', 'description']
        
        search_parts = []
        
        # Add standard fields
        for field_name in search_fields:
            if field_name == 'category' and self.category:
                search_parts.append(self.category)
            elif field_name == 'name' and self.name:
                search_parts.append(self.name)
            elif field_name == 'description' and self.description:
                search_parts.append(self.description)
            elif field_name in self.custom_fields:
                # Add custom field value
                value = self.custom_fields[field_name]
                if value is not None:
                    search_parts.append(str(value))
        
        return ' '.join(search_parts)
    
    def to_dict(self, include_custom_fields: bool = True) -> Dict[str, Any]:
        """
        Convert item to dictionary representation.
        
        Args:
            include_custom_fields: Whether to include custom fields in output
            
        Returns:
            Dictionary representation of the item
        """
        result = {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'description': self.description
        }
        
        if include_custom_fields and self.custom_fields:
            result.update(self.custom_fields)
        
        return result
    
    def get_field_value(self, field_name: str) -> Any:
        """
        Get value of a field (standard or custom).
        
        Args:
            field_name: Name of the field to retrieve
            
        Returns:
            Field value or None if not found
        """
        if field_name == 'id':
            return self.id
        elif field_name == 'category':
            return self.category
        elif field_name == 'name':
            return self.name
        elif field_name == 'description':
            return self.description
        elif field_name in self.custom_fields:
            return self.custom_fields[field_name]
        else:
            return None
    
    def set_field_value(self, field_name: str, value: Any) -> None:
        """
        Set value of a field (standard or custom).
        
        Args:
            field_name: Name of the field to set
            value: Value to set
        """
        if field_name == 'id':
            self.id = value
        elif field_name == 'category':
            self.category = value
        elif field_name == 'name':
            self.name = value
        elif field_name == 'description':
            self.description = value
        else:
            self.custom_fields[field_name] = value
    
    def matches_category(self, category_filter: str) -> bool:
        """
        Check if item matches a category filter.
        
        Args:
            category_filter: Category to filter by
            
        Returns:
            True if item matches the category
        """
        if not category_filter:
            return True
        return self.category == category_filter
    
    def __str__(self) -> str:
        """String representation of the item."""
        return self.get_display_name()
    
    def __repr__(self) -> str:
        """Developer representation of the item."""
        return f"Item(id={self.id}, category='{self.category}', name='{self.name}')"


@dataclass
class ValidationResult:
    """Result of data validation operation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


@dataclass
class DataStats:
    """Statistics about loaded data."""
    total_items: int = 0
    categories: Dict[str, int] = field(default_factory=dict)
    fields: List[str] = field(default_factory=list)
    custom_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'total_items': self.total_items,
            'categories': self.categories,
            'fields': self.fields,
            'custom_fields': self.custom_fields
        }