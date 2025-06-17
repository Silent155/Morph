# Spine Marker - Qt Version

🦴 A simple GUI tool for manually annotating spinal midline keypoints from X-ray images.  
Built with `PySide6`, supports saving annotations to `.csv` and `.mat` format.

---

## 🖼️ Features

- ✅ Load a folder of `.jpg` images
- ✅ Manually label spinal lines (2 points per line)
- ✅ Auto-sort keypoints by vertical position
- ✅ Export results to:
  - CSV (`[left_point, right_point] x N`)
  - MATLAB `.mat` file (`p2` matrix)
- ✅ Copies labeled images into a dedicated folder
- ✅ "Skip" bad images into a separate folder (`bad data/`)

---

## 📦 Requirements

```bash
pip install PySide6 numpy scipy


