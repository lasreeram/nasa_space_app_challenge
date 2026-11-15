# NASA Space Apps Challenge: New Horizons Graphic Novel

A graphic novel about the NASA New Horizons mission to Pluto. The story, characters and hand-drawn sketches are ours. Super intelligence only produces the visuals, through a reproducible workflow that keeps the characters consistent from panel to panel.

## How it works

1. **Hand-drawn sketches.** The characters (for example Alan, and the New Horizons craft) are drawn by hand on paper and scanned.
2. **Dataset preparation.** The scanned sheet is split into single images, cleaned, cropped and captioned, so a model learns the character rather than the page layout.
3. **LoRA training.** A small LoRA (learned weights) is trained per character or subject on an online GPU (Kaggle or Colab).
4. **Panel generation.** ComfyUI, running on an online GPU, loads the LoRA and generates one image per panel from the script, with a sketch optionally guiding pose and composition.
5. **Review and layout.** We pick the best panels, then add speech bubbles and assemble pages.

Stills are easier to keep consistent than video, and small panel-to-panel drift is acceptable in comics.

## Repository layout

| Path | Contents |
|---|---|
| `new_horizon_sketches.ipynb` | Splits and prepares the hand-drawn sketch sheet. |
| `new_horizons.ipynb` | Panel generation experiments for the New Horizons story. |
| `sketches_alan/` | Sketches of Alan (1024 px) with captions, including face-restyled and hand-drawn-style variants. |
| `sketches_alan_full/` | Full-size Alan sketches. |
| `sketches_alan_lora/` | Cleaned Alan images and captions used as the LoRA training set. |
| `sketches_craft/` | Spacecraft sketches with `restyled` and `nh_restyled` variants. |
| `sketches_craft_full/` | Full-size spacecraft sketches. |
| `sketches_craft_lora/` | Training set for the spacecraft LoRA. |
| `sketches_craft_nh_lora/` | Training set for the New Horizons-specific spacecraft LoRA. |
| `gallery/` | Generated results comparing prompts (`style`, `story`, `specific`) with no LoRA and LoRA epochs 6 and 8. Open `gallery/index.html`. |
| `comparison_first_output.png` | Comparison of the first generated panel. |
| `research/` | Mission research: New Horizons images, Deep Space Network (DSN) handover and site-spacing diagrams, and a Doppler effect notebook. |

## Image conventions

- Sketches are named `sketch_<n>_1024.png`, with a same-named `.txt` caption.
- Captions describe the subject in plain words, for example "hand-drawn pencil sketch of alan, front view portrait, black and white graphite on white paper".
- Training images are flattened to a white background, cropped to the figure and padded to a long side of 1024 px.

## Reproducing the results

1. Open `new_horizon_sketches.ipynb` to split a scanned sketch sheet into single images.
2. Prepare a training folder (cleanup, crop, bucket sizes, captions).
3. Train a LoRA on Kaggle or Colab using the `*_lora` folders as the dataset.
4. Run ComfyUI on an online GPU, load the LoRA, and generate panels with `new_horizons.ipynb`.
5. Compare checkpoints in `gallery/`.

Fix the seed for each chosen panel so it can be regenerated.

## Credits

Story, characters and sketches by the team. Mission facts come from public NASA New Horizons material. Images are generated with super intelligence tools and are always based on our own drawings.
