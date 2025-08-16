from pathlib import Path

from midori_ai_hello.config import Config, load_config, save_config, update_config


def test_load_save_update(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.yaml"
    cfg = Config(
        dataset=str(tmp_path / "data"),
        epochs=1,
        batch=2,
        idle_threshold=5,
        model="yolo11n.pt",
        cameras=["0"],
    )
    save_config(cfg, cfg_path)

    loaded = load_config(cfg_path)
    assert loaded.dataset.endswith("data")

    update_config(cfg_path, epochs=3)
    updated = load_config(cfg_path)
    assert updated.epochs == 3


def test_camera_dirs_created(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.yaml"
    data_root = tmp_path / "dataset"
    cfg = Config(
        dataset=str(data_root),
        epochs=1,
        batch=1,
        idle_threshold=0,
        model="yolo11n.pt",
        cameras=["a", "b"],
    )
    save_config(cfg, cfg_path)
    for cam in ["a", "b"]:
        assert (data_root / "images" / cam).is_dir()
        assert (data_root / "labels" / cam).is_dir()

