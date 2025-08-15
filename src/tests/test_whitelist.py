from pathlib import Path

from midori_ai_hello.whitelist import WhitelistManager


def test_add_and_load_users(tmp_path: Path):
    model = tmp_path / "model.pt"
    model.write_bytes(b"model-weights")
    config_dir = tmp_path / "config"

    manager = WhitelistManager(model_path=model, config_dir=config_dir)
    manager.add_user("alice")
    assert manager.users() == ["alice"]

    # Re-create manager to ensure persistence
    manager2 = WhitelistManager(model_path=model, config_dir=config_dir)
    assert manager2.users() == ["alice"]


def test_uuid_file_persistence(tmp_path: Path):
    model = tmp_path / "model.pt"
    model.write_bytes(b"model-weights")
    config_dir = tmp_path / "config"

    manager = WhitelistManager(model_path=model, config_dir=config_dir)
    manager.add_user("alice")  # trigger key derivation and file creation
    uuid_file = config_dir / "hellouuid.txt"
    assert uuid_file.exists()
    original = uuid_file.read_text()

    manager2 = WhitelistManager(model_path=model, config_dir=config_dir)
    manager2.users()
    assert uuid_file.read_text() == original


def test_hash_mismatch(tmp_path: Path):
    model = tmp_path / "model.pt"
    model.write_bytes(b"model-weights")
    config_dir = tmp_path / "config"

    manager = WhitelistManager(model_path=model, config_dir=config_dir)
    manager.add_user("alice")
    assert manager.is_hash_mismatch() is False

    # Change model weights to trigger mismatch
    model.write_bytes(b"new-model-weights")
    manager_new = WhitelistManager(model_path=model, config_dir=config_dir)
    assert manager_new.is_hash_mismatch() is True

    manager_new.reencrypt()
    assert manager_new.is_hash_mismatch() is False


def test_data_encrypted(tmp_path: Path):
    model = tmp_path / "model.pt"
    model.write_bytes(b"model-weights")
    config_dir = tmp_path / "config"

    manager = WhitelistManager(model_path=model, config_dir=config_dir)
    manager.add_user("alice")

    raw = (config_dir / "whitelist.json").read_text()
    assert "alice" not in raw
