"""Add timed AI narration to the clean demo, preserving its original video stream.

Requires kokoro-onnx, soundfile, ffmpeg and local Kokoro v1.0 model/voice files.
Cached speech, the assembled WAV and timing metadata remain under playground/.
"""

import argparse
import hashlib
import json
import re
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "docs/website/assets"
WORK = ROOT / "playground/website/voiceover"
SAMPLE_RATE = 24000
PADDING = 0.15


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def duration(path):
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]
        )
    )


def read_cues(path):
    def seconds(timestamp):
        hours, minutes, value = timestamp.replace(",", ".").split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(value)

    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        _, timing, *lines = block.splitlines()
        start, end = (seconds(value.strip()) for value in timing.split("-->"))
        if end - start <= 2 * PADDING or (cues and start < cues[-1]["end"]):
            raise ValueError(f"Invalid or overlapping narration interval: {timing}")
        cues.append({"start": start, "end": end, "text": " ".join(lines)})
    return cues


def spoken_text(text):
    pronunciations = {"FDM": "F D M", "VLA": "V L A", "WAM": "W A M", "MSE": "M S E", "1x": "normal"}
    return re.sub(r"\b(?:FDM|VLA|WAM|MSE|1x)\b", lambda match: pronunciations[match[0]], text)


def synthesize(cues, voice, speed, model, voices, work):
    import onnxruntime as ort
    import soundfile as sf
    from kokoro_onnx import Kokoro

    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(str(model), sess_options=options, providers=["CPUExecutionProvider"])
    kokoro = Kokoro.from_session(session, str(voices))
    model_key = [(path.name, path.stat().st_size, path.stat().st_mtime_ns) for path in [model, voices]]
    for index, cue in enumerate(cues, 1):
        text = spoken_text(cue["text"])
        key = hashlib.sha256(json.dumps([model_key, voice, speed, text]).encode()).hexdigest()[:16]
        audio = work / f"{index:02d}-{key}.wav"
        if not audio.exists():
            temporary = audio.with_suffix(".tmp.wav")
            samples, sample_rate = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
            sf.write(str(temporary), samples, sample_rate, subtype="PCM_16")
            temporary.replace(audio)
        cue["speech"] = str(audio)
        cue["spoken_text"] = text
        print(f"Synthesized {index}/{len(cues)}", flush=True)


def assemble(cues, total_duration, work):
    timeline = bytearray(round(total_duration * SAMPLE_RATE) * 2)
    trim = "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-50dB"
    for index, cue in enumerate(cues, 1):
        trimmed = work / f"{index:02d}-trimmed.wav"
        run(
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            cue["speech"],
            "-af",
            f"{trim},areverse,{trim},areverse",
            "-ar",
            SAMPLE_RATE,
            "-ac",
            "1",
            trimmed,
        )
        available = cue["end"] - cue["start"] - 2 * PADDING
        speed = max(1.0, duration(trimmed) / available)
        if speed > 1.3:
            raise ValueError(f"Cue {index} needs {speed:.2f}x speed; shorten its text or use a faster voice.")
        fitted = work / f"{index:02d}-fitted.wav"
        run(
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            trimmed,
            "-af",
            f"atempo={speed:.8f},loudnorm=I=-18:TP=-2:LRA=7",
            "-ar",
            SAMPLE_RATE,
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            fitted,
        )
        with wave.open(str(fitted), "rb") as audio:
            samples = audio.readframes(audio.getnframes())
        start = round((cue["start"] + PADDING) * SAMPLE_RATE) * 2
        end = start + len(samples)
        if end > round(cue["end"] * SAMPLE_RATE) * 2 or end > len(timeline):
            raise ValueError(f"Cue {index} exceeds its narration interval after retiming.")
        timeline[start:end] = samples
        cue.update({"speech_start": start / 2 / SAMPLE_RATE, "speech_end": end / 2 / SAMPLE_RATE, "speed": speed})
        print(f"Aligned {index}/{len(cues)}: {cue['speech_start']:.2f}-{cue['speech_end']:.2f}s", flush=True)
    output = work / "narration.wav"
    with wave.open(str(output), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(timeline)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ASSETS / "demo.mp4")
    parser.add_argument("--subtitles", type=Path, default=ASSETS / "demo.en.srt")
    parser.add_argument("--output", type=Path, default=ASSETS / "demo-narrated.mp4")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--model", type=Path, default=WORK / "kokoro-v1.0.onnx")
    parser.add_argument("--voices", type=Path, default=WORK / "voices-v1.0.bin")
    parser.add_argument("--work-dir", type=Path, default=WORK)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("Use a separate output path to preserve the clean source.")
    args.work_dir.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cues = read_cues(args.subtitles)
    total_duration = duration(args.input)
    if not cues or cues[-1]["end"] > total_duration:
        parser.error("Narration must contain cues that fit within the video duration.")
    synthesize(cues, args.voice, args.speed, args.model, args.voices, args.work_dir)
    narration = assemble(cues, total_duration, args.work_dir)
    temporary = args.output.with_suffix(".tmp.mp4")
    run(
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-i",
        args.input,
        "-i",
        narration,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-metadata:s:a:0",
        "language=eng",
        "-metadata:s:a:0",
        "title=English AI narration",
        "-disposition:a:0",
        "default",
        "-movflags",
        "+faststart",
        temporary,
    )
    temporary.replace(args.output)
    (args.work_dir / "timing.json").write_text(
        json.dumps(
            {
                "voice": args.voice,
                "speed": args.speed,
                "model": args.model.name,
                "duration": total_duration,
                "cues": cues,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Exported {args.output} ({total_duration:.2f}s), with narration and no subtitle track.")


if __name__ == "__main__":
    main()
