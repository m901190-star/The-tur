# Content kit

Daily content suggestions for two social-media clients, produced by a scheduled Claude routine.

## Clients

| Client | Profile | Platforms | Content |
|---|---|---|---|
| מועצת יש"ע (Yesha Council) | `clients/yesha/client.json` (logo, white logo, palette) | Facebook, Instagram | Posts + reels |
| תוכן אחד / הבורסה (Haredi podcast) | `tochen-echad` profile in the `pro-video-editing` skill | Facebook, Instagram | Reels from episodes + posts |

`clients/yesha/brand-kit.png` shows the approved look (quote card 4:5, reel 9:16).

## Daily output

Every run writes `daily/YYYY-MM-DD/` with, per client: `post.md` (Facebook + Instagram text), `post.png` (1080x1350 graphic) and `reel.md` (reel idea + script).

## Ideas log

`ideas-log.md` lists every idea already suggested, one line each, so ideas are not repeated.
