# Apple tvOS Decoded UI Asset Catalogs Summary

**Milestone**: M2 (UI Architecture & Asset Reverse Engineering)  
**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap / Apple TV 4K 1st Gen)  
**Total Catalogs Decoded**: 19  
**Total Facets**: 1,887  
**Total Renditions**: 79,113  
**Total Extracted Bitmaps (PNG)**: 490  
**Total Extracted Vectors (PDF)**: 84  

---

## 1. Master Catalog Table

| Application / Bundle | Size | Facets | Renditions | PNGs | PDFs | Target Profile | Decoded JSON Manifest |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AppStore.app** | 13,073,384 B | 58 | 137 | 40 | 27 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`AppStore_assets.json`](./AppStore_assets.json) |
| **AppleTV.app** | 359,208 B | 6 | 15 | 9 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`AppleTV_assets.json`](./AppleTV_assets.json) |
| **Arcade.app** | 13,448,728 B | 58 | 137 | 40 | 27 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`Arcade_assets.json`](./Arcade_assets.json) |
| **HeadBoard.app** | 666,808 B | 44 | 93 | 75 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`HeadBoard_assets.json`](./HeadBoard_assets.json) |
| **PineBoard.app** | 116,088 B | 12 | 39 | 10 | 10 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`PineBoard_assets.json`](./PineBoard_assets.json) |
| **PreBoard.app** | 25,512 B | 1 | 2 | 2 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`PreBoard_assets.json`](./PreBoard_assets.json) |
| **Setup.app** | 27,624 B | 5 | 13 | 3 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`Setup_assets.json`](./Setup_assets.json) |
| **Siri.app** | 175,400 B | 26 | 77 | 10 | 20 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`Siri_assets.json`](./Siri_assets.json) |
| **TVCRDService.app** | 20,200 B | 1 | 2 | 2 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVCRDService_assets.json`](./TVCRDService_assets.json) |
| **TVDiagnostics.app** | 97,288 B | 9 | 13 | 10 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVDiagnostics_assets.json`](./TVDiagnostics_assets.json) |
| **TVMusic.app** | 8,585,224 B | 85 | 195 | 100 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVMusic_assets.json`](./TVMusic_assets.json) |
| **TVNowPlayingService.app** | 359,416 B | 33 | 82 | 31 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVNowPlayingService_assets.json`](./TVNowPlayingService_assets.json) |
| **TVPhotos.app** | 1,998,568 B | 41 | 83 | 44 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVPhotos_assets.json`](./TVPhotos_assets.json) |
| **TVSearch.app** | 1,215,048 B | 6 | 15 | 8 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVSearch_assets.json`](./TVSearch_assets.json) |
| **TVSystemBulletinService.app**| 101,448 B | 16 | 44 | 16 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVSystemBulletinService_assets.json`](./TVSystemBulletinService_assets.json) |
| **TVSystemMenuService.app** | 19,512 B | 1 | 4 | 0 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`TVSystemMenuService_assets.json`](./TVSystemMenuService_assets.json) |
| **AssistiveTouch.app** | 555,480 B | 126 | 288 | 0 | 0 | tvOS 4K UHD (`idiom 3, subtype 3840`) | [`AssistiveTouch_assets.json`](./AssistiveTouch_assets.json) |
| **CoreGlyphs.bundle** | 91,411,496 B | 1,280 | 77,697 | 50 | 0 | Universal SF Symbols (`CoreGlyphs`) | [`CoreGlyphs_assets.json`](./CoreGlyphs_assets.json) |
| **MobileCoreTypes.bundle** | 768,472 B | 79 | 177 | 40 | 0 | System UTI File Type Icons | [`MobileCoreTypes_assets.json`](./MobileCoreTypes_assets.json) |

---

## 2. Key UI Asset Categories

### 2.1 Picture-in-Picture & Windowing Icons (`PineBoard.app`)
- Extracted vector PDFs and raster bitmaps for Picture-in-Picture controls:
  - `pip-icon-deactivate`
  - `pip-icon-enter`
  - `pip-icon-fullscreen`
  - `pip-icon-info`
  - `pip-icon-move-top-left`
  - `pip-icon-move-top-right`
  - `pip-icon-move-bottom-left`
  - `pip-icon-move-bottom-right`
  - `pip-icon-swap`
- Remote interaction hints:
  - `control-center-hint-tv-button` (visual remote diagram showing user how to hold TV button for Control Center)
  - `control-center-icon-sleep` (bed/moon sleep icon)

### 2.2 Parallax Multi-Layer Card Stacks (`HeadBoard.app`)
- `AppPreloadGrid` (Front, Middle, Back layer content sets)
- `PreloadAsset-Dark-Generic`
- `PreloadAsset-Dark-Generic16x9`
- `PreloadAsset-Dark-GenericFlowcase`
- `PreloadAsset-Dark-GenericPoster`
- `PreloadAsset-Dark-GenericSquare`
- `PreloadAsset-Dark-GenericTopShelfBanner`

### 2.3 System SF Symbols (`CoreGlyphs.bundle`)
- 1,280 system glyphs covering:
  - Numbered circles (`0.circle` to `50.circle.fill`)
  - Transport controls (`play.fill`, `pause.fill`, `forward.fill`, `backward.fill`)
  - Device icons (`tv.fill`, `applewatch`, `airpods`, `gamecontroller.fill`)
  - System status indicators (`wifi`, `gear`, `bell.fill`, `battery.100`)
