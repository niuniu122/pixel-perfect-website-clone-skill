# Pixel Fidelity Guidelines

This reference folds the core rules from prior high-fidelity website clone work into this portable skill. Treat it as the default pixel-perfect website-clone standard when the active workspace has no stricter local instructions.

## Mission

- Prioritize fidelity above implementation preference.
- Treat the live reference as truth. Measure instead of guessing.
- Close the loop with screenshots and pixel diff evidence before claiming completion.
- Iterate aggressively when differences remain: box model, position, font metrics, color, `box-sizing`, `line-height`, transform, asset dimensions, and runtime initialization order are all suspect until measured.
- Keep the work for learning or authorized internal use. Do not present another site's brand, copy, or proprietary assets as a new commercial product.

## Tooling Choice

Default to the smallest stack that can match the reference:

- Static HTML/CSS/JS is acceptable for simple static pages and can be more precise than a framework.
- React + Vite + TypeScript is a reasonable default when component logic is useful.
- Use GSAP + ScrollTrigger for scroll-driven animation, pinning, scrub, reveal, and parallax.
- Use GSAP timeline for complex timed sequences.
- Use SplitText-style logic for character, word, or line text animation.
- Use Motion for React component enter/exit, gesture, and layout animation.
- Use Three.js for 3D, WebGL backgrounds, particles, and shader scenes.
- Use Lenis or ScrollSmoother only when the reference has smooth/inertial scrolling.
- Avoid UI libraries such as Ant Design for marketing-site clones unless the original site itself uses that design language.

## Hard Rules

- Verify section by section; do not build the entire page and check only at the end.
- Every done claim needs diff artifacts and numeric evidence.
- Extract exact colors, fonts, font sizes, weights, line heights, letter spacing, radii, shadows, media dimensions, and breakpoints.
- Never use approximate colors or default fonts when the reference exposes exact values.
- Preserve original responsive behavior. Do not invent breakpoints.
- Preserve original animation triggers, duration, easing, stagger, scrub/pin behavior, and hover/interaction states.
- Console errors, broken images, and 404 local assets are blockers.

## Reference Capture

Capture at least:

- `1920x1000`
- `1440x1000`
- `1024x1000`
- `768x1000`
- `375x812`

For each breakpoint, capture:

- Top viewport screenshot.
- Full-page screenshot.
- Rendered HTML.
- Resource manifest.
- Design-token summary.
- Runtime information for images, videos, canvases, fonts, scripts, and stylesheets.

Scroll through the page once before capture to trigger lazy-loaded media and scroll-linked setup.

## Extraction

Extract and save:

- `tokens.json` or equivalent design summary.
- `assets-manifest.json` or equivalent resource summary.
- Rendered HTML.
- Images, SVGs, videos/posters, fonts, textures, and WebGL assets required for local fidelity.

Turn extracted values into CSS variables, framework tokens, or local constants. Avoid magic values that are not traceable to the reference.

## Build Loop

Use this loop for each page or major section:

1. Capture or measure the reference.
2. Implement the smallest matching structure.
3. Run local capture.
4. Diff against reference.
5. Fix the largest visible difference first.
6. Repeat until the section passes.

For mirrored runtime clones, preserve original DOM, CSS/JS ordering, data attributes, and asset paths as much as possible. Fix only local path/base issues required for localhost.

## Animation Reconstruction

Create an animation inventory:

- Trigger: load, scroll, hover, click, drag, viewport entry, timeline.
- Target: text, image, section, SVG, canvas, WebGL object, sticky UI.
- Timing: duration, delay, stagger.
- Easing: measured or inferred from runtime.
- Scroll behavior: pin, scrub, start/end offsets, smooth-scroll integration.

Map effects to the closest implementation:

- Scroll effects -> GSAP ScrollTrigger.
- Timelines -> GSAP timeline.
- Text splits -> SplitText-style DOM splitting or equivalent.
- Component reveals/gestures -> Motion.
- 3D/canvas/WebGL -> Three.js or mirrored original runtime.

For dynamic media, capture both live and controlled states. Freeze videos to a shared `currentTime`; stabilize canvas/WebGL state when possible.

## Pixel Diff Reading

Diff color convention: magenta/pink means changed pixels.

- Large solid pink regions mean structural mismatch: position, size, color, asset, or layout is wrong.
- Thin pink around text or image edges may be antialiasing noise.
- Percent alone is not enough; inspect whether differences are structural.
- For a strict one-to-one clone, controlled-state diff should be zero where dynamic randomness has been removed.
- If a nonzero diff remains, document the exact cause and get user acceptance before final delivery.

## Definition Of Done

All must pass:

- Required breakpoints captured for reference and replica.
- Top and full-page controlled diffs pass the target threshold, preferably zero for mirrored runtime clones.
- Page heights and screenshot dimensions match.
- Fonts, colors, spacing, media, sticky elements, and layout match.
- Main animations and interaction states match.
- Console has no errors.
- Local required resources return 200.
- Images and videos are loaded and nonblank.
- Checker agent returns `PASS` when multi-agent QA is required.

## Anti-Patterns

- Do not claim completion without diff evidence.
- Do not eyeball colors, spacing, or fonts.
- Do not substitute default fonts.
- Do not use a generic UI kit that imposes a different design language.
- Do not ignore mobile breakpoints.
- Do not hide broken resources behind screenshots from a warmed cache.
- Do not treat a live autoplay video-frame diff as a layout failure; use controlled-frame diff to decide.
