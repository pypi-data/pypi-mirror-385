"""
Tests for dynamic field extraction from STFCaseItem
"""

import pytest

from judex.items import STFCaseItem
from judex.output_registry import OutputFormatRegistry


class TestDynamicFieldExtraction:
    """Test dynamic field extraction from STFCaseItem"""

    def test_stf_case_item_fields_exist(self):
        """Test that STFCaseItem has the expected fields"""
        fields = list(STFCaseItem.fields.keys())

        # Check that we have the expected number of fields
        assert len(fields) == 24

        # Check for key fields
        expected_fields = [
            "processo_id",
            "incidente",
            "numero_unico",
            "classe",
            "liminar",
            "tipo_processo",
            "relator",
            "origem",
            "data_protocolo",
            "origem_orgao",
            "autor1",
            "assuntos",
            "partes",
            "andamentos",
            "decisoes",
            "deslocamentos",
            "peticoes",
            "recursos",
            "pautas",
            "informacoes",
            "sessao",
            "status",
            "html",
            "extraido",
        ]

        for field in expected_fields:
            assert field in fields, f"Field '{field}' not found in STFCaseItem"

    def test_csv_format_has_dynamic_fields(self):
        """Test that CSV format uses dynamic field extraction"""
        csv_config = OutputFormatRegistry.get_format("csv")

        assert csv_config is not None
        assert "extra_config" in csv_config
        assert "fields" in csv_config["extra_config"]

        # Check that fields match STFCaseItem fields in class definition order
        csv_fields = csv_config["extra_config"]["fields"]
        from judex.output_registry import get_fields_in_class_order

        expected_fields = get_fields_in_class_order(STFCaseItem)

        assert csv_fields == expected_fields
        assert len(csv_fields) == 24

    def test_json_format_has_dynamic_fields(self):
        """Test that JSON format uses dynamic field extraction"""
        json_config = OutputFormatRegistry.get_format("json")

        assert json_config is not None
        assert "extra_config" in json_config
        assert "fields" in json_config["extra_config"]

        # Check that fields match STFCaseItem fields in class definition order
        json_fields = json_config["extra_config"]["fields"]
        from judex.output_registry import get_fields_in_class_order

        expected_fields = get_fields_in_class_order(STFCaseItem)

        assert json_fields == expected_fields
        assert len(json_fields) == 24

    def test_jsonlines_format_has_dynamic_fields(self):
        """Test that JSONLines format uses dynamic field extraction"""
        jsonlines_config = OutputFormatRegistry.get_format("jsonlines")

        assert jsonlines_config is not None
        assert "extra_config" in jsonlines_config
        assert "fields" in jsonlines_config["extra_config"]

        # Check that fields match STFCaseItem fields in class definition order
        jsonlines_fields = jsonlines_config["extra_config"]["fields"]
        from judex.output_registry import get_fields_in_class_order

        expected_fields = get_fields_in_class_order(STFCaseItem)

        assert jsonlines_fields == expected_fields
        assert len(jsonlines_fields) == 24

    def test_field_order_consistency(self):
        """Test that all formats have the same field order"""
        csv_config = OutputFormatRegistry.get_format("csv")
        json_config = OutputFormatRegistry.get_format("json")
        jsonlines_config = OutputFormatRegistry.get_format("jsonlines")

        csv_fields = csv_config["extra_config"]["fields"]
        json_fields = json_config["extra_config"]["fields"]
        jsonlines_fields = jsonlines_config["extra_config"]["fields"]

        # All formats should have the same field order
        assert csv_fields == json_fields
        assert json_fields == jsonlines_fields
        assert csv_fields == jsonlines_fields

    def test_field_order_matches_item_definition(self):
        """Test that field order matches the order in STFCaseItem class"""
        expected_order = [
            "processo_id",
            "incidente",
            "numero_unico",
            "classe",
            "liminar",
            "tipo_processo",
            "relator",
            "origem",
            "data_protocolo",
            "origem_orgao",
            "autor1",
            "assuntos",
            "partes",
            "andamentos",
            "decisoes",
            "deslocamentos",
            "peticoes",
            "recursos",
            "pautas",
            "informacoes",
            "sessao",
            "status",
            "html",
            "extraido",
        ]

        csv_config = OutputFormatRegistry.get_format("csv")
        actual_fields = csv_config["extra_config"]["fields"]

        assert actual_fields == expected_order

    def test_sql_format_does_not_use_feeds(self):
        """Test that SQL format doesn't use FEEDS (no field ordering needed)"""
        sql_config = OutputFormatRegistry.get_format("sql")

        assert sql_config is not None
        assert sql_config.get("use_feeds", True) is False
        assert "pipeline" in sql_config
        assert sql_config["pipeline"] == "judex.pipelines.DatabasePipeline"

    def test_all_formats_have_required_config(self):
        """Test that all formats have the required configuration"""
        formats = ["csv", "json", "jsonlines", "sql"]

        for format_name in formats:
            config = OutputFormatRegistry.get_format(format_name)
            assert config is not None, f"Format '{format_name}' not found"
            assert "format" in config
            assert "extension" in config
            assert "use_feeds" in config

            if config.get("use_feeds", False):
                assert "extra_config" in config
                assert "fields" in config["extra_config"]

    def test_dynamic_field_extraction_is_live(self):
        """Test that field extraction reflects current STFCaseItem state"""
        # Get fields from registry
        csv_config = OutputFormatRegistry.get_format("csv")
        registry_fields = csv_config["extra_config"]["fields"]

        # Get fields directly from STFCaseItem in class definition order
        from judex.output_registry import get_fields_in_class_order

        item_fields = get_fields_in_class_order(STFCaseItem)

        # They should be identical
        assert registry_fields == item_fields

        # Test that if we modify the item class, the registry reflects it
        # (This is a theoretical test - in practice, the registry is loaded at import time)
        assert len(registry_fields) == len(item_fields)

    def test_field_extraction_handles_empty_item(self):
        """Test that field extraction works even with empty item"""
        # Create a minimal item to test field extraction
        item = STFCaseItem()

        # The item should have all the fields defined in the class
        from judex.output_registry import get_fields_in_class_order

        expected_fields = get_fields_in_class_order(STFCaseItem)
        assert len(expected_fields) == 24

        # All fields should be present in the item's fields dict
        for field in expected_fields:
            assert field in STFCaseItem.fields

    def test_format_registry_consistency(self):
        """Test that format registry maintains consistency"""
        all_formats = OutputFormatRegistry.get_all_formats()

        # Should have all expected formats
        expected_formats = ["json", "csv", "jsonlines", "sql"]
        for format_name in expected_formats:
            assert format_name in all_formats

        # All feed-based formats should have dynamic fields
        feed_formats = ["json", "csv", "jsonlines"]
        for format_name in feed_formats:
            config = all_formats[format_name]
            assert config.get("use_feeds", False) is True
            assert "fields" in config["extra_config"]
            assert len(config["extra_config"]["fields"]) == 24
