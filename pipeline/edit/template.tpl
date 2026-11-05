<!doctype html>
<html lang="pt-BR" data-resolution="{{ORIENT}}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={{W}}, height={{H}}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {
        --ground: #000;
        --ink: #ffffff;
        --accent: {{ACCENT}};
        --font-display: "{{FONT}}", sans-serif;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: {{W}}px; height: {{H}}px; overflow: hidden; background: var(--ground); }
      #root { position: relative; width: {{W}}px; height: {{H}}px; overflow: hidden; background: var(--ground); font-family: var(--font-display); }
      video.bg { position: absolute; left: 0; top: 0; width: {{W}}px; height: {{H}}px; object-fit: cover; z-index: 1; }
      video.meme { position: absolute; z-index: 5; }
      .landscape video.meme.side { right: 110px; top: 210px; height: 600px; width: auto; max-width: 820px; }
      .landscape video.meme.center { left: 310px; top: 60px; width: 1300px; height: auto; }
      .portrait video.meme.side, .portrait video.meme.center { left: 0; right: 0; margin: 0 auto; top: 330px; height: 620px; width: auto; max-width: 1000px; }
      video.meme.full { left: 0; top: 0; width: {{W}}px; height: {{H}}px; object-fit: cover; z-index: 6; }
      #captions { position: absolute; left: 0; top: 0; width: {{W}}px; height: {{H}}px; z-index: 8; pointer-events: none; }
      .grp {
        position: absolute; left: 0; width: {{W}}px; text-align: center; visibility: hidden; opacity: 0; overflow: visible;
        font-weight: 700; letter-spacing: -0.01em; line-height: 1.1; color: var(--ink);
        text-shadow: 0 3px 14px rgba(0, 0, 0, 0.85), 0 0 3px rgba(0, 0, 0, 0.9);
      }
      .landscape .grp { bottom: 112px; font-size: 66px; }
      .portrait .grp { bottom: 640px; font-size: 82px; padding: 0 70px; }
      .w { display: inline-block; margin: 0 0.12em; }
      #vignette { position: absolute; left: 0; top: 0; width: {{W}}px; height: {{H}}px; z-index: 7; pointer-events: none;
        background: linear-gradient(to top, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 32%); }
      .portrait #vignette { background: linear-gradient(to top, rgba(0,0,0,0) 20%, rgba(0,0,0,0.45) 38%, rgba(0,0,0,0) 56%); }
      #offer { position: absolute; z-index: 9; opacity: 0; display: flex; align-items: center; gap: 14px;
        background: rgba(10, 10, 10, 0.78); color: var(--ink); border-radius: 999px; padding: 16px 30px;
        font-size: 38px; font-weight: 700; border: 2px solid var(--accent); }
      .landscape #offer { left: 80px; top: 80px; }
      .portrait #offer { left: 0; right: 0; margin: 0 auto; width: max-content; top: 220px; }
      #offer .dot { width: 16px; height: 16px; border-radius: 999px; background: var(--accent); }
      #hook { position: absolute; left: 0; width: {{W}}px; top: 170px; z-index: 9; text-align: center; padding: 0 60px; opacity: 0;
        font-size: 54px; font-weight: 800; line-height: 1.15; color: var(--ink);
        text-shadow: 0 3px 16px rgba(0,0,0,0.9); }
      #fade, #fadein { position: absolute; left: 0; top: 0; width: {{W}}px; height: {{H}}px; background: #000; z-index: 20; opacity: 0; pointer-events: none; }
      #fadein { opacity: 1; }
    </style>
  </head>
  <body>
    <div id="root" class="{{ORIENT}}" data-composition-id="main" data-start="0" data-duration="{{DUR}}" data-width="{{W}}" data-height="{{H}}" data-fps="30">
      {{MEDIA}}
      <div id="vignette"></div>
      <div id="captions" class="clip" data-start="0" data-duration="{{DUR}}" data-track-index="4" data-track-kind="captions">
        {{CAPTIONS}}
      </div>
      {{OVERLAYS}}
      <div id="fade"></div>
      <div id="fadein"></div>
    </div>
    <script>
      {{JS}}
    </script>
  </body>
</html>
