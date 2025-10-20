#!/usr/bin/env python3
"""
TIFF Viewer (PySide6) — RGB (2–98% global stretch) + Shapefile overlays

Features
- Open GeoTIFFs (single or multi-band)
- Combine separate single-band TIFFs into RGB (--rgbfiles R.tif G.tif B.tif)
- QGIS-like RGB display using global 2–98 percentile stretch
- Single-band view with contrast/gamma + colormap toggle (viridis <-> magma)
- Pan & zoom
- Switch bands with [ and ] (single-band)
- Overlay one or more shapefiles reprojected to raster CRS
- Z/M tolerant: ignores Z or M coords in shapefiles

Controls
  + / - : zoom in/out
  Arrow keys or WASD : pan
  C / V : increase/decrease contrast (works in RGB and single-band)
  G / H : increase/decrease gamma    (works in RGB and single-band)
  M     : toggle colormap (viridis <-> magma) — single-band only
  [ / ] : previous / next band (single-band)
  R     : reset view

Examples
  python tiff_viewer.py my.tif --band 1
  python tiff_viewer.py my_multiband.tif --rgb 4 3 2
  python tiff_viewer.py --rgbfiles B4.tif B3.tif B2.tif --shapefile coast.shp counties.shp --shp-color cyan --shp-width 1.8
"""

import sys
import os
import argparse
import numpy as np
import rasterio
from rasterio.transform import Affine
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QScrollBar, QGraphicsPathItem
)
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt

import matplotlib.cm as cm

# Optional overlay deps
try:
    import geopandas as gpd
    from shapely.geometry import (
        LineString, MultiLineString, Polygon, MultiPolygon,
        GeometryCollection, Point, MultiPoint
    )
    HAVE_GEO = True
except Exception:
    HAVE_GEO = False

def warn_if_large(tif_path, scale=1):
    """Warn and confirm before loading very large rasters (GeoTIFF, GDB, or HDF).
    Works even if GDAL is not installed.
    """
    import os
    width = height = None
    size_mb = None

    # Try GDAL if available
    try:
        from osgeo import gdal
        gdal.UseExceptions()
        info = gdal.Info(tif_path, format="json")
        width, height = info.get("size", [0, 0])
    except ImportError:
        # Fallback if GDAL not installed
        try:
            import rasterio
            with rasterio.open(tif_path) as src:
                width, height = src.width, src.height
        except Exception:
            print("[WARN] Could not estimate raster size (no GDAL/rasterio). Skipping size check.")
            return
    except Exception as e:
        print(f"[WARN] Could not pre-check raster size with GDAL: {e}")
        return

    # File size
    if os.path.exists(tif_path):
        size_mb = os.path.getsize(tif_path) / (1024 ** 2)

    total_pixels = (width * height) / (scale ** 2)
    if total_pixels > 20_000_000 and scale <= 5:
        msg = (
            f"[WARN] Large raster detected ({width}×{height}, ~{total_pixels/1e6:.1f}M pixels"
            + (f", ~{size_mb:.1f} MB" if size_mb else "")
            + "). Loading may freeze. Consider --scale (e.g. --scale 10)."
        )
        print(msg)
        ans = input("Proceed anyway? [y/N]: ").strip().lower()
        if ans not in ("y", "yes"):
            print("Cancelled.")
            sys.exit(0)

# -------------------------- QGraphicsView tweaks -------------------------- #
class RasterView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._wheel_zoom_step = 1.2

    def wheelEvent(self, event):
        """Zoom in/out centered at the cursor position.

        Uses a multiplicative scale per 15° wheel step.
        """
        delta = event.angleDelta().y()
        if delta == 0:
            # Trackpads may report pixelDelta; fall back to it if angleDelta is 0
            pixel_delta = event.pixelDelta().y()
            delta = pixel_delta

        if delta == 0:
            event.ignore()
            return

        steps = delta / 120.0  # 120 units per 15° step
        if steps > 0:
            factor = self._wheel_zoom_step ** steps
        else:
            factor = (1.0 / self._wheel_zoom_step) ** (-steps)

        self.scale(factor, factor)
        event.accept()


