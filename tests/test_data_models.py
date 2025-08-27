"""
Unit tests for enhanced data models.
"""

import unittest
from instant_search_db.data_models import Item, ValidationResult, DataStats


class TestItem(unittest.TestCase):
    """Test cases for the Item data model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.item = Item(
            id=1,
            category="武器",
            name="つるはし",
            description="攻 1 買 240 補正 12 売 100 補正 7テ ○掛 拾食 ×フェイ ○変 ○鍛 ×能力 壁を掘れるが、何度か掘ると壊れる",
            custom_fields={
                "attack": 1,
                "price": 240,
                "sellable": True
            }
        )
    
    def test_item_creation(self):
        """Test basic item creation."""
        item = Item()
        self.assertIsNone(item.id)
        self.assertEqual(item.category, "")
        self.assertEqual(item.name, "")
        self.assertEqual(item.description, "")
        self.assertEqual(item.custom_fields, {})
    
    def test_item_creation_with_data(self):
        """Test item creation with data."""
        self.assertEqual(self.item.id, 1)
        self.assertEqual(self.item.category, "武器")
        self.assertEqual(self.item.name, "つるはし")
        self.assertIn("壁を掘れる", self.item.description)
        self.assertEqual(self.item.custom_fields["attack"], 1)
        self.assertEqual(self.item.custom_fields["price"], 240)
        self.assertTrue(self.item.custom_fields["sellable"])
    
    def test_get_display_name_default(self):
        """Test default display name generation."""
        display_name = self.item.get_display_name()
        self.assertEqual(display_name, "武器 つるはし")
    
    def test_get_display_name_name_only(self):
        """Test display name with name only."""
        item = Item(name="テストアイテム")
        display_name = item.get_display_name()
        self.assertEqual(display_name, "テストアイテム")
    
    def test_get_display_name_no_name(self):
        """Test display name with no name."""
        item = Item(id=5)
        display_name = item.get_display_name()
        self.assertEqual(display_name, "Item 5")
    
    def test_get_display_name_no_id(self):
        """Test display name with no name or id."""
        item = Item()
        display_name = item.get_display_name()
        self.assertEqual(display_name, "Unnamed Item")
    
    def test_get_display_name_with_config(self):
        """Test display name with custom format configuration."""
        field_config = {
            "display_format": "{name} (攻撃力: {attack})"
        }
        display_name = self.item.get_display_name(field_config)
        self.assertEqual(display_name, "つるはし (攻撃力: 1)")
    
    def test_get_display_name_invalid_config(self):
        """Test display name with invalid format configuration."""
        field_config = {
            "display_format": "{name} (存在しないフィールド: {nonexistent})"
        }
        # Should fallback to default format
        display_name = self.item.get_display_name(field_config)
        self.assertEqual(display_name, "武器 つるはし")
    
    def test_get_search_text_default(self):
        """Test default search text generation."""
        search_text = self.item.get_search_text()
        self.assertIn("武器", search_text)
        self.assertIn("つるはし", search_text)
        self.assertIn("壁を掘れる", search_text)
    
    def test_get_search_text_custom_fields(self):
        """Test search text with custom fields."""
        search_fields = ["name", "attack", "price"]
        search_text = self.item.get_search_text(search_fields)
        self.assertIn("つるはし", search_text)
        self.assertIn("1", search_text)  # attack value
        self.assertIn("240", search_text)  # price value
        self.assertNotIn("武器", search_text)  # category not included
    
    def test_get_search_text_empty_fields(self):
        """Test search text with empty fields."""
        item = Item(name="テスト")
        search_text = item.get_search_text()
        self.assertEqual(search_text, "テスト")
    
    def test_to_dict_with_custom_fields(self):
        """Test dictionary conversion with custom fields."""
        result = self.item.to_dict()
        expected_keys = {'id', 'category', 'name', 'description', 'attack', 'price', 'sellable'}
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['category'], "武器")
        self.assertEqual(result['name'], "つるはし")
        self.assertEqual(result['attack'], 1)
        self.assertEqual(result['price'], 240)
        self.assertTrue(result['sellable'])
    
    def test_to_dict_without_custom_fields(self):
        """Test dictionary conversion without custom fields."""
        result = self.item.to_dict(include_custom_fields=False)
        expected_keys = {'id', 'category', 'name', 'description'}
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertNotIn('attack', result)
        self.assertNotIn('price', result)
    
    def test_get_field_value_standard_fields(self):
        """Test getting standard field values."""
        self.assertEqual(self.item.get_field_value('id'), 1)
        self.assertEqual(self.item.get_field_value('category'), "武器")
        self.assertEqual(self.item.get_field_value('name'), "つるはし")
        self.assertIn("壁を掘れる", self.item.get_field_value('description'))
    
    def test_get_field_value_custom_fields(self):
        """Test getting custom field values."""
        self.assertEqual(self.item.get_field_value('attack'), 1)
        self.assertEqual(self.item.get_field_value('price'), 240)
        self.assertTrue(self.item.get_field_value('sellable'))
    
    def test_get_field_value_nonexistent(self):
        """Test getting nonexistent field value."""
        self.assertIsNone(self.item.get_field_value('nonexistent'))
    
    def test_set_field_value_standard_fields(self):
        """Test setting standard field values."""
        self.item.set_field_value('id', 2)
        self.item.set_field_value('category', "盾")
        self.item.set_field_value('name', "皮甲の盾")
        self.item.set_field_value('description', "新しい説明")
        
        self.assertEqual(self.item.id, 2)
        self.assertEqual(self.item.category, "盾")
        self.assertEqual(self.item.name, "皮甲の盾")
        self.assertEqual(self.item.description, "新しい説明")
    
    def test_set_field_value_custom_fields(self):
        """Test setting custom field values."""
        self.item.set_field_value('defense', 5)
        self.item.set_field_value('rarity', "rare")
        
        self.assertEqual(self.item.custom_fields['defense'], 5)
        self.assertEqual(self.item.custom_fields['rarity'], "rare")
    
    def test_matches_category(self):
        """Test category matching."""
        self.assertTrue(self.item.matches_category("武器"))
        self.assertFalse(self.item.matches_category("盾"))
        self.assertTrue(self.item.matches_category(""))  # Empty filter matches all
    
    def test_str_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.item), "武器 つるはし")
    
    def test_repr_representation(self):
        """Test developer representation."""
        expected = "Item(id=1, category='武器', name='つるはし')"
        self.assertEqual(repr(self.item), expected)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult."""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])
    
    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors, ["Test error"])
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")
        
        self.assertTrue(result.is_valid)  # Warnings don't affect validity
        self.assertEqual(result.warnings, ["Test warning"])
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = ValidationResult(is_valid=False)
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        
        dict_result = result.to_dict()
        expected = {
            'is_valid': False,
            'errors': ["Error 1"],
            'warnings': ["Warning 1"]
        }
        self.assertEqual(dict_result, expected)


