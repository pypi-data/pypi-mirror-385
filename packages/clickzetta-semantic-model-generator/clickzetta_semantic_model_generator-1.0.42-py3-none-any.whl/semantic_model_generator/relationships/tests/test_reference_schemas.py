from __future__ import annotations

from typing import Iterable, Tuple

from semantic_model_generator.relationships.discovery import (
    RelationshipDiscoveryResult,
    discover_relationships_from_table_definitions,
)


def _discover_relationship_pairs(
    payload: Iterable[dict],
    *,
    min_confidence: float = 0.6,
    max_relationships: int = 50,
) -> Tuple[RelationshipDiscoveryResult, set[Tuple[str, str]]]:
    """Helper that returns discovery result and (left_table, right_table) pairs."""
    result = discover_relationships_from_table_definitions(
        payload,
        min_confidence=min_confidence,
        max_relationships=max_relationships,
    )
    pairs = {(rel.left_table, rel.right_table) for rel in result.relationships}
    return result, pairs


def test_star_schema_fact_orders_links_all_dimensions() -> None:
    """Classic star schema: FACT_ORDERS should link to all surrounding dimensions."""
    payload = [
        {
            "table_name": "dim_customer",
            "columns": [
                {"name": "customer_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "customer_name", "type": "STRING"},
                {"name": "customer_segment", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_product",
            "columns": [
                {"name": "product_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "product_name", "type": "STRING"},
                {"name": "category", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_date",
            "columns": [
                {"name": "date_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "calendar_date", "type": "DATE"},
                {"name": "fiscal_week", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "fact_orders",
            "columns": [
                {"name": "order_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "order_date_key", "type": "NUMBER"},
                {"name": "customer_key", "type": "NUMBER"},
                {"name": "product_key", "type": "NUMBER"},
                {"name": "order_amount", "type": "NUMBER"},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload)

    expected_pairs = {
        ("FACT_ORDERS", "DIM_CUSTOMER"),
        ("FACT_ORDERS", "DIM_PRODUCT"),
        ("FACT_ORDERS", "DIM_DATE"),
    }
    assert expected_pairs <= pairs


def test_tpch_subset_relationships_detected() -> None:
    """Ensure TPC-H style naming is resolved into the expected join graph."""
    payload = [
        {
            "table_name": "customer",
            "columns": [
                {"name": "c_custkey", "type": "NUMBER", "is_primary_key": True},
                {"name": "c_nationkey", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "orders",
            "columns": [
                {"name": "o_orderkey", "type": "NUMBER", "is_primary_key": True},
                {"name": "o_custkey", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "lineitem",
            "columns": [
                {"name": "l_orderkey", "type": "NUMBER", "is_primary_key": True},
                {"name": "l_linenumber", "type": "NUMBER", "is_primary_key": True},
                {"name": "l_partkey", "type": "NUMBER"},
                {"name": "l_suppkey", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "part",
            "columns": [
                {"name": "p_partkey", "type": "NUMBER", "is_primary_key": True},
            ],
        },
        {
            "table_name": "supplier",
            "columns": [
                {"name": "s_suppkey", "type": "NUMBER", "is_primary_key": True},
                {"name": "s_nationkey", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "nation",
            "columns": [
                {"name": "n_nationkey", "type": "NUMBER", "is_primary_key": True},
                {"name": "n_regionkey", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "region",
            "columns": [
                {"name": "r_regionkey", "type": "NUMBER", "is_primary_key": True},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload)

    expected_pairs = {
        ("ORDERS", "CUSTOMER"),
        ("LINEITEM", "ORDERS"),
        ("LINEITEM", "PART"),
        ("LINEITEM", "SUPPLIER"),
        ("SUPPLIER", "NATION"),
        ("CUSTOMER", "NATION"),
        ("NATION", "REGION"),
    }
    assert expected_pairs <= pairs


def test_bridge_table_creates_many_to_many_link() -> None:
    """
    Two-way fact bridge: ORDER_ITEMS joins ORDERS and PRODUCTS and yields derived relationship.
    """
    payload = [
        {
            "table_name": "orders",
            "columns": [
                {"name": "order_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "customer_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "products",
            "columns": [
                {"name": "product_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "sku", "type": "STRING"},
            ],
        },
        {
            "table_name": "order_items",
            "columns": [
                {"name": "order_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "product_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "quantity", "type": "NUMBER"},
            ],
        },
    ]

    result, pairs = _discover_relationship_pairs(payload)

    assert ("ORDER_ITEMS", "ORDERS") in pairs
    assert ("ORDER_ITEMS", "PRODUCTS") in pairs

    # The derived bridge relationship should reference both tables.
    bridge_names = [
        rel.name.lower()
        for rel in result.relationships
        if rel.left_table == "ORDERS" and rel.right_table == "PRODUCTS"
    ]
    assert bridge_names, "Expected derived ORDERS -> PRODUCTS relationship via bridge"
    assert any("order_items" in name or "_via_" in name for name in bridge_names)


def test_snowflake_style_hub_and_spoke() -> None:
    """
    Snowflake-style schema: DIM_CUSTOMER normalized into hub + satellite tables.
    Ensures relationships propagate through hub to satellites.
    """
    payload = [
        {
            "table_name": "dim_customer",
            "columns": [
                {"name": "customer_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "current_address_key", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "dim_customer_attributes",
            "columns": [
                {"name": "customer_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "email", "type": "STRING"},
                {"name": "phone", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_customer_address",
            "columns": [
                {"name": "address_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "street", "type": "STRING"},
                {"name": "city", "type": "STRING"},
            ],
        },
        {
            "table_name": "fact_subscription",
            "columns": [
                {"name": "subscription_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "customer_key", "type": "NUMBER"},
                {"name": "start_date_key", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "dim_date",
            "columns": [
                {"name": "date_key", "type": "NUMBER", "is_primary_key": True},
                {"name": "calendar_date", "type": "DATE"},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload)

    expected_pairs = {
        ("FACT_SUBSCRIPTION", "DIM_CUSTOMER"),
        ("FACT_SUBSCRIPTION", "DIM_DATE"),
        ("DIM_CUSTOMER", "DIM_CUSTOMER_ATTRIBUTES"),
        ("DIM_CUSTOMER", "DIM_CUSTOMER_ADDRESS"),
    }
    assert expected_pairs <= pairs


def test_saas_crm_pipeline_schema() -> None:
    """
    Salesforce/CRM style pipeline: accounts, opportunities, contacts, users.
    Checks that role-based foreign keys go to the right tables.
    """
    payload = [
        {
            "table_name": "accounts",
            "columns": [
                {"name": "account_id", "type": "STRING", "is_primary_key": True},
                {"name": "parent_account_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "opportunities",
            "columns": [
                {"name": "opportunity_id", "type": "STRING", "is_primary_key": True},
                {"name": "account_id", "type": "STRING"},
                {"name": "owner_user_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "contacts",
            "columns": [
                {"name": "contact_id", "type": "STRING", "is_primary_key": True},
                {"name": "account_id", "type": "STRING"},
                {"name": "owner_user_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "users",
            "columns": [
                {"name": "user_id", "type": "STRING", "is_primary_key": True},
                {"name": "manager_id", "type": "STRING"},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload, min_confidence=0.5)

    expected_pairs = {
        ("OPPORTUNITIES", "ACCOUNTS"),
        ("CONTACTS", "ACCOUNTS"),
        ("OPPORTUNITIES", "USERS"),
        ("CONTACTS", "USERS"),
        ("ACCOUNTS", "ACCOUNTS"),  # self-parenting should be ignored
    }
    assert ("OPPORTUNITIES", "ACCOUNTS") in pairs
    assert ("CONTACTS", "ACCOUNTS") in pairs
    assert ("OPPORTUNITIES", "USERS") in pairs
    assert ("CONTACTS", "USERS") in pairs
    # Self relationship must not be created even though parent_account_id exists.
    assert ("ACCOUNTS", "ACCOUNTS") not in pairs


def test_finance_ledger_schema_detects_balanced_relationships() -> None:
    """
    General ledger: journal entries -> journal lines -> accounts, cost centers, employees.
    Ensures composite keys and suffix-based matches work.
    """
    payload = [
        {
            "table_name": "gl_journal_entry",
            "columns": [
                {"name": "journal_entry_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "batch_id", "type": "NUMBER"},
                {"name": "entered_by_employee_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "gl_journal_line",
            "columns": [
                {"name": "journal_entry_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "journal_line_number", "type": "NUMBER", "is_primary_key": True},
                {"name": "account_id", "type": "NUMBER"},
                {"name": "cost_center_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "dim_account",
            "columns": [
                {"name": "account_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "account_type", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_cost_center",
            "columns": [
                {"name": "cost_center_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "division", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_employee",
            "columns": [
                {"name": "employee_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "manager_employee_id", "type": "NUMBER"},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload)

    expected_pairs = {
        ("GL_JOURNAL_LINE", "GL_JOURNAL_ENTRY"),
        ("GL_JOURNAL_LINE", "DIM_ACCOUNT"),
        ("GL_JOURNAL_LINE", "DIM_COST_CENTER"),
        ("GL_JOURNAL_ENTRY", "DIM_EMPLOYEE"),
    }
    assert expected_pairs <= pairs


def test_manufacturing_shop_floor_schema() -> None:
    """
    Manufacturing shop floor: production orders, work orders, machines, BOM components.
    Validates that hierarchical IDs connect correctly across operational tables.
    """
    payload = [
        {
            "table_name": "prod_order",
            "columns": [
                {"name": "prod_order_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "item_id", "type": "NUMBER"},
                {"name": "customer_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "work_order",
            "columns": [
                {"name": "work_order_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "prod_order_id", "type": "NUMBER"},
                {"name": "machine_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "machine",
            "columns": [
                {"name": "machine_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "work_center_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "work_center",
            "columns": [
                {"name": "work_center_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "plant_id", "type": "NUMBER"},
            ],
        },
        {
            "table_name": "bom_component",
            "columns": [
                {"name": "prod_order_id", "type": "NUMBER", "is_primary_key": True},
                {"name": "component_id", "type": "NUMBER", "is_primary_key": True},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload)

    expected_pairs = {
        ("WORK_ORDER", "PROD_ORDER"),
        ("WORK_ORDER", "MACHINE"),
        ("MACHINE", "WORK_CENTER"),
        ("BOM_COMPONENT", "PROD_ORDER"),
    }
    assert expected_pairs <= pairs


def test_marketing_attribution_schema() -> None:
    """
    Multi-touch attribution: campaigns -> channels -> touches -> conversions.
    Verifies that channel/touch relationships align without mis-linking conversions.
    """
    payload = [
        {
            "table_name": "dim_campaign",
            "columns": [
                {"name": "campaign_id", "type": "STRING", "is_primary_key": True},
                {"name": "channel_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_channel",
            "columns": [
                {"name": "channel_id", "type": "STRING", "is_primary_key": True},
                {"name": "parent_channel_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "fact_touch",
            "columns": [
                {"name": "touch_id", "type": "STRING", "is_primary_key": True},
                {"name": "campaign_id", "type": "STRING"},
                {"name": "user_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "fact_conversion",
            "columns": [
                {"name": "conversion_id", "type": "STRING", "is_primary_key": True},
                {"name": "touch_id", "type": "STRING"},
                {"name": "user_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_user",
            "columns": [
                {"name": "user_id", "type": "STRING", "is_primary_key": True},
                {"name": "household_id", "type": "STRING"},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload, min_confidence=0.5)

    expected_pairs = {
        ("FACT_TOUCH", "DIM_CAMPAIGN"),
        ("DIM_CAMPAIGN", "DIM_CHANNEL"),
        ("FACT_TOUCH", "DIM_USER"),
        ("FACT_CONVERSION", "FACT_TOUCH"),
        ("FACT_CONVERSION", "DIM_USER"),
    }
    assert expected_pairs <= pairs
    # Ensure no direct campaign->conversion relationship is assumed.
    assert ("FACT_CONVERSION", "DIM_CAMPAIGN") not in pairs


def test_healthcare_encounter_schema() -> None:
    """
    Healthcare EMR-style model: patients, encounters, providers, diagnoses, procedures.
    Ensures that encounter-level many-to-many tables connect to both sides.
    """
    payload = [
        {
            "table_name": "dim_patient",
            "columns": [
                {"name": "patient_id", "type": "STRING", "is_primary_key": True},
                {"name": "primary_provider_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "dim_provider",
            "columns": [
                {"name": "provider_id", "type": "STRING", "is_primary_key": True},
                {"name": "specialty", "type": "STRING"},
            ],
        },
        {
            "table_name": "fact_encounter",
            "columns": [
                {"name": "encounter_id", "type": "STRING", "is_primary_key": True},
                {"name": "patient_id", "type": "STRING"},
                {"name": "attending_provider_id", "type": "STRING"},
            ],
        },
        {
            "table_name": "fact_encounter_diagnosis",
            "columns": [
                {"name": "encounter_id", "type": "STRING", "is_primary_key": True},
                {"name": "diagnosis_code", "type": "STRING", "is_primary_key": True},
            ],
        },
        {
            "table_name": "dim_diagnosis",
            "columns": [
                {"name": "diagnosis_code", "type": "STRING", "is_primary_key": True},
                {"name": "icd_chapter", "type": "STRING"},
            ],
        },
        {
            "table_name": "fact_encounter_procedure",
            "columns": [
                {"name": "encounter_id", "type": "STRING", "is_primary_key": True},
                {"name": "procedure_code", "type": "STRING", "is_primary_key": True},
            ],
        },
        {
            "table_name": "dim_procedure",
            "columns": [
                {"name": "procedure_code", "type": "STRING", "is_primary_key": True},
                {"name": "category", "type": "STRING"},
            ],
        },
    ]

    _, pairs = _discover_relationship_pairs(payload, min_confidence=0.5)

    expected_pairs = {
        ("FACT_ENCOUNTER", "DIM_PATIENT"),
        ("FACT_ENCOUNTER", "DIM_PROVIDER"),
        ("FACT_ENCOUNTER_DIAGNOSIS", "FACT_ENCOUNTER"),
        ("FACT_ENCOUNTER_DIAGNOSIS", "DIM_DIAGNOSIS"),
        ("FACT_ENCOUNTER_PROCEDURE", "FACT_ENCOUNTER"),
        ("FACT_ENCOUNTER_PROCEDURE", "DIM_PROCEDURE"),
    }
    assert expected_pairs <= pairs