# ------------------------------- Main Window ------------------------------ #
class TiffViewer(QMainWindow):
    def __init__(
        self,
        tif_path: str | None,
        scale: int = 1,
        band: int = 1,
        rgb: list[int] | None = None,
        rgbfiles: list[str] | None = None,
        shapefiles: list[str] | None = None,
        shp_color: str = "white",
        shp_width: float = 2,
        subset: int | None = None,
    ):
        super().__init__()

        self.tif_path = tif_path or ""
        self.rgb_mode = rgb is not None or rgbfiles is not None
        self.band = int(band)
        self.rgb = rgb
        self.rgbfiles = rgbfiles

        self._scale_arg = max(1, int(scale or 1))
        self._transform: Affine | None = None
        self._crs = None

        # Overlay config/state
        self._shapefiles = shapefiles or []
        self._shp_color = shp_color
        self._shp_width = float(shp_width)
        self._overlay_items: list[QGraphicsPathItem] = []

        # --- Load data ---
        if rgbfiles:
            red, green, blue = rgbfiles
            with rasterio.open(red) as r, rasterio.open(green) as g, rasterio.open(blue) as b:
                if (r.width, r.height) != (g.width, g.height) or (r.width, r.height) != (b.width, b.height):
                    raise ValueError("All RGB files must have the same dimensions.")
                arr = np.stack([
                    r.read(1, out_shape=(r.height // self._scale_arg, r.width // self._scale_arg)),
                    g.read(1, out_shape=(g.height // self._scale_arg, g.width // self._scale_arg)),
                    b.read(1, out_shape=(b.height // self._scale_arg, b.width // self._scale_arg))
                ], axis=-1).astype(np.float32)
                self._transform = r.transform
                self._crs = r.crs

            self.data = arr
            self.band_count = 3
            self.rgb = [os.path.basename(red), os.path.basename(green), os.path.basename(blue)]
            # Use common prefix for title if tif_path not passed
            self.tif_path = self.tif_path or (os.path.commonprefix([red, green, blue]) or red)

        elif tif_path:
            # ---------------- Handle File Geodatabase (.gdb) ---------------- #
            if tif_path.lower().endswith(".gdb") and ":" not in tif_path:
                import re, subprocess
                gdb_path = tif_path  # use full path to .gdb
                try:
                    out = subprocess.check_output(["gdalinfo", "-norat", gdb_path], text=True)
                    rasters = re.findall(r"RASTER_DATASET=(\S+)", out)
                    if not rasters:
                        print(f"[WARN] No raster datasets found in {os.path.basename(gdb_path)}.")
                        sys.exit(0)
                    else:
                        print(f"Found {len(rasters)} raster dataset{'s' if len(rasters) > 1 else ''}:")
                        for i, r in enumerate(rasters):
                            print(f"[{i}] {r}")
                        print("\nUse one of these names to open. For example, to open the first raster:")
                        print(f'viewtif "OpenFileGDB:{gdb_path}:{rasters[0]}"')
                        sys.exit(0)
                except subprocess.CalledProcessError as e:
                    print(f"[WARN] Could not inspect FileGDB: {e}")
                    sys.exit(0)

            # --- Universal size check before loading ---
            warn_if_large(tif_path, scale=self._scale_arg)

            # --------------------- Detect HDF/HDF5 --------------------- #
            if tif_path.lower().endswith((".hdf", ".h5", ".hdf5")):
                try:
                    # Try reading directly with Rasterio first (works for simple HDF layouts)
                    with rasterio.open(tif_path) as src:
                        print(f"Opened HDF with rasterio: {os.path.basename(tif_path)}")
                        arr = src.read().astype(np.float32)
                        arr = np.squeeze(arr)
                        if arr.ndim == 3:
                            arr = np.transpose(arr, (1, 2, 0))
                        elif arr.ndim == 2:
                            print("Single-band dataset.")
                        self.data = arr
                        self._transform = src.transform
                        self._crs = src.crs
                        self.band_count = arr.shape[2] if arr.ndim == 3 else 1
                        self.band_index = 0
                        self.vmin, self.vmax = np.nanmin(arr), np.nanmax(arr)
                        return  # ✅ Skip GDAL path if Rasterio succeeded

                except Exception as e:
                    print(f"Rasterio could not open HDF directly: {e}")
                    print("Falling back to GDAL...")

                    try:
                        from osgeo import gdal
                        gdal.UseExceptions()

                        ds = gdal.Open(tif_path)
                        subs = ds.GetSubDatasets()
                        if not subs:
                            raise ValueError("No subdatasets found in HDF/HDF5 file.")

                        print(f"Found {len(subs)} subdatasets in {os.path.basename(tif_path)}:")
                        for i, (_, desc) in enumerate(subs):
                            print(f"[{i}] {desc}")

                        if subset is None:
                            print("\nUse --subset N to open a specific subdataset.")
                            sys.exit(0)

                        if subset < 0 or subset >= len(subs):
                            raise ValueError(f"Invalid subset index {subset}. Valid range: 0–{len(subs)-1}")

                        sub_name, desc = subs[subset]
                        print(f"\nOpening subdataset [{subset}]: {desc}")
                        sub_ds = gdal.Open(sub_name)

                        arr = sub_ds.ReadAsArray().astype(np.float32)
                        arr = np.squeeze(arr)
                        if arr.ndim == 3:
                            arr = np.transpose(arr, (1, 2, 0))
                        elif arr.ndim == 2:
                            print("Single-band dataset.")
                        else:
                            raise ValueError(f"Unexpected array shape {arr.shape}")

                        # Downsample large arrays for responsiveness
                        h, w = arr.shape[:2]
                        if h * w > 4_000_000:
                            step = max(2, int((h * w / 4_000_000) ** 0.5))
                            arr = arr[::step, ::step] if arr.ndim == 2 else arr[::step, ::step, :]
                            print(f"⚠️ Large dataset preview: downsampled by {step}x")

                        # Assign
                        self.data = arr
                        self._transform = None
                        self._crs = None
                        self.band_count = arr.shape[2] if arr.ndim == 3 else 1
                        self.band_index = 0
                        self.vmin, self.vmax = np.nanmin(arr), np.nanmax(arr)

                        if self.band_count > 1:
                            print(f"This subdataset has {self.band_count} bands — switch with [ and ] keys.")
                        else:
                            print("This subdataset has 1 band.")

                        if self.band and self.band <= self.band_count:
                            self.band_index = self.band - 1
                            print(f"Opening band {self.band}/{self.band_count}")

                    except ImportError:
                        raise RuntimeError(
                            "HDF/HDF5 support requires GDAL (Python bindings).\n"
                            "Install it first (e.g., brew install gdal && pip install GDAL)"
                        )

            # --------------------- Regular GeoTIFF --------------------- #
            else:
                if os.path.dirname(tif_path).endswith(".gdb"):
                    tif_path = f"OpenFileGDB:{os.path.dirname(tif_path)}:{os.path.basename(tif_path)}"

                with rasterio.open(tif_path) as src:
                    self._transform = src.transform
                    self._crs = src.crs
                    if rgb is not None:
                        bands = [src.read(b, out_shape=(src.height // self._scale_arg, src.width // self._scale_arg))
                                for b in rgb]
                        arr = np.stack(bands, axis=-1).astype(np.float32)
                        nd = src.nodata
                        if nd is not None:
                            arr[arr == nd] = np.nan
                        self.data = arr
                        self.band_count = 3
                    else:
                        arr = src.read(
                            self.band,
                            out_shape=(src.height // self._scale_arg, src.width // self._scale_arg)
                        ).astype(np.float32)
                        nd = src.nodata
                        if nd is not None:
                            arr[arr == nd] = np.nan
                        self.data = arr
                        self.band_count = src.count

                        # single-band display range (fast stats or fallback)
                        try:
                            stats = src.stats(self.band)
                            if stats and stats.min is not None and stats.max is not None:
                                self.vmin, self.vmax = stats.min, stats.max
                            else:
                                raise ValueError("No stats in file")
                        except Exception:
                            self.vmin, self.vmax = np.nanmin(arr), np.nanmax(arr)

        else:
            raise ValueError("Provide a TIFF path or --rgbfiles.")

        # Window title
        self.update_title()

        # State
        self.contrast = 1.0
        self.gamma = 1.0

        # Colormap (single-band)
        self.cmap_name = "viridis"
        self.alt_cmap_name = "magma"  # toggle with M in single-band

        self.zoom_step = 1.2
        self.pan_step = 80

        # Scene + view
        self.scene = QGraphicsScene(self)
        self.view = RasterView(self.scene, self)
        self.setCentralWidget(self.view)

        self.pixmap_item = None
        self._last_rgb = None
        self.update_pixmap()

        # Overlays (if any)
        if self._shapefiles:
            self._add_shapefile_overlays()

        self.resize(1200, 800)

        if self.pixmap_item is not None:
            rect = self.pixmap_item.boundingRect()
            self.scene.setSceneRect(rect)
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            self.view.scale(5, 5)
            self.view.centerOn(self.pixmap_item)

    # ---------------------------- Overlays ---------------------------- #
    def _geo_to_pixel(self, x: float, y: float):
        """Map coords (raster CRS) -> image pixel coords (after downsampling)."""
        if self._transform is None:
            return None
        inv = ~self._transform  # (col, row) from (x, y)
        col, row = inv * (x, y)
        return (col / self._scale_arg, row / self._scale_arg)

    def _geom_to_qpath(self, geom) -> QPainterPath | None:
        """
        Convert shapely geom (in raster CRS) to QPainterPath in *image pixel* coords.
        Z/M tolerant: only X,Y are used. Draws Points as tiny segments.
        """
        def _coords_to_path(coords, path: QPainterPath):
            first = True
            for c in coords:
                if c is None:
                    continue
                # tolerate 2D or 3D tuples (ignore Z/M)
                x = c[0]
                y = c[1] if len(c) > 1 else None
                if y is None:
                    continue
                px = self._geo_to_pixel(x, y)
                if px is None:
                    continue
                if first:
                    path.moveTo(px[0], px[1])
                    first = False
                else:
                    path.lineTo(px[0], px[1])

        path = QPainterPath()

        if isinstance(geom, LineString):
            _coords_to_path(list(geom.coords), path)
            return path

        if isinstance(geom, MultiLineString):
            for ls in geom.geoms:
                _coords_to_path(list(ls.coords), path)
            return path

        if isinstance(geom, Polygon):
            _coords_to_path(list(geom.exterior.coords), path)
            for ring in geom.interiors:
                _coords_to_path(list(ring.coords), path)
            return path

        if isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                _coords_to_path(list(poly.exterior.coords), path)
                for ring in poly.interiors:
                    _coords_to_path(list(ring.coords), path)
            return path

        if isinstance(geom, Point):
            px = self._geo_to_pixel(geom.x, geom.y)
            if px is None:
                return None
            path.moveTo(px[0], px[1])
            path.lineTo(px[0] + 0.01, px[1] + 0.01)  # tiny mark; cosmetic pen keeps visible
            return path

        if isinstance(geom, MultiPoint):
            for p in geom.geoms:
                sub = self._geom_to_qpath(p)
                if sub:
                    path.addPath(sub)
            return path

        if isinstance(geom, GeometryCollection):
            for g in geom.geoms:
                sub = self._geom_to_qpath(g)
                if sub:
                    path.addPath(sub)
            return path

        return None

    def _add_shapefile_overlays(self):
        if not HAVE_GEO:
            print("[WARN] geopandas/shapely not available; --shapefile ignored.")
            return
        if self._crs is None or self._transform is None:
            print("[WARN] raster lacks CRS/transform; cannot place overlays.")
            return

        pen = QPen(QColor(self._shp_color))
        pen.setWidthF(self._shp_width)
        pen.setCosmetic(True)  # constant on-screen width

        for shp_path in self._shapefiles:
            try:
                gdf = gpd.read_file(shp_path)
                if gdf.empty:
                    continue

                if gdf.crs is None:
                    print(f"[WARN] {os.path.basename(shp_path)} has no CRS; assuming raster CRS.")
                    gdf = gdf.set_crs(self._crs)
                else:
                    gdf = gdf.to_crs(self._crs)

                for geom in gdf.geometry:
                    if geom is None or geom.is_empty:
                        continue
                    qpath = self._geom_to_qpath(geom)
                    if qpath is None or qpath.isEmpty():
                        continue
                    item = QGraphicsPathItem(qpath)
                    item.setPen(pen)
                    item.setZValue(10.0)
                    self.scene.addItem(item)
                    self._overlay_items.append(item)

            except Exception as e:
                print(f"[WARN] Failed to draw overlay {os.path.basename(shp_path)}: {e}")

    # ----------------------- Title / Rendering ----------------------- #
    def update_title(self):
        if self.rgbfiles:
            names = [os.path.basename(n) for n in self.rgbfiles]
            self.setWindowTitle(f"RGB ({', '.join(names)})")
        elif self.rgb_mode and self.rgb:
            self.setWindowTitle(f"RGB {self.rgb} — {os.path.basename(self.tif_path)}")
        elif hasattr(self, "band_index"):
            self.setWindowTitle(
                f"Band {self.band_index + 1}/{self.band_count} — {os.path.basename(self.tif_path)}"
            )
        else:
            self.setWindowTitle(f"Band {self.band}/{self.band_count} — {os.path.basename(self.tif_path)}")

    def _render_rgb(self):
        if self.rgb_mode:
            arr = self.data
            finite = np.isfinite(arr)
            rgb = np.zeros_like(arr)
            if np.any(finite):
                # Global 2–98 percentile stretch across all bands (QGIS-like)
                global_min, global_max = np.nanpercentile(arr, (2, 98))
                rng = max(global_max - global_min, 1e-12)
                norm = np.clip((arr - global_min) / rng, 0, 1)
                rgb = np.clip(norm * self.contrast, 0, 1)
                rgb = np.power(rgb, self.gamma)
            return (rgb * 255).astype(np.uint8)
        else:
            a = self.data
            finite = np.isfinite(a)
            norm = np.zeros_like(a, dtype=np.float32)
            rng = max(self.vmax - self.vmin, 1e-12)
            if np.any(finite):
                norm[finite] = (a[finite] - self.vmin) / rng
            norm = np.clip(norm * self.contrast, 0.0, 1.0)
            norm = np.power(norm, self.gamma)
            # viridis <-> magma toggle
            cmap = getattr(cm, self.cmap_name, cm.viridis)
            rgb = (cmap(norm)[..., :3] * 255).astype(np.uint8)
            return rgb

    def update_pixmap(self):
        # --- Select display data ---
        if hasattr(self, "band_index"):
            # HDF or scientific multi-band
            if self.data.ndim == 3:
                a = self.data[:, :, self.band_index]
            else:
                a = self.data
            rgb = None
        else:
            # Regular GeoTIFF (could be RGB or single-band)
            if self.rgb_mode:  # user explicitly passed --rgb or --rgbtiles
                rgb = self.data
                a = None
            else:
                a = self.data
                rgb = None
        # ----------------------------

        # --- Render image ---
        if rgb is None:
            # Grayscale rendering for single-band (scientific) data
            finite = np.isfinite(a)
            rng = max(np.nanmax(a) - np.nanmin(a), 1e-12)
            norm = np.zeros_like(a, dtype=np.float32)
            if np.any(finite):
                norm[finite] = (a[finite] - np.nanmin(a)) / rng
            norm = np.clip(norm, 0, 1)
            norm = np.power(norm * self.contrast, self.gamma)
            cmap = getattr(cm, self.cmap_name, cm.viridis)
            rgb = (cmap(norm)[..., :3] * 255).astype(np.uint8)
        else:
            # True RGB mode (unchanged)
            rgb = self._render_rgb()
        # ----------------------

        h, w, _ = rgb.shape
        self._last_rgb = rgb
        qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        if self.pixmap_item is None:
            self.pixmap_item = QGraphicsPixmapItem(pix)
            self.pixmap_item.setZValue(0.0)
            self.scene.addItem(self.pixmap_item)
        else:
            self.pixmap_item.setPixmap(pix)

    # ----------------------- Single-band switching ------------------- #
    def load_band(self, band_num: int):
        if self.rgb_mode:
            return

        tif_path = self.tif_path
      
        if os.path.dirname(self.tif_path).endswith(".gdb"):
            tif_path = f"OpenFileGDB:{os.path.dirname(self.tif_path)}:{os.path.basename(self.tif_path)}"

        with rasterio.open(tif_path) as src:
            self.band = band_num
            arr = src.read(self.band).astype(np.float32)
            nd = src.nodata
            if nd is not None:
                arr[arr == nd] = np.nan
            self.data = arr
            self.vmin, self.vmax = np.nanmin(arr), np.nanmax(arr)
        self.update_pixmap()
        self.update_title()

    # ------------------------------ Keys ----------------------------- #
    def keyPressEvent(self, ev):
        k = ev.key()
        hsb: QScrollBar = self.view.horizontalScrollBar()
        vsb: QScrollBar = self.view.verticalScrollBar()

        if k in (Qt.Key.Key_Plus, Qt.Key.Key_Equal, Qt.Key.Key_Z):
            self.view.scale(self.zoom_step, self.zoom_step)
        elif k in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore, Qt.Key.Key_X):
            inv = 1.0 / self.zoom_step
            self.view.scale(inv, inv)
        elif k in (Qt.Key.Key_Left, Qt.Key.Key_A):
            hsb.setValue(hsb.value() - self.pan_step)
        elif k in (Qt.Key.Key_Right, Qt.Key.Key_D):
            hsb.setValue(hsb.value() + self.pan_step)
        elif k in (Qt.Key.Key_Up, Qt.Key.Key_W):
            vsb.setValue(vsb.value() - self.pan_step)
        elif k in (Qt.Key.Key_Down, Qt.Key.Key_S):
            vsb.setValue(vsb.value() + self.pan_step)

        # Contrast / Gamma now work in both modes
        elif k == Qt.Key.Key_C:
            self.contrast *= 1.1; self.update_pixmap()
        elif k == Qt.Key.Key_V:
            self.contrast /= 1.1; self.update_pixmap()
        elif k == Qt.Key.Key_G:
            self.gamma *= 1.1; self.update_pixmap()
        elif k == Qt.Key.Key_H:
            self.gamma /= 1.1; self.update_pixmap()

        # Colormap toggle (single-band only)
        elif not self.rgb_mode and k == Qt.Key.Key_M:
            self.cmap_name, self.alt_cmap_name = self.alt_cmap_name, self.cmap_name
            self.update_pixmap()

        # Band switch
        elif k == Qt.Key.Key_BracketRight:
            if hasattr(self, "band_index"):  # HDF/NetCDF mode
                self.band_index = (self.band_index + 1) % self.band_count
                self.update_pixmap()
                self.update_title()
            elif not self.rgb_mode:  # GeoTIFF single-band mode
                new_band = self.band + 1 if self.band < self.band_count else 1
                self.load_band(new_band)

        elif k == Qt.Key.Key_BracketLeft:
            if hasattr(self, "band_index"):  # HDF/NetCDF mode
                self.band_index = (self.band_index - 1) % self.band_count
                self.update_pixmap()
                self.update_title()
            elif not self.rgb_mode:  # GeoTIFF single-band mode
                new_band = self.band - 1 if self.band > 1 else self.band_count
                self.load_band(new_band)

        elif k == Qt.Key.Key_R:
            self.contrast = 1.0
            self.gamma = 1.0
            self.update_pixmap()
            self.view.resetTransform()
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            super().keyPressEvent(ev)


# --------------------------------- Legacy argparse CLI (not used by default) ----------------------------------- #
def legacy_argparse_main():
    parser = argparse.ArgumentParser(description="TIFF viewer with RGB (2–98%) & shapefile overlays")
    parser.add_argument("tif_path", nargs="?", help="Path to TIFF (optional if --rgbfiles is used)")
    parser.add_argument("--scale", type=int, default=1, help="Downsample factor (1=full, 10=10x smaller)")
    parser.add_argument("--band", type=int, default=1, help="Band number (ignored if --rgb/--rgbfiles used)")
    parser.add_argument("--rgb", nargs=3, type=int, help="Three band numbers for RGB, e.g. --rgb 4 3 2")
    parser.add_argument("--rgbfiles", nargs=3, help="Three single-band TIFFs for RGB, e.g. --rgbfiles B4.tif B3.tif B2.tif")
    parser.add_argument("--shapefile", nargs="+", help="One or more shapefiles to overlay")
    parser.add_argument("--shp-color", default="cyan", help="Overlay color (name or #RRGGBB). Default: cyan")
    parser.add_argument("--shp-width", type=float, default=1.5, help="Overlay line width (screen pixels). Default: 1.5")
    args = parser.parse_args()

    from PySide6.QtCore import Qt
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    win = TiffViewer(
        args.tif_path,
        scale=args.scale,
        band=args.band,
        rgb=args.rgb,
        rgbfiles=args.rgbfiles,
        shapefiles=args.shapefile,
        shp_color=args.shp_color,
        shp_width=args.shp_width,
    )
    win.show()
    sys.exit(app.exec())


def run_viewer(
    tif_path,
    scale=None,
    band=None,
    rgb=None,
    rgbfiles=None,
    shapefile=None,
    shp_color=None,
    shp_width=None,
    subset=None
):

    """Launch the TiffViewer app"""
    from PySide6.QtCore import Qt
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    win = TiffViewer(
        tif_path,
        scale=scale,
        band=band,
        rgb=rgb,
        rgbfiles=rgbfiles,
        shapefiles=shapefile,
        shp_color=shp_color,
        shp_width=shp_width,
        subset=subset
    )
    win.show()
    sys.exit(app.exec())

import click

@click.command()
@click.version_option("0.1.10", prog_name="viewtif")
@click.argument("tif_path", required=False)
@click.option("--band", default=1, show_default=True, type=int, help="Band number to display")
@click.option("--scale", default=1.0, show_default=True, type=int, help="Scale factor for display")
@click.option("--rgb", nargs=3, type=int, help="Three band numbers for RGB, e.g. --rgb 4 3 2")
@click.option("--rgbfiles", nargs=3, type=str, help="Three single-band TIFFs for RGB, e.g. --rgbfiles B4.tif B3.tif B2.tif")
@click.option("--shapefile", multiple=True, type=str, help="One or more shapefiles to overlay")
@click.option("--shp-color", default="white", show_default=True, help="Overlay color (name or #RRGGBB).")
@click.option("--shp-width", default=1.0, show_default=True, type=float, help="Overlay line width (screen pixels).")
@click.option("--subset", default=None, type=int, help="Open specific subdataset index in .hdf/.h5 file")

def main(tif_path, band, scale, rgb, rgbfiles, shapefile, shp_color, shp_width, subset):
    """Lightweight GeoTIFF viewer."""
    # --- Warn early if shapefile requested but geopandas missing ---
    if shapefile and not HAVE_GEO:
        print(
            "[WARN] --shapefile requires geopandas and shapely.\n"
            "       Install them with: pip install viewtif[geo]\n"
            "       Proceeding without shapefile overlay."
        )

    run_viewer(
        tif_path,
        scale=scale,
        band=band,
        rgb=rgb,
        rgbfiles=rgbfiles,
        shapefile=shapefile,
        shp_color=shp_color,
        shp_width=shp_width,
        subset=subset
    )

if __name__ == "__main__":
    main()