class TestDataStats(unittest.TestCase):
    """Test cases for DataStats."""
    
    def test_data_stats_creation(self):
        """Test DataStats creation."""
        stats = DataStats()
        self.assertEqual(stats.total_items, 0)
        self.assertEqual(stats.categories, {})
        self.assertEqual(stats.fields, [])
        self.assertEqual(stats.custom_fields, [])
    
    def test_data_stats_with_data(self):
        """Test DataStats with data."""
        stats = DataStats(
            total_items=100,
            categories={"武器": 20, "盾": 15},
            fields=["id", "name", "category"],
            custom_fields=["attack", "defense"]
        )
        
        self.assertEqual(stats.total_items, 100)
        self.assertEqual(stats.categories["武器"], 20)
        self.assertEqual(stats.categories["盾"], 15)
        self.assertIn("id", stats.fields)
        self.assertIn("attack", stats.custom_fields)
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        stats = DataStats(
            total_items=50,
            categories={"武器": 10},
            fields=["name"],
            custom_fields=["price"]
        )
        
        dict_result = stats.to_dict()
        expected = {
            'total_items': 50,
            'categories': {"武器": 10},
            'fields': ["name"],
            'custom_fields': ["price"]
        }
        self.assertEqual(dict_result, expected)


if __name__ == '__main__':
    unittest.main()