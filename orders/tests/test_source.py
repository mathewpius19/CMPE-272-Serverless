from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_module_3_files_exist():
    required = [
        ROOT / "template.yaml",
        ROOT / "src/api/order/create/create_order.py",
        ROOT / "src/api/order/list/list_orders.py",
        ROOT / "src/api/order/get/get_order.py",
        ROOT / "src/api/order/edit/edit_order.py",
        ROOT / "src/api/order/cancel/cancel_order.py",
    ]
    assert all(path.is_file() for path in required)


def test_template_contains_idempotency_resources():
    template = (ROOT / "template.yaml").read_text()
    assert "IdempotencyTable:" in template
    assert "IDEMPOTENCY_TABLE_NAME" in template
    assert "AddOrderFunction:" in template
