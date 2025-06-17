from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QComboBox,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap, QPen
from PySide6.QtCore import Qt
import sys, os, csv, numpy as np
from scipy.io import savemat
import shutil

# ---------------- ① 畫布 ---------------- #
class ImageCanvas(QGraphicsView):
    def __init__(self, parent=None, point_num: int = 30):
        super().__init__(parent)
        self.point_num = point_num
        self.setScene(QGraphicsScene(self))
        self.pixmap_item: QGraphicsPixmapItem | None = None
        self.lines, self.current_pts = [], []

    # 影像載入
    def load_image(self, img_path):
        self.scene().clear()
        self.lines.clear(); self.current_pts.clear()
        self.pixmap_item = QGraphicsPixmapItem(QPixmap(img_path))
        self.scene().addItem(self.pixmap_item)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    # 滑鼠點擊
    def mousePressEvent(self, event):
        if self.pixmap_item is None:
            return
        if len(self.lines) >= self.point_num:
            QMessageBox.information(self, "提示", "已標滿點位")
            return

        p = self.mapToScene(event.pos())
        self.current_pts.append((p.x(), p.y()))
        self.scene().addEllipse(p.x()-2, p.y()-2, 4, 4, QPen(Qt.red, 4))

        if len(self.current_pts) == 2:
            p1, p2 = self.current_pts
            self.scene().addLine(p1[0], p1[1], p2[0], p2[1], QPen(Qt.blue, 2))
            self.lines.append((p1, p2))
            self.current_pts = []

# ---------------- ② 主視窗 ---------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spine Marker - Qt 版")

        # 下拉選單
        self.combo = QComboBox()
        self.combo.addItem("10 條線（20 點）", 10)
        self.combo.addItem("30 條線（60 點）", 30)
        self.combo.currentIndexChanged.connect(self.update_point_num)

        # 畫布
        self.canvas = ImageCanvas(point_num=self.combo.currentData())

        # 按鈕
        self.load_btn = QPushButton("載入資料夾")
        self.next_btn = QPushButton("下一張")
        self.save_btn = QPushButton("儲存與下一張")
        self.skip_btn = QPushButton("跳過錯圖")

        self.load_btn.clicked.connect(self.load_folder)
        self.next_btn.clicked.connect(self.next_image)
        self.save_btn.clicked.connect(self.save_and_next)
        self.skip_btn.clicked.connect(self.skip_and_next)

        # 版面配置
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.combo)
        for b in (self.load_btn, self.next_btn, self.save_btn, self.skip_btn):
            btn_layout.addWidget(b)

        central = QWidget(); layout = QVBoxLayout(central)
        layout.addLayout(btn_layout)
        layout.addWidget(self.canvas)
        self.setCentralWidget(central)

        # 影像清單
        self.image_paths, self.idx = [], 0

    # ---------- 功能槽 ---------- #
    def update_point_num(self):
        self.canvas.point_num = self.combo.currentData()

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇 images 資料夾")
        if not folder: return
        self.image_paths = sorted(
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(".jpg")
        )
        if not self.image_paths:
            QMessageBox.warning(self, "錯誤", "找不到 jpg 圖片"); return
        self.idx = 0; self.show_image()

    def show_image(self):
        if self.idx >= len(self.image_paths):
            QMessageBox.information(self, "完成", "已標註所有圖片"); return
        self.canvas.load_image(self.image_paths[self.idx])
        self.setWindowTitle(
            f"[{self.idx+1}/{len(self.image_paths)}] {os.path.basename(self.image_paths[self.idx])}"
        )

    def next_image(self):
        self.idx += 1; self.show_image()

    def save_and_next(self):
        if len(self.canvas.lines) != self.canvas.point_num:
            QMessageBox.warning(self, "尚未完成",
                                f"目前 {len(self.canvas.lines)}/{self.canvas.point_num} 對")
            return
        self.save_points(); self.next_image()

    def skip_and_next(self):
        img = self.image_paths[self.idx]
        bad_dir = os.path.join(os.path.dirname(img), "bad data")
        os.makedirs(bad_dir, exist_ok=True)
        os.replace(img, os.path.join(bad_dir, os.path.basename(img)))
        self.next_image()

    # ---------- 儲存 ---------- #
    def save_points(self):
        img_path = self.image_paths[self.idx]
        base = os.path.splitext(os.path.basename(img_path))[0]
        save_dir = f"APL_Labels_{self.canvas.point_num}"
        os.makedirs(save_dir, exist_ok=True)
        csv_path = os.path.join(save_dir, base + ".csv")
        mat_path = os.path.join(save_dir, base + ".mat")

        # 取得左右點
        pts   = self.canvas.lines
        left  = np.array([p1 for p1, _ in pts])
        right = np.array([p2 for _, p2 in pts])

        # 左右交換 (保證 left 在左側)
        swap = left[:, 0] > right[:, 0]
        left[swap], right[swap] = right[swap], left[swap]

        # 依 y 座標排序
        order = np.argsort(left[:, 1])
        left, right = left[order], right[order]

        # 合併為 2N x 2 的格式
        points = np.vstack([left, right])  # shape = (2N, 2)

        # 儲存 CSV
        with open(csv_path, 'w', newline='') as f:
            csv.writer(f).writerows(points)

        # 儲存 MAT
        savemat(mat_path, {'p2': points})  # shape = (2N, 2)
        print("✅ 已儲存：", csv_path, mat_path)

            # 把原圖複製（或搬移）到 label 資料夾，保證 .jpg 與 .mat 同層
        dst_path = os.path.join(save_dir, os.path.basename(img_path))
        if not os.path.exists(dst_path):
            # ✅ 推薦：先「複製」保留備份；若你確定要搬走，可改用 shutil.move
            shutil.copy2(img_path, dst_path)
            print("📁 已複製原圖到 label 資料夾：", dst_path)
        else:
            print("⚠️  目標已存在同名圖片，已跳過複製")



# ----------------- 入口 ----------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow(); win.resize(1200, 800); win.show()
    sys.exit(app.exec())
