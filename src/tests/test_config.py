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
        device="cpu",
        model_size="n",
        cameras=["0"],
    )
    save_config(cfg, cfg_path)

    loaded = load_config(cfg_path)
    assert loaded.dataset.endswith("data")
    assert loaded.device == "cpu"
    assert loaded.model_size == "n"

    update_config(cfg_path, epochs=3, model_size="s")
    updated = load_config(cfg_path)
    assert updated.epochs == 3
    assert updated.model_size == "s"
    assert updated.model.endswith("yolo11s.pt")


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

