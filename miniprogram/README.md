# WeChat Mini Program — Flywheel Layers

Minimal Mini Program that plays `media/flywheel-layers-soothing.mp4` (H.264 + AAC).

## Open in WeChat DevTools

1. Install [WeChat DevTools](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html).
2. **Import project** → choose this folder: `miniprogram/`.
3. AppID: use test/tourist ID (`touristappid` is already set), or paste your real AppID.
4. Compile → tap play on the video.

No server required for local package video (file is ~542KB, under main-package limits).

## Use your own AppID / cloud video later

- Replace `"appid": "touristappid"` in `project.config.json`.
- To host remotely: upload the MP4 to HTTPS CDN / WeChat cloud, set `src` in `pages/index/index.js`, and allowlist the domain in the Mini Program admin console.
