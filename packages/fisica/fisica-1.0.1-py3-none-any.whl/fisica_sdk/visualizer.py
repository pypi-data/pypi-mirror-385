import cv2
import numpy as np
from typing import Union
from PIL import Image, ImageDraw, ImageFont
from .analyzer import pca_bounding_box_dimensions
from .gui_viewer import update_gui
from .utils import log


def render(grid_data: np.ndarray, mode: str = 'BLUR', bbox: bool = False, scale: float = 1.0) -> Union[np.ndarray, bytes, list]:
    vis = Visualizer()
    vis.scale(scale)
    return vis.render(grid_data, mode, bbox)

class VisualOptions:
    """
    Fisica SDK : VisualOptions
        Available rendering modes FisicaSDK.render():
            - PIXEL: Color-mapped pixel
            - BLUR: Smoothly rendered
            - BINARY: Text grid of values
            - BINARY_NONZERO: Text grid hiding zero values
            - CONTOUR: Contour outline of foot shape
            - ALL: Return all in a list.
    """

    ALL    = 'ALL'
    PIXEL  = 'PIXEL'
    BLUR   = 'BLUR'
    BINARY = 'BINARY'
    BINARY_NONZERO = 'BINARY_NONZERO'
    CONTOUR = 'CONTOUR'

