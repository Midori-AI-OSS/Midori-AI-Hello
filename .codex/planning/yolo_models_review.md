# YOLO Model Review Guide

## Repositories
- [Ultralytics](https://github.com/ultralytics/ultralytics) – YOLOv8/YOLO11 suite.
- [WongKinYiu/yolov9](https://github.com/WongKinYiu/yolov9) – YOLOv9 research implementation.

## Training Examples
### Ultralytics
```python
from ultralytics import YOLO
model = YOLO("yolo11n.pt")
train_results = model.train(
    data="coco8.yaml",
    epochs=100,
    imgsz=640,
    device="cpu",
)
```

### YOLOv9
```bash
python train_dual.py --workers 8 --device 0 --batch 16 --data data/coco.yaml \
  --img 640 --cfg models/detect/yolov9-c.yaml --weights '' --name yolov9-c \
  --hyp hyp.scratch-high.yaml --min-items 0 --epochs 500 --close-mosaic 15
```

## Annotation Format
- YOLO labels use one text file per image with lines in the form `class x_center y_center width height`,
  where coordinates are normalized 0–1 relative to image size.
- Ultralytics parses these files via `ultralytics/data/utils.py`; review this module to confirm dataset structure.

## Review Steps for Task Masters
1. Clone the repos and inspect each `README.md` for setup and training instructions.
2. In Ultralytics, examine `ultralytics/models/yolo/detect/train.py` for the `DetectionTrainer` class and its dataset loading.
3. In YOLOv9, review `train_dual.py` for CLI training flags and config dependencies.
4. Check `ultralytics/data/utils.py` to verify label parsing and confirm the annotation format above.
5. Note CPU training options, dataset layouts, and differences in command-line flags or features.
