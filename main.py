import time
import cv2
import mss
import numpy as np
import pyautogui

# Progress bar region (left, top, width, height). Tune for your resolution.
BAR_REGION = (2380, 820, 525, 80)

# HSV range for the light blue progress-bar glow.
LOWER_HSV = np.array([90, 70, 150])
UPPER_HSV = np.array([110, 255, 255])

CHECK_INTERVAL_SEC = 0.1
SHOW_PREVIEW = False
PRESS_COOLDOWN_SEC = 0.3
MIN_PIXEL_COUNT = 10
PREVIEW_MONITOR_INDEX = 1
TRIGGER_DELAY_SEC = 0.3


def _bar_is_visible(sct, bar_region):
    frame = np.array(
        sct.grab(
            {
                "left": bar_region[0],
                "top": bar_region[1],
                "width": bar_region[2],
                "height": bar_region[3],
            }
        )
    )[:, :, :3]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)
    return cv2.countNonZero(mask) >= MIN_PIXEL_COUNT


def _show_region_box(sct, regions):
    monitor = sct.monitors[PREVIEW_MONITOR_INDEX]
    frame = np.array(sct.grab(monitor))[:, :, :3].copy()
    offset_left = monitor["left"]
    offset_top = monitor["top"]
    for left, top, width, height in regions:
        cv2.rectangle(
            frame,
            (left - offset_left, top - offset_top),
            (left - offset_left + width, top - offset_top + height),
            (0, 0, 255),
            2,
        )
    scale = 0.25
    resized = cv2.resize(
        frame,
        (int(frame.shape[1] * scale), int(frame.shape[0] * scale)),
        interpolation=cv2.INTER_AREA,
    )
    cv2.imshow("Capture Region", resized)
    cv2.waitKey(1)


def main():
    print("Script started")
    last_press = 0.0
    pending_press_at = None
    was_visible = False
    with mss.mss() as sct:
        while True:
            if SHOW_PREVIEW:
                _show_region_box(sct, [BAR_REGION])

            now = time.time()
            visible = _bar_is_visible(sct, BAR_REGION)
            if visible and not was_visible and pending_press_at is None:
                pending_press_at = now + TRIGGER_DELAY_SEC
            if pending_press_at is not None and now >= pending_press_at:
                if now - last_press >= PRESS_COOLDOWN_SEC:
                    pyautogui.press("d")
                    last_press = now
                pending_press_at = None
            was_visible = visible
            time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    main()