class Visualizer:
    def __init__(self):
        self._scale = 1.0  # default scale

    def scale(self, factor: float):
        self._scale = factor

    def _render_with_transparency(self, grid_data: np.ndarray, bbox: bool) -> np.ndarray:

        grid_norm = ((grid_data - np.min(grid_data)) / (np.max(grid_data) - np.min(grid_data)) * 255).astype(np.uint8)
        heatmap = cv2.resize(grid_norm, (456, 512), interpolation=cv2.INTER_LINEAR)
        heatmap_blurred = cv2.GaussianBlur(heatmap, (21, 21), 0)

        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(heatmap_blurred, -1, kernel)

        dst = cv2.applyColorMap(heatmap_blurred, cv2.COLORMAP_JET)
        alpha = np.ones(dst.shape[:2], dtype=np.uint8) * 255
        alpha[heatmap_blurred == np.min(heatmap_blurred)] = 0
        rgba = cv2.cvtColor(dst, cv2.COLOR_BGR2BGRA)
        rgba[:, :, 3] = alpha
        rgba[sharpened < 10, 3] = 0
        rgba = cv2.cvtColor(dst, cv2.COLOR_BGRA2BGR)

        scale = self._scale
        target_size = (int(456 * scale), int(512 * scale))
        rgba_resized = cv2.resize(rgba, target_size, interpolation=cv2.INTER_LINEAR)
        if bbox:
            rgba_resized = self._render_bbox(grid_data, rgba_resized)

        return rgba_resized


    def _render_pixel(self, grid_data: np.ndarray, bbox: bool) -> np.ndarray:
        try:
            grid_norm = ((grid_data - np.min(grid_data)) / (np.max(grid_data) - np.min(grid_data)) * 255).astype(np.uint8)
        except Exception as e:
            log.critical(
                "\n\nFisica SDK\n"
                f"   There seems to be a problem with processing the matrix: {e}\n"
            )
            raise e
        img = cv2.resize(cv2.applyColorMap(grid_norm, cv2.COLORMAP_JET), (456, 512), interpolation=cv2.INTER_NEAREST)

        scale = self._scale
        target_size = (int(456 * scale), int(512 * scale))
        img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_NEAREST)

        if bbox:
            self._render_bbox(grid_data, img_resized)

        return img_resized

    def _render_binary(self, grid_data: np.ndarray, bbox_x:bool, hide_zeros: bool = False) -> np.ndarray:
        rows, cols = grid_data.shape
        base_w, base_h = 456, 512
        cell_w = base_w // cols
        cell_h = base_h // rows

        image = Image.new("RGB", (base_w, base_h), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        try:
            font_size = int(min(cell_w, cell_h) * 0.8)
            font = ImageFont.truetype("SansSerif.ttf", font_size)
        except IOError:
            log.warning("TrueType font not found. Falling back to default font.")
            font = ImageFont.load_default()

        for i in range(rows):
            for j in range(cols):
                val = int(grid_data[i, j])
                if hide_zeros and val == 0:
                    continue
                text = str(val)
                bbox = font.getbbox(text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = j * cell_w + 8 + (cell_w - text_width) // 2
                y = i * cell_h + (cell_h - text_height) // 2
                draw.text((x, y), text, fill=(255, 255, 255), font=font)

        scale = self._scale
        target_size = (int(base_w * scale), int(base_h * scale))
        image_resized = image.resize(target_size, resample=Image.BICUBIC)
        final_image = cv2.cvtColor(np.array(image_resized), cv2.COLOR_RGB2BGR)
        if bbox_x:
            final_image = self._render_bbox(grid_data, final_image)

        return final_image

    def _render_bbox(self, grid_data: np.ndarray, img:np.ndarray) -> np.ndarray:
        rows, cols = grid_data.shape
        h, w = img.shape[:2]
        cell_w = w / cols
        cell_h = h / rows
        def draw_pca_box(subgrid, col_offset, color):
            pts_idx = np.argwhere(subgrid > 0)
            if pts_idx.size == 0:
                return
            pts_idx = pts_idx.copy()
            pts_idx[:,1] += col_offset
            pts = np.stack([
                pts_idx[:,1] * cell_w + cell_w/2,
                pts_idx[:,0] * cell_h + cell_h/2
            ], axis=1)
            width, length, cx, cy = pca_bounding_box_dimensions(pts, cell_w, cell_h)
            center = np.array([cx, cy])
            cov = np.cov(pts, rowvar=False)
            eigvals, eigvecs = np.linalg.eigh(cov)
            principal = eigvecs[:, eigvals.argmax()]
            secondary = eigvecs[:, eigvals.argmin()]
            half_len = length / 2
            half_wid = width / 2
            corners = np.array([
                center + principal*half_len + secondary*half_wid,
                center + principal*half_len - secondary*half_wid,
                center - principal*half_len - secondary*half_wid,
                center - principal*half_len + secondary*half_wid
            ]).astype(int)
            cv2.polylines(img, [corners], True, color, 2)

        mid = cols // 2
        draw_pca_box(grid_data[:, :mid], 0, (0,255,0))
        draw_pca_box(grid_data[:, mid:], mid, (255,0,0))

        return img


    def _render_contour(self, grid_data: np.ndarray, bbox: bool) -> np.ndarray:
        img = self._render_pixel(grid_data, False)
        mask = (grid_data > 0).astype(np.uint8) * 255
        h, w = img.shape[:2]
        mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img, contours, -1, (0,0,255), 2)
        if bbox:
            img = self._render_bbox(grid_data, img)
            
        return img

    def render(self, grid_data: np.ndarray, mode: str, bbox: bool) -> Union[np.ndarray, bytes, list]:
        if mode == VisualOptions.PIXEL:
            return self._render_pixel(grid_data, bbox)
        elif mode == VisualOptions.BLUR:
            return self._render_with_transparency(grid_data, bbox)
        elif mode == VisualOptions.BINARY:
            return self._render_binary(grid_data, bbox)
        elif mode == VisualOptions.BINARY_NONZERO:
            return self._render_binary(grid_data, bbox, hide_zeros=True)
        elif mode == VisualOptions.CONTOUR:
            return self._render_contour(grid_data, bbox)
        elif mode == VisualOptions.ALL:
            pixel_img_for_bbox = self._render_pixel(grid_data, bbox=False)
            return [
                self._render_pixel(grid_data, bbox),
                self._render_with_transparency(grid_data, bbox),
                self._render_binary(grid_data, bbox),
                self._render_binary(grid_data, bbox, hide_zeros=True),
                self._render_bbox(grid_data, pixel_img_for_bbox),
                self._render_contour(grid_data, bbox)
            ]
        else:
            raise ValueError(f"Unsupported rendering mode: {mode}")

    def update(self, image: np.ndarray):
        update_gui(image)

    def run(self, scale=1.0):
        from .gui_viewer import sys, setup_gui
        app = setup_gui(scale)
        sys.exit(app.exec_())
