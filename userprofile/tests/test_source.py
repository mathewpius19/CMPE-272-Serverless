from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_module_4_files_exist():
    required = [
        ROOT / "template.yaml",
        ROOT / "src/api/address/publish/publish_address.py",
        ROOT / "src/api/address/process/process_address.py",
        ROOT / "src/api/address/list/list_addresses.py",
        ROOT / "src/api/favorites/publish/publish_favorite.py",
        ROOT / "src/api/favorites/process/process_favorite.py",
        ROOT / "src/api/favorites/list/list_favorites.py",
    ]
    assert all(path.is_file() for path in required)


def test_template_contains_async_resources():
    template = (ROOT / "template.yaml").read_text()
    for resource in (
        "AddressBus:",
        "FavoriteRestaurantsQueue:",
        "ProcessAddressFunction:",
        "ProcessFavoriteFunction:",
    ):
        assert resource in template
