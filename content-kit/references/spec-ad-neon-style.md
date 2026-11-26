# Style reference: "spec ad" with one neon line (the user's favourite style)

Source: a guide by Refael Levi (refael-ai.com), "how we made the Yellow ad with Claude". Saved because the user loves this look.
Use it for promos/product videos when the user asks for "the neon style", "ספק אד", or "like the Yellow ad".

## The look
- 20s promo, black background with a soft brand-colour radial glow in the centre, studio feel, faint glowing dust.
- One continuous neon line runs behind everything and connects every element across all screens. Only curves, never sharp corners;
  every new segment starts in the direction the previous one ended.
- Real app screenshots: inside a CSS 3D phone, and as cut-out rounded cards.
- Hebrew RTL headlines, heavy weight (Rubik 900), one word highlighted in the brand colour with glow. Words enter from blur(22px)+scale 1.35, stagger 0.18s.
- Narrator (deep, formal male voice) + music that stays under the voice (only a few dB carve).

## Structure
- A wide "world strip" of 7 panels × 1920px. The camera moves in x between panels (0.5s, power3.inOut); inside each panel a slow push 1.0→1.03.
- One paused, seek-safe GSAP timeline (no real-time animation). 16:9 1920×1080 @60fps (adapt to 9:16 for reels).
- Opening: 1s logo pop (scale 0→1 back.out(2.4), rotate -12→0, breathe, shrink out back.in at 0.76s). Wrap the whole film in an inner
  timeline and add it at master.add(tl, 1.0) so nothing else moves; shift all audio +1s. pop in, whoosh out.

## The neon line (3 layers of the same SVG path, linecap round)
1. halo: stroke #ffb300, width 28, blur(16px), opacity .6
2. tube: stroke brand yellow, width 7, double drop-shadow
3. core: stroke #fffbe8, width 2.4
Draws with strokeDashoffset length→0. A glowing "head" (white-yellow radial dot + thin light streak) rides the tip using
keyframes from getPointAtLength, rotated to the path direction; when the line stops at a joint the head fades (opacity 0, scale .3, .25s).

## Recurring moves
- Phone: CSS 330×660, radius 54, black bezel, Dynamic Island. Enters rotationY 28 / z -260 → rotationY -10 (expo.out), keeps turning slowly, a light sheen passes.
  The line comes in from bottom-right, its last segment vertical, and continues into a closed rounded-rect loop (r 60) 14px around the phone.
- Selection: frame the chosen card with a 3-layer neon frame 10px around it (same radius), drawn in .3s, plus a tap ripple. Cards enter from the left, expo.out, stagger .07.
  Cut cards from screenshots with a 4× supersampled mask, downscale LANCZOS for smooth edges.
- Pay button: pill cut-out, scale .5 / x -380 → in with back.out(1.4); press scale .94 (.07s); a pill-shaped neon frame just before; green "paid" tag (#2fd06e, white tick) back.out(2.2); soft pop, no loud click.
- Transition: the line peels off the loop's bottom, curves down (soft bezier) and exits the panel edge exactly when the camera moves; it continues at the same height on the next panel. whoosh on every camera move.
- Split: two symmetric paths from one point around a card (r 60), same length/duration/ease, each with its own head; they meet on the far side and continue as one.
- Star of 5: icons on a regular pentagon (r 280) around a centre item, the gap facing the incoming line; straight equal rays, each icon pops (back.out(2.6), .2s apart).
  Counter ticks (e.g. ₪0→₪50 every .07s) on the key spoken word, with a flash and a hit.
- Fly-out: a transparent PNG object on a top layer climbs, then accelerates (power3.in) into the camera to scale 5 with motion blur; start the final transition as it fills the frame.
- End: brand-colour circle clip-path 0→1200px in .16s (power1.in) with a hit, logo in from scale 1.2 (expo.out), then a black credit card with a glowing underline (scaleX 0→1).
- Privacy: any real code/barcode/plate in screenshots is painted out and replaced with dummy data (not blurred).

## Sound
- VO script 15–16s, one short sentence per screen. ElevenLabs, deep formal male Hebrew voice; add niqqud to words that get misread and re-record only that line.
- Process: normalise to -16 LUFS, slight deepening: asetrate=44100*0.95,aresample=44100,atempo=1.0526,bass=g=3:f=140.
- Transcribe the VO and sync headlines, transitions and SFX to word timings.
- Music bed throughout at ~0.34 with a gentle carve under the voice (strength ~0.3) so it never disappears.

## Production notes for this environment
- HyperFrames' hosted compose is not available from Claude Code; build the HTML+GSAP page locally (gsap from npm, the CDNs are blocked)
  and render frames with the pre-installed Playwright Chromium by seeking the paused timeline, then encode with ffmpeg.
- Client rules still apply on top of this style (palette, logo rules, no women's singing for Haredi/Torah audiences, etc.).
