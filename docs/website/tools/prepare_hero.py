"""Join all five FDM w/ VLM third-camera recordings into a silent, looping cover."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "docs/website/assets/hero"
TASKS = ("drawer", "gift", "badminton", "cup", "cube")
FPS = 24


def prepare_clip(task, directory):
    source = ROOT / "web/real-exp" / task / "FDM-VLM/third.mp4"
    video = directory / f"{task}.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-threads",
            "1",
            "-i",
            str(source),
            "-an",
            "-vf",
            f"fps={FPS},setsar=1",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "26",
            "-pix_fmt",
            "yuv420p",
            "-threads",
            "2",
            str(video),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-threads",
            "1",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-quality",
            "85",
            str(ASSETS / f"{task}.webp"),
        ],
        check=True,
    )
    frames = int(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=nb_frames",
                "-of",
                "csv=p=0",
                str(video),
            ],
            text=True,
        )
    )
    print(f"Prepared {task}: {frames / FPS:.2f} s", flush=True)
    return video, frames


def prepare_hero():
    ASSETS.mkdir(parents=True, exist_ok=True)
    intermediates = ROOT / "playground/website/render"
    intermediates.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hero-", dir=intermediates) as temporary:
        directory = Path(temporary)
        clips, chapters, frames = [], [], 0
        for task in TASKS:
            video, count = prepare_clip(task, directory)
            clips.append(f"file '{video.as_posix()}'")
            chapters.append({"task": task, "start": round(frames / FPS, 6)})
            frames += count
        manifest = directory / "concat.txt"
        manifest.write_text("\n".join(clips) + "\n")
        output = ASSETS / "rollouts.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(manifest),
                "-c",
                "copy",
                "-an",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
        )
        (ASSETS / "chapters.json").write_text(json.dumps(chapters, indent=2) + "\n")
        print(f"Joined all five tasks: {frames / FPS:.2f} s, {output.stat().st_size / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    prepare_hero()
