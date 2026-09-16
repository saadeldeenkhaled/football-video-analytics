# Football AI Analytics

A modular football video analysis prototype. It detects people with an Ultralytics YOLO model, assigns coarse jersey-colour labels, tracks player centroids, estimates movement metrics, and writes an annotated MP4 through a Gradio interface.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The default model is `yolo11n.pt`; Ultralytics downloads it on first use. Set `FOOTBALL_MODEL` to a local model path when required.

## Validation

```powershell
python -m unittest discover -s tests -v
```

The pixel-to-metre scale is a configurable approximation. For reliable match metrics, replace it with a pitch homography calibrated from known field points.