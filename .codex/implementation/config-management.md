# Configuration management

The application stores settings in ``config.yaml`` using the following keys:

- ``dataset``: root directory for images and labels
- ``epochs``: number of epochs for training runs
- ``batch``: batch size used during training
- ``idle_threshold``: seconds of idle time before training triggers
- ``model``: path to the YOLO model weights
- ``device``: compute device for YOLO operations (``cpu`` or GPU id)
- ``model_size``: YOLO model size key (``n``, ``s``, ``m``, ``l``, ``xl``)
- ``backend``: training backend (``ultralytics`` or other)
- ``cameras``: list of camera IDs (max 20) used for capture and detection
- ``profile_hash`` *(optional)*: path for storing the hash of model weights

Saving the configuration automatically creates camera-specific directories
under ``dataset/images/<camera_id>`` and ``dataset/labels/<camera_id>``.
When ``model_size`` is updated without an explicit ``model`` path, the
filename defaults to ``yolo11{model_size}.pt``.
When ``cameras`` is empty, ``MidoriApp`` calls ``list_cameras()`` to
automatically detect available webcams. Numeric IDs stored as strings are
coerced to integers before opening devices.
