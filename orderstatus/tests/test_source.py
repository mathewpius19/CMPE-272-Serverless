from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_module_5_files_exist():
    required = [
        ROOT / "template.yaml",
        ROOT / "polling-api.sh",
        ROOT / "publish-update.sh",
        ROOT / "src/api/create/create_order.py",
        ROOT / "src/api/status/get_order_status.py",
        ROOT / "src/api/update/update_order_status.py",
    ]
    assert all(path.is_file() for path in required)


def test_template_contains_polling_resources():
    template = (ROOT / "template.yaml").read_text()
    for resource in (
        "RestaurantBus:",
        "OrdersTable:",
        "GetOrderStatusFunction:",
        "UpdateOrderStatusFunction:",
    ):
        assert resource in template
