from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Sequence, Tuple
import multiprocessing

import chanfig
import cv2 as cv
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

from tqdm import tqdm


@dataclass
class BoundingBox:
    top: int
    bottom: int
    left: int
    right: int

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)


@dataclass
class ColorCues:
    band: np.ndarray
    glare_mask: np.ndarray
    specular_map: np.ndarray


class Config(chanfig.Config):
    input: str = "images"
    output: str = "outputs"
    table: str = "zx.csv"
    percentile: float = 92.0
    bbox_color: Tuple[int, int, int] = (0, 255, 0)
    bbox_thickness: int = 5
    workers: int | None = None

    def post(self) -> None:
        if not (0.0 < self.percentile <= 100.0):
            raise ValueError("percentile must be within (0, 100]")
        if self.workers is not None and self.workers < 0:
            raise ValueError("workers must be None, 0, or positive integer")


class Axis(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


def _ensure_odd(value: int) -> int:
    return value if value % 2 == 1 else value + 1


def _smooth_sequence(sequence: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return sequence
    window = _ensure_odd(int(window))
    kernel = np.ones(window, dtype=np.float64) / window
    return np.convolve(sequence, kernel, mode="same")


def _clahe_parameters(gray: np.ndarray) -> Tuple[float, Tuple[int, int]]:
    h, w = gray.shape
    grid = max(2, int(round(np.sqrt(h * w) / 150)))
    clip = float(np.clip(np.var(gray) / 1024 + 1.5, 1.0, 8.0))
    return clip, (grid, grid)


def _preprocess(gray: np.ndarray) -> np.ndarray:
    clip_limit, tile_grid = _clahe_parameters(gray)
    clahe = cv.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid)
    enhanced = clahe.apply(gray)
    kernel = _ensure_odd(max(3, int(round(min(gray.shape) / 150))))
    return cv.GaussianBlur(enhanced, (kernel, kernel), 0)


def _band_image(gray: np.ndarray) -> np.ndarray:
    blur_size = _ensure_odd(max(21, int(round(gray.shape[1] / 20))))
    baseline = cv.GaussianBlur(gray, (blur_size, blur_size), 0)
    band = cv.subtract(gray, baseline)
    return cv.normalize(band, None, 0, 255, cv.NORM_MINMAX).astype(np.float32)


def _percentile_profile(
    primary: np.ndarray,
    axis: Axis,
    percentile: float,
    extras: Optional[Sequence[Tuple[np.ndarray, float]]] = None,
    weight_power: Optional[float] = 1.0,
) -> np.ndarray:
    def compute(sample: np.ndarray) -> np.ndarray:
        if sample.size == 0:
            length = sample.shape[0] if axis is Axis.VERTICAL else sample.shape[1]
            return np.zeros(length, dtype=np.float64)

        collapse_axis = 1 if axis is Axis.VERTICAL else 0
        weighted = sample
        if weight_power is not None:
            if axis is Axis.VERTICAL:
                weights = _column_weights(sample.shape[1]) ** float(weight_power)
                weighted = weighted * weights
            else:
                weights = (_row_weights(sample.shape[0]) ** float(weight_power))[:, None]
                weighted = weighted * weights
        return np.percentile(weighted, percentile, axis=collapse_axis).astype(np.float64)

    profile = compute(primary)
    if extras:
        for extra, blend in extras:
            if extra is None or extra.size == 0 or blend == 0.0:
                continue
            profile += float(blend) * compute(extra)
    return profile


def _extract_color_cues(image: np.ndarray) -> ColorCues:
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    processed_sat = _preprocess(saturation)
    band_sat = _band_image(processed_sat)

    red = image[:, :, 2]
    blue = image[:, :, 0]
    rb_diff = cv.absdiff(red, blue)
    processed_diff = _preprocess(rb_diff)
    band_diff = _band_image(processed_diff)
    color_band = np.maximum(band_sat, band_diff).astype(np.float32)

    value = hsv[:, :, 2].astype(np.float32)
    saturation_f = saturation.astype(np.float32)
    glare_sigma = max(1.0, min(image.shape[0], image.shape[1]) / 400.0)
    value_blur = cv.GaussianBlur(value, (0, 0), glare_sigma)
    saturation_blur = cv.GaussianBlur(saturation_f, (0, 0), glare_sigma)

    value_threshold = float(np.percentile(value_blur, 95))
    saturation_threshold = float(np.percentile(saturation_blur, 30))
    glare_mask = np.logical_and(value_blur >= value_threshold, saturation_blur <= saturation_threshold).astype(
        np.float32
    )
    glare_mask = cv.GaussianBlur(glare_mask, (0, 0), glare_sigma)
    glare_mask /= glare_mask.max() + 1e-9

    specular_map = cv.max(value_blur - saturation_blur, 0.0)
    specular_map = cv.GaussianBlur(specular_map, (0, 0), glare_sigma)
    specular_map /= specular_map.max() + 1e-9

    return ColorCues(
        band=color_band,
        glare_mask=glare_mask.astype(np.float32),
        specular_map=specular_map.astype(np.float32),
    )


def _column_weights(width: int) -> np.ndarray:
    positions = (np.arange(width) - (width - 1) / 2) / max(width / 6.0, 1.0)
    weights = np.exp(-(positions**2) / 2.0)
    return weights / weights.max()


def _row_weights(height: int) -> np.ndarray:
    positions = (np.arange(height) - (height - 1) / 2) / max(height / 6.0, 1.0)
    weights = np.exp(-(positions**2) / 2.0)
    return weights / weights.max()


def _sobel_profiles(image: np.ndarray, axis: int) -> Tuple[np.ndarray, np.ndarray]:
    if axis == 0:
        grad = cv.Sobel(image, cv.CV_32F, 0, 1, ksize=3)
        col_weights = _column_weights(image.shape[1])
        row_weights = _row_weights(image.shape[0])
        positive = (np.maximum(grad, 0.0) * col_weights).sum(axis=1) * row_weights
        negative = (np.maximum(-grad, 0.0) * col_weights).sum(axis=1) * row_weights
    elif axis == 1:
        grad = cv.Sobel(image, cv.CV_32F, 1, 0, ksize=3)
        row_weights = _row_weights(image.shape[0])
        weighted = np.maximum(grad, 0.0) * row_weights[:, None]
        col_weights = _column_weights(image.shape[1]) ** 0.5
        positive = weighted.sum(axis=0) * col_weights
        weighted_neg = np.maximum(-grad, 0.0) * row_weights[:, None]
        negative = weighted_neg.sum(axis=0) * col_weights
    else:
        raise ValueError("axis must be 0 (vertical) or 1 (horizontal)")
    return positive.astype(np.float64), negative.astype(np.float64)


def _column_energy(
    primary_slice: np.ndarray,
    extra_slice: Optional[np.ndarray],
    glare_mask: Optional[np.ndarray],
    specular_map: Optional[np.ndarray],
    smooth_sigma: float,
    blend: float = 0.35,
    glare_weight: float = 0.3,
    specular_weight: float = 0.2,
) -> np.ndarray:
    extras: Optional[Sequence[Tuple[np.ndarray, float]]] = None
    if extra_slice is not None and extra_slice.size:
        extras = [(extra_slice, blend)]
    energy = _percentile_profile(primary_slice, Axis.HORIZONTAL, 97.0, extras=extras, weight_power=None)
    energy = cv.GaussianBlur(energy.reshape(1, -1), (0, 0), smooth_sigma).reshape(-1)
    energy -= energy.min()
    if not np.any(energy):
        energy = np.ones_like(energy)
    else:
        energy /= energy.max() + 1e-9

    if glare_mask is not None and glare_mask.size:
        glare_profile = glare_mask.mean(axis=0).astype(np.float64)
        glare_profile = cv.GaussianBlur(glare_profile.reshape(1, -1), (0, 0), smooth_sigma).reshape(-1)
        glare_profile = np.clip(glare_profile, 0.0, 1.0)
        energy *= np.clip(1.0 - glare_weight * glare_profile, 0.1, 1.0)

    if specular_map is not None and specular_map.size:
        spec_profile = specular_map.mean(axis=0).astype(np.float64)
        spec_profile = cv.GaussianBlur(spec_profile.reshape(1, -1), (0, 0), smooth_sigma).reshape(-1)
        if np.any(spec_profile):
            spec_profile /= spec_profile.max() + 1e-9
            energy *= np.clip(1.0 - specular_weight * spec_profile, 0.2, 1.0)

    return energy


def _refine_bounds(profile: np.ndarray, start: int, end: int, margin: int) -> Tuple[int, int]:
    start = max(0, min(start, profile.size - 2))
    end = max(start + 1, min(end, profile.size))
    gradient = np.gradient(profile)
    top_window = gradient[max(0, start - margin) : min(profile.size, start + margin)]
    bottom_window = gradient[max(0, end - margin) : min(profile.size, end + margin)]
    top_idx = max(0, start - margin) + int(np.argmax(top_window)) if top_window.size else start
    bottom_idx = max(0, end - margin) + int(np.argmin(bottom_window)) if bottom_window.size else end
    bottom_idx = max(top_idx + 1, bottom_idx)
    return top_idx, min(profile.size, bottom_idx)


def _energy_window(values: np.ndarray, lower: float, upper: float) -> Tuple[int, int]:
    length = values.size
    if length == 0:
        return 0, 0

    weights = np.clip(values.astype(np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= 0.0:
        return 0, length

    cumulative = np.cumsum(weights) / total
    start = int(np.searchsorted(cumulative, float(np.clip(lower, 0.0, 1.0)), side="left"))
    end = int(np.searchsorted(cumulative, float(np.clip(upper, 0.0, 1.0)), side="right"))
    start = max(0, min(start, length - 1))
    end = max(start + 1, min(end, length))

    if end <= start:
        peak = int(np.argmax(weights))
        start = max(0, peak - 1)
        end = min(length, peak + 2)

    return start, end


def _moment_window(values: np.ndarray, minimum: int) -> Tuple[int, int]:
    length = values.size
    if length == 0:
        return 0, 0

    weights = np.clip(values.astype(np.float64), 0.0, None)
    total = float(weights.sum())
    if total <= 0.0:
        return 0, length

    positions = (np.arange(length, dtype=np.float64) + 0.5) / float(length)
    mean = float(np.dot(weights, positions) / total)
    variance = float(np.dot(weights, (positions - mean) ** 2) / total)
    sigma = max(np.sqrt(max(variance, 0.0)), 1.0 / length)

    lower = max(0.0, mean - sigma)
    upper = min(1.0, mean + sigma)

    start = int(np.floor(lower * length))
    end = int(np.ceil(upper * length))
    if end - start < minimum:
        padding = (minimum - (end - start)) / (2.0 * length)
        lower = max(0.0, lower - padding)
        upper = min(1.0, upper + padding)
        start = int(np.floor(lower * length))
        end = int(np.ceil(upper * length))

    start = max(0, min(start, length - 1))
    end = max(start + 1, min(end, length))
    return start, end


def _local_maxima(values: np.ndarray) -> np.ndarray:
    if values.size < 3:
        return np.array([], dtype=np.int32)
    gradient = np.diff(values)
    signs = np.sign(gradient)
    turning = (np.hstack([signs, 0.0]) < 0.0) & (np.hstack([0.0, signs]) > 0.0)
    return np.where(turning)[0].astype(np.int32)


def _localize_vertical_bounds(
    enhanced_gray: np.ndarray,
    band: np.ndarray,
    color_cues: ColorCues,
    percentile: float,
) -> Tuple[int, int]:
    height = enhanced_gray.shape[0]
    if height == 0:
        return 0, 0

    blur_sigma = max(1.0, min(enhanced_gray.shape) / 1500.0)
    blurred = cv.GaussianBlur(enhanced_gray, (0, 0), blur_sigma)
    upward_edges, downward_edges = _sobel_profiles(blurred, axis=0)

    smoothing = max(5, height // 200)
    upward_smooth = _smooth_sequence(upward_edges, smoothing)
    downward_smooth = _smooth_sequence(downward_edges, smoothing)

    bottom_peak = int(np.argmax(downward_smooth))
    peaks = _local_maxima(upward_smooth)
    max_gap = max(height // 4, 400)
    candidates = [idx for idx in peaks if 0 < bottom_peak - idx <= max_gap]
    if not candidates and bottom_peak > 0:
        candidates = [int(np.argmax(upward_smooth[:bottom_peak]))]
    top_estimate = (
        max(candidates, key=lambda idx: upward_smooth[idx]) if candidates else max(0, bottom_peak - height // 10)
    )
    top_estimate = int(top_estimate)
    bottom_estimate = max(top_estimate + 1, bottom_peak)

    percentile_energy = min(99.0, 95.0 + height / 8000.0)
    base_margin = max(smoothing * 3, height // 100, 40)
    min_height = max(40, height // 100)
    margin = max(base_margin, (bottom_estimate - top_estimate) // 2 + min_height)
    lower = max(0, min(top_estimate, bottom_estimate) - margin)
    upper = min(height, max(top_estimate, bottom_estimate) + margin)
    if upper - lower <= min_height:
        extra = min_height - (upper - lower)
        lower = max(0, lower - extra // 2)
        upper = min(height, upper + extra - extra // 2)

    band_segment = band[lower:upper]
    energy = _percentile_profile(band_segment, Axis.VERTICAL, percentile_energy)
    smooth_window = max(3, band_segment.shape[0] // 120)
    energy = _smooth_sequence(energy, smooth_window)
    energy = np.clip(energy, 0.0, None)

    if color_cues.glare_mask.size:
        glare_profile = color_cues.glare_mask[lower:upper].mean(axis=1)
        glare_profile = _smooth_sequence(glare_profile, smooth_window)
        energy *= np.clip(1.0 - 0.45 * glare_profile, 0.1, 1.0)
    if color_cues.specular_map.size:
        spec_profile = color_cues.specular_map[lower:upper].mean(axis=1)
        spec_profile = _smooth_sequence(spec_profile, smooth_window)
        if np.any(spec_profile):
            spec_profile /= spec_profile.max() + 1e-9
            energy *= np.clip(1.0 - 0.25 * spec_profile, 0.2, 1.0)

    segment_length = max(upper - lower, 1)
    desired_span = max(min_height, bottom_estimate - top_estimate)
    span_fraction = np.clip(desired_span / segment_length, 0.2, 0.85)
    center_fraction = np.clip(((top_estimate + bottom_estimate) / 2 - lower) / segment_length, 0.0, 1.0)
    lower_frac = max(0.0, center_fraction - span_fraction / 2.0)
    upper_frac = min(1.0, center_fraction + span_fraction / 2.0)
    span_frac = max(upper_frac - lower_frac, 1e-3)
    if span_frac < span_fraction:
        deficit = span_fraction - span_frac
        lower_frac = max(0.0, lower_frac - deficit / 2.0)
        upper_frac = min(1.0, upper_frac + deficit / 2.0)

    rel_top, rel_bottom = _energy_window(energy, lower_frac, upper_frac)
    candidate_top = lower + rel_top
    candidate_bottom = lower + rel_bottom
    if candidate_bottom <= candidate_top:
        candidate_bottom = min(height, candidate_top + max(2, int(np.ceil(segment_length * span_fraction))))
    span = candidate_bottom - candidate_top
    if span < min_height:
        pad = (min_height - span) // 2
        candidate_top = max(0, candidate_top - pad)
        candidate_bottom = min(height, candidate_bottom + (min_height - span - pad))

    row_profile = _percentile_profile(band, Axis.VERTICAL, percentile)
    refinement_margin = max(10, min((candidate_bottom - candidate_top) // 2, 60))
    top_final, bottom_final = _refine_bounds(row_profile, candidate_top, candidate_bottom, refinement_margin)
    top_final = max(0, min(top_final, height - 2))
    bottom_final = max(top_final + 1, min(bottom_final, height))
    return top_final, bottom_final


def _localize_horizontal_bounds(
    enhanced_gray: np.ndarray,
    band: np.ndarray,
    color_cues: ColorCues,
    top: int,
    bottom: int,
) -> Tuple[int, int]:
    height, width = enhanced_gray.shape
    top = max(0, min(top, height - 1))
    bottom = max(top + 1, min(bottom, height))
    strip_proc = enhanced_gray[top:bottom]
    if strip_proc.size == 0:
        return 0, width

    profile = strip_proc.mean(axis=0).astype(np.float64)
    sigma = max(1.0, width / 1800.0)
    smoothed = cv.GaussianBlur(profile.reshape(1, -1), (0, 0), sigma).reshape(-1)
    gradient = np.gradient(smoothed)
    center = (width - 1) / 2.0
    sigma_weight = max(width / 4.0, 1.0)
    weights = np.exp(-((np.arange(width) - center) ** 2) / (2.0 * sigma_weight**2))

    band_slice = band[top:bottom]
    smooth_cols = max(1.0, width / 2000.0)
    extra_slice = color_cues.band[top:bottom]
    glare_slice = color_cues.glare_mask[top:bottom]
    spec_slice = color_cues.specular_map[top:bottom]
    col_norm = _column_energy(band_slice, extra_slice, glare_slice, spec_slice, smooth_cols)
    col_boost = 0.5 + 0.5 * np.clip(col_norm, 0.0, 1.0)
    center_idx = int(round(center))
    weighted = gradient * weights
    sobel_pos, sobel_neg = _sobel_profiles(strip_proc, axis=1)
    negative = (np.clip(-weighted, 0.0, None) + sobel_neg) * col_boost
    positive = (np.clip(weighted, 0.0, None) + sobel_pos) * col_boost

    if center_idx <= 0:
        left_region = negative
        grad_left = int(np.argmax(left_region)) if left_region.size else 0
        combo_left = grad_left
    else:
        left_region = negative[:center_idx]
        if np.all(left_region == 0.0):
            grad_left = int(np.argmin(weighted[:center_idx]))
            combo_left = grad_left
        else:
            grad_left = int(np.argmax(left_region))
            left_norm = left_region / (left_region.max() + 1e-9)
            combo_scores = left_norm * (0.3 + 0.7 * col_norm[:center_idx])
            combo_left = int(np.argmax(combo_scores))
    if center_idx >= width - 1:
        right_region = positive
        grad_right = int(np.argmax(right_region)) if right_region.size else width - 1
        combo_right = grad_right
    else:
        right_region = positive[center_idx:]
        if np.all(right_region == 0.0):
            grad_right = center_idx + int(np.argmax(weighted[center_idx:]))
            combo_right = grad_right
        else:
            grad_right = center_idx + int(np.argmax(right_region))
            right_norm = right_region / (right_region.max() + 1e-9)
            combo_scores = right_norm * (0.3 + 0.7 * col_norm[center_idx:])
            combo_right = center_idx + int(np.argmax(combo_scores))

    threshold = 0.15
    if left_region.size:
        left_strength = col_norm[min(grad_left, col_norm.size - 1)]
        left = grad_left if left_strength >= threshold else combo_left
    else:
        left = 0
    if right_region.size:
        right_strength = col_norm[min(grad_right, col_norm.size - 1)]
        right = grad_right if right_strength >= threshold else combo_right
    else:
        right = width - 1

    if right <= left:
        right = min(width - 1, left + max(width // 40, 10))
    left = max(0, min(left, width - 2))
    right = max(left + 1, min(right, width - 1))

    # Adaptive refinement using specular and intensity cues guards against
    # under-estimated widths when plate reflections dominate or plates nearly touch.
    spec_profile = color_cues.specular_map[top:bottom].mean(axis=0).astype(np.float64)
    intensity_profile = smoothed
    center_idx = width // 2
    center_window = intensity_profile[max(0, center_idx - 200) : min(width, center_idx + 200)]
    center_mean = float(center_window.mean()) if center_window.size else float(intensity_profile.mean())

    bbox_width = right - left
    ratio = bbox_width / float(width)

    spec_cut = 0.12
    spec_high = 0.4
    min_first_low = max(50, min(width // 8, 400))
    spec_window = max(50, min(width // 4, 600))

    candidates = np.where(spec_profile[:center_idx] <= spec_cut)[0]
    if ratio < 0.45 and candidates.size:
        first_low = int(candidates[0])
        if first_low > min_first_low and spec_profile[:first_low].max() >= spec_high:
            start = max(0, first_low - spec_window)
            if first_low > start:
                spec_left = start + int(np.argmax(negative[start:first_low]))
                left = max(0, min(spec_left, left))

    margin_left = 30.0
    min_delta_increase = max(50, int(round(width * 0.03)))
    threshold_left = center_mean + margin_left
    idx_left = 0
    while idx_left < center_idx and intensity_profile[idx_left] > threshold_left:
        idx_left += 1
    if idx_left > left + min_delta_increase:
        left = max(left, min(idx_left, width - 2))

    margin_right = 20.0
    min_delta_decrease = max(50, int(round(width * 0.02)))
    threshold_right = center_mean + margin_right
    idx_right = width - 1
    while idx_right >= center_idx and intensity_profile[idx_right] > threshold_right:
        idx_right -= 1
    if idx_right >= 0 and right - idx_right > min_delta_decrease:
        right = max(left + 1, min(idx_right, width - 1))

    local_margin = max(40, width // 200)
    left_window_start = left
    left_window_end = min(center_idx, left + local_margin)
    if left_window_end - left_window_start > 1:
        local_idx = int(np.argmax(negative[left_window_start:left_window_end])) + left_window_start
        left = max(left, min(local_idx, width - 2))
    right_window_start = max(center_idx, right - local_margin)
    right_window_end = right + 1
    if right_window_end - right_window_start > 1:
        local_idx = int(np.argmax(positive[right_window_start:right_window_end])) + right_window_start
        right = max(left + 1, min(local_idx, width - 1))

    spec_low_tight = spec_cut * 0.03
    if left < width - 2:
        left_low = np.where(spec_profile[left : min(center_idx, left + local_margin * 3)] <= spec_low_tight)[0]
        if left_low.size:
            candidate = left + int(left_low[0])
            if candidate - left <= local_margin * 3:
                left = max(0, min(candidate, width - 2))

    return left, right


def detect_bbox(image: np.ndarray, percentile: float) -> BoundingBox:
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    enhanced_gray = _preprocess(gray)
    gray_band = _band_image(enhanced_gray)
    color_cues = _extract_color_cues(image)
    combined_band = np.maximum(gray_band, color_cues.band)

    top, bottom = _localize_vertical_bounds(enhanced_gray, combined_band, color_cues, percentile)
    left, right = _localize_horizontal_bounds(enhanced_gray, combined_band, color_cues, top, bottom)

    height, width = enhanced_gray.shape
    top = max(0, min(top, height - 2))
    bottom = max(top + 1, min(bottom, height))
    left = max(0, min(left, width - 2))
    right = max(left + 1, min(right, width))

    return BoundingBox(top=top, bottom=bottom, left=left, right=right)


def draw_bbox(image: np.ndarray, box: BoundingBox, bbox_color: Tuple[int, int, int], bbox_thickness: int) -> np.ndarray:
    annotated = image.copy()
    cv.rectangle(
        annotated,
        (int(box.left), int(box.top)),
        (int(box.right), int(box.bottom)),
        tuple(int(v) for v in bbox_color),
        int(bbox_thickness),
    )
    return annotated


def process_image(
    input: str, output: str, percentile: float, bbox_color: Tuple[int, int, int], bbox_thickness: int
) -> Tuple[BoundingBox, str]:
    input_path = Path(input)
    color = cv.imread(str(input_path), cv.IMREAD_COLOR)
    if color is None:
        raise FileNotFoundError(f"unable to read image: {input_path}")

    bbox = detect_bbox(color, percentile)
    annotated = draw_bbox(color, bbox, bbox_color, bbox_thickness)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(input_path)
    exif = img.getexif()
    time = exif[306]
    if not cv.imwrite(str(output_path), annotated):
        raise RuntimeError(f"failed to save {output_path}")
    return bbox, time


def _process_wrapper(args):
    f, input_path, output_path, cfg = args
    box, time = process_image(input_path, output_path, cfg)
    return box, time


def process_image_wrapper(args):
    input_path, output_path, percentile, bbox_color, bbox_thickness, f = args
    box, time = process_image(input_path, output_path, percentile, bbox_color, bbox_thickness)
    return (box, time), f


if __name__ == "__main__":
    cfg = Config().parse()
    ret = []
    files = sorted(os.listdir(cfg.input))
    if cfg.workers == 0:
        for f in tqdm(files, total=len(files), desc="Processing images"):
            box, time = process_image(
                os.path.join(cfg.input, f),
                os.path.join(cfg.output, f),
                cfg.percentile,
                cfg.bbox_color,
                cfg.bbox_thickness,
            )
            ret.append(
                {
                    "id": f,
                    "time": time,
                    "height": box.height,
                    "width": box.width,
                    "top": box.top,
                    "left": box.left,
                    "bottom": box.bottom,
                    "right": box.right,
                }
            )
    else:
        num_workers = cfg.workers if cfg.workers is not None else multiprocessing.cpu_count()
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            results = list(
                tqdm(
                    executor.map(
                        process_image_wrapper,
                        [
                            (
                                os.path.join(cfg.input, f),
                                os.path.join(cfg.output, f),
                                cfg.percentile,
                                cfg.bbox_color,
                                cfg.bbox_thickness,
                                f,
                            )
                            for f in files
                        ],
                    ),
                    total=len(files),
                    desc="Processing images",
                )
            )
            ret = []
            for (box, time), f in results:
                ret.append(
                    {
                        "id": f,
                        "time": time,
                        "height": box.height,
                        "width": box.width,
                        "top": box.top,
                        "left": box.left,
                        "bottom": box.bottom,
                        "right": box.right,
                    }
                )
    df = pd.DataFrame(ret)
    df.to_csv(cfg.table, index=False)
    print(f"saved table -> {cfg.table}")
