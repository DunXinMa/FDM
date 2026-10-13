# FDM project website

Static English project page for **Forward Dynamics Model**, with locally hosted fonts, figures and narrated H.264 video. No Node build or runtime dependencies are required.

The website lives in `docs/website/`, separate from the development guides in `docs/`; only the page and its prepared assets are deployed. Original PPTs and recordings remain local under `web/`.

## Preview

From the repository root:

```bash
python -m http.server 8000 --directory docs/website
```

Open `http://localhost:8000`. Use an HTTP server rather than opening `index.html` directly so media metadata loads correctly.

For video chapter seeking during playback, use a preview server with HTTP byte-range support; Python's basic HTTP server does not provide it.

## GitHub Pages

The project URL is https://logosroboticsgroup.github.io/FDM/.

1. Include `docs/website/index.html`, both JavaScript files (`app.js`, `results.js`), all three stylesheets (`styles.css`, `diagrams.css`, `results.css`), **all of `docs/website/assets/`**, and `.github/workflows/project-page.yml` in the repository.
2. In repository **Settings → Pages → Build and deployment**, select **GitHub Actions**.
3. Push to the default branch, or run **Deploy FDM project page** manually from Actions. Only the default branch deploys automatically.
4. Use the successful deployment's `page_url` as the live URL. Creating these files locally does not publish the site.

The workflow uploads only the website and prepared assets. Raw recordings, PowerPoint files, media tooling, and local render intermediates are not deployed. All site assets use relative paths, including on `/FDM/`. If the repository moves, update the resource links, Open Graph image URL, and both main README links.

## Sources and editorial decisions

- Method, numerical results and figures: supplied `ICLR27_Forwar_Dynamics_Models.pdf` and figure PDFs in the matching ZIP.
- Public title: **Forward Dynamics Model** (singular), as specified by the author. The supplied PDF remains unmodified and uses the older plural title.
- Authors and institutions: repository README and manuscript.
- `gift/` contains the box-packing-and-closing experiment.
- Success rates are manuscript results, not newly measured results from this release. A clip's duration is not inference latency.
- `demo.mp4` is exported from the complete, updated 18-slide PowerPoint. Slides are rendered with LibreOffice; the five embedded comparison videos play in full at 1× speed, positioned in their original slide rectangles. PowerPoint build animations are flattened into static slide compositions. A derived copy uses the requested singular title and omits the submission number; the original PPT is unchanged. `demo-narrated.mp4` adds an English AI female voice to the clean video, timed to the 18 existing narration cues. No music or subtitle overlays are added.

## Media and narration

- `assets/hero/`: one silent H.264 cover video joining all five FDM w/ VLM tasks, plus chapter timestamps and WebP fallback posters, from the original FDM w/ VLM third-camera recordings. The five full recordings play consecutively at 1× speed, then loop; task buttons seek within the same video and follow the active chapter. Background playback pauses offscreen or in a hidden tab, respects manual pause, and starts with a static poster when reduced motion is preferred. The cover reuses the page's existing paper, sage and forest colors and self-hosted typefaces.
- `assets/demo-narrated.mp4`: the embedded and downloadable overview, with English female AI narration (Kokoro v1.0, `af_heart`) and no subtitle track or burned-in captions. The original H.264 stream is copied without re-encoding; AAC audio and MP4 fast-start support browser playback.
- `assets/demo.mp4`: preserved silent, clean source for narration exports.
- `assets/demo-captioned.mp4`: legacy burned-in subtitle export, no longer linked by the page.
- `assets/demo.en.srt` and `assets/demo.en.vtt`: retained editorial sources; SRT timing drives the narration. The webpage does not attach a caption track.
- `assets/comparisons/`: 20 H.264/yuv420p synchronized composites with MP4 fast-start and WebP posters. Each is 640 × 720: third view at 640 × 480 above left/right wrist views at 320 × 240 each. Shorter views hold their final frame. Original videos remain locally in `web/real-exp/`.
- `assets/comparisons.json`: durations and any incomplete view names for each composite.
- `assets/*.{pdf,webp}`: original figure PDFs and raster derivatives.
- Architecture comparison and the full MoT pipeline are inline SVG in `index.html`, styled by `diagrams.css`. Text and arrows stay sharp when zoomed. The pipeline opens by default and follows the training/inference controls. Arrow animations pause offscreen, in hidden tabs, when collapsed, or via each figure's pause button; reduced motion and disabled JavaScript retain static diagrams. Narrow screens stack the architecture panels and allow horizontal scrolling of the full pipeline. Original PDFs remain linked below both figures.
- The simplified pipeline shares the same animation controls; its generation and backward paths stop at inference. Every remaining disclosure opens by default. The video transcript disclosure and video subtitle track have been removed.
- `results.js`, `results.css`, and `assets/results.json` provide interactive real-robot, LIBERO, RoboTwin, ablation, and efficiency comparisons. All 158 numerical entries were checked against Tables 2–5 and Figure 5 of the published arXiv paper. Success bars start at zero and retain all reported baselines; efficiency charts label their units and preferred direction. Bars animate only when a reader changes a selection, respecting reduced motion. Exact values are available in an expanded table and downloadable JSON. The real-robot average chart and full real-robot table are also present in static HTML.
- `assets/future-perturbation.{svg,pdf}`, `assets/gradient-alignment.{svg,pdf}`, and `assets/real_results_bar.svg` preserve the supplied paper figures as vectors. SVGs are direct PyMuPDF exports from the source PDFs, with text converted to paths. Captions use the published paper's figure numbering (5–7). The perturbation zero line is explicitly identified as an architectural property; the curves have not been reconstructed from guessed data.
- Fonts: DM Sans for body text, Libre Caslon Display for webpage headings, and Instrument Serif in the prepared video graphics, self-hosted under the SIL Open Font License; license files are in `assets/fonts/`.

To regenerate derived figures, videos and subtitles from source material (not needed for hosting):

```bash
pip install Pillow pypdfium2
# Install LibreOffice Impress and ffmpeg with libx264/libass support, then:
python docs/website/tools/prepare_media.py
```

The script uses the already downloaded fonts. Rendering intermediates stay in `playground/website/render/`. Keep `assets/comparisons.json` in sync. Poster and social-image generation is included in the media preparation script.

To re-export only the demo from an updated PPT, run `python docs/website/tools/export_ppt.py`. To rebuild only the 20 three-view comparisons, run `python docs/website/tools/compose_views.py`.

To generate the narrated demo after exporting the clean source:

```bash
python -m venv playground/website/voiceover/.venv
playground/website/voiceover/.venv/bin/pip install kokoro-onnx==0.6.1 soundfile
curl -fL -o playground/website/voiceover/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
curl -fL -o playground/website/voiceover/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin
playground/website/voiceover/.venv/bin/python docs/website/tools/narrate_demo.py
```

Speech synthesis runs locally on CPU with [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx). `--voice`, `--speed`, `--input`, `--subtitles`, and `--output` can be overridden. Each cue begins 150 ms after its slide boundary, with only minimal pitch-preserving speed adjustment when needed to fit. Per-cue loudness normalization keeps the narration consistent; experiment footage continues silently after each task introduction. Models, cached speech, the assembled WAV, and `timing.json` remain in ignored `playground/website/voiceover/`. Only the final MP4 belongs in website assets.

To regenerate the continuous cover video, chapter timestamps and five posters, run `python docs/website/tools/prepare_hero.py` (requires ffmpeg and the original recordings in `web/real-exp/`).
