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


🚀 How to Use
Run the script:

bash
複製
編輯
python your_script_name.py
Load a folder of .jpg images

Choose the number of lines to annotate (e.g. 10 or 30)

Click on the image to mark points (2 points = 1 line)

Once done:

Click 儲存與下一張 to save and go to the next image

Click 跳過錯圖 to move the current image to bad data/ folder

📁 Output Structure
When saving, a folder named like APL_Labels_30/ will be created:

複製
編輯
APL_Labels_30/
├── image01.jpg
├── image01.csv
├── image01.mat
└── ...
Each .csv and .mat file contains the sorted 2N × 2 matrix of keypoints

🛠️ File Structure
File / Class	Description
ImageCanvas	Custom QGraphicsView for image + draw
MainWindow	Main GUI window with control buttons
save_points()	Handles CSV + MAT export logic
skip_and_next()	Moves bad image to bad data/ folder
