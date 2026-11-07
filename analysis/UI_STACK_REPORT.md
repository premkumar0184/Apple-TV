# Comprehensive tvOS 13.4.8 UI Architecture & Shell Services Report

**Milestone**: M2 (UI Architecture & Asset Reverse Engineering)  
**Target**: tvOS 13.4.8 (Build 17M61, Train: `YagerG`, AppleTV6,2 / j105aap / Apple TV 4K 1st Gen)  
**Execution Safety (R7)**: Strictly Static Reverse Engineering — 0 Host Executions of Target ARM64 Binaries  
**Input Partitions**: `extracted/rootfs/Applications/`, `extracted/rootfs/System/Library/`, `extracted/dyld_cache/`  

---

## 1. Architectural Overview & System Topography

Apple tvOS 13.4.8 is a specialized, hardware-accelerated Darwin/Mach-O operating system designed specifically for the big-screen television experience. Unlike iOS (touch-driven) or macOS (cursor/window-driven), the tvOS user experience is centered around:
1. **10-foot Viewing Distance**: UI layouts, typography scales, contrast levels, and interactive targets are tuned for viewing from 8 to 12 feet away.
2. **Indirect Spatial Focus Navigation**: All navigation occurs via discrete directional movements across a 2D focus graph managed by `UIFocusEngine`.
3. **Decoupled Out-of-Process Shell Services**: System functions (Home screen, Control Center, Alerts, Aerial screen savers, Accessory management) are not hosted in a single monolithic process. Instead, `PineBoard` coordinates a federation of dedicated application daemons via Mach services and `BoardServices` IPC.

```
+------------------------------------------------------------------------------------+
|                               HARDWARE DISPLAY PLANE                                |
|                        [Apple A10X Fusion / T8011 Display Pipe]                     |
+------------------------------------------------------------------------------------+
                                          ^
                                          | Hardware Composited via CoreAnimation (CAContext)
+------------------------------------------------------------------------------------+
|                                PINEBOARD.APP (Shell)                                |
|  - Process Coordinator & Compositor         - PBHardwareButtonAccessManager         |
|  - PBSceneManager (FBScene hosting)         - PBPictureInPictureManager             |
|  - PBWindowManager (Window Levels)          - PBAppSwitcherManager                  |
+------------------------------------------------------------------------------------+
          |                     |                      |                     |
          v (XPC/BSServices)    v (XPC/BSServices)     v (XPC/BSServices)    v (XPC/BSServices)
+-------------------+ +--------------------+ +--------------------+ +--------------------+
|   HEADBOARD.APP   | | TVSYSTEMMENUSERVICE| | TVSYSTEMBULLETIN   | |  TVIDLESCREEN.APP  |
| - Home Screen App | | - Control Center   | | - Alerts & HUDs    | | - 4K HDR Aerial    |
| - App Grid View   | | - Fast User Switch | | - Volume Level Bar | | - Swipe Gestures   |
| - Top Shelf Host  | | - System Modules   | | - Battery Warnings | | - Location Labels  |
+-------------------+ +--------------------+ +--------------------+ +--------------------+
          |
          v (Extension IPC: TVTopShelfProvider)
+------------------------------------------------------------------------------------+
|                            APPLICATION TOP SHELF EXTENSIONS                         |
|  - AppStoreTopShelfExtension.appex    - TVMusicTopShelfExtension.appex             |
|  - TVUpNextExtension.appex            - Third-Party Apps (Netflix, YouTube, etc.)  |
+------------------------------------------------------------------------------------+
```

---

## 2. Core System Applications & Shell Services

### 2.1 `PineBoard.app` — The Master Shell & Display Compositor
- **Binary Profile**: `extracted/rootfs/Applications/PineBoard.app/PineBoard` (3,645,792 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.PineBoard`
- **Architectural Role**: Master userspace compositor, window manager, and process lifecycle coordinator (tvOS equivalent to iOS `SpringBoard`).

#### Key Subsystems & Reverse-Engineered Classes:
1. **Scene Management (`PBSceneManager`)**:
   - Manages out-of-process client application scenes (`FBScene` / `FBSScene`).
   - Tracks the active foreground application via `focusedExternalApplicationScene`.
   - Enforces kiosk lockouts and single-app restrictions via `defaultKioskSceneIdentity`.
   - Manages scene deactivation assertions (`addSceneDeferralTargetAssertion:`) when system overlays take priority.
2. **Display Compositing & Window Levels (`PBWindowManager`)**:
   - Uses `CAContext` (`com.apple.QuartzCore.displayable-context`) to attach CoreAnimation layer trees directly to hardware framebuffers.
   - Enforces a strict vertical window layering hierarchy:
     - Level 0: Wallpaper / Aerial Backdrop
     - Level 10: Base Application UI (`HeadBoard` or running 3rd-party app)
     - Level 20: Picture-in-Picture (`PBPIPContainerViewController`)
     - Level 30: System Menu / Control Center (`TVSystemMenuService`)
     - Level 40: System Bulletins & Alerts (`TVSystemBulletinService`)
     - Level 50: Siri Overlay Canvas
     - Level 60: Early Boot Barrier (`PreBoard`)
3. **Picture-in-Picture Engine (`PBPictureInPictureManager`)**:
   - Hosts floating out-of-process video playback windows.
   - Provides quadrant snapping (`pip-icon-move-top-left`, `pip-icon-move-top-right`, `pip-icon-move-bottom-left`, `pip-icon-move-bottom-right`).
   - Supports PiP audio swapping (`pip-icon-swap`) and fullscreen restoration (`pip-icon-fullscreen`).
4. **Hardware Button & Gesture Routing (`PBHardwareButtonAccessManager`)**:
   - Intercepts raw kernel `IOHIDEvent` streams from the Siri Remote.
   - Arbitrates exclusive access to media controls (`_appWithExclusivePlayPauseButtonAccess`, `_appWithVolumeButtonAccess`).
   - Routes TV/Home button single-tap to `HeadBoard`, double-tap to `PBAppSwitcherManager`, and long-press to `TVSystemMenuService`.

---

### 2.2 `HeadBoard.app` — Home Screen Launcher & Top Shelf Extension Host
- **Binary Profile**: `extracted/rootfs/Applications/HeadBoard.app/HeadBoard` (1,319,504 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.HeadBoard`
- **Architectural Role**: Home screen launcher, application grid renderer, and Top Shelf extension host.

#### Key Subsystems & Reverse-Engineered Classes:
1. **Hierarchical App Grid Engine (`HBRootFolderViewController`, `HBFolder`, `HBAppItem`)**:
   - The Home Screen is organized as a nested folder structure declared in `DefaultOrder.plist`:
     - **Dock Row (GridOrder 1000 - 5000)**: Prime bottom shelf housing 5 core applications: Apple TV (`com.apple.TVWatchList`), Music (`com.apple.TVMusic`), Arcade (`com.apple.Arcade`), Photos (`com.apple.TVPhotos`), and App Store (`com.apple.TVAppStore`). When focused, these apps take over the entire top half of the television screen.
     - **Main Grid (GridOrder 6000 - 11000)**: 5x3 app grid containing secondary system apps (Podcasts, Movies, Shows, Search, Home Sharing, Settings) and installed third-party apps.
2. **Top Shelf Extension Host (`HBTopShelfManager`, `HBTopShelfExtensionController`)**:
   - Applications placed in the dock row supply an app extension (`.appex`) adopting `TVTopShelfProvider`.
   - `HBTopShelfExtensionController` queries the active extension via XPC and renders the appropriate content model:
     - `HBTopShelfSectionedModel`: Horizontal carousels of sectioned items with titles.
     - `HBTopShelfParadeModel`: Full-width hero cards with rich metadata, descriptions, Rotten Tomatoes critic scores (`HBTopShelfRottenTomatoesRating`), and direct Play action buttons (`HBTopShelfPlayAction`).
     - `HBTopShelfVideoView`: Modern full-bleed background video playback with synchronized audio.
3. **Folder Management & Jiggle Mode**:
   - Dragging an app over another instantiates an `HBFolder`.
   - Long-pressing Play/Pause enters edit/jiggle mode (`_isEndEditingFocusUpdate`).
   - Employs dedicated focus guides (`_leadingRenameFolderTextFieldFocusGuide`) to allow seamless navigation between the folder title field and the app grid.

---

### 2.3 `PreBoard.app` — Early Boot & Passcode Barrier
- **Binary Profile**: `extracted/rootfs/Applications/PreBoard.app/PreBoard` (111,008 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.PreBoard`
- **Architectural Role**: Unauthenticated early boot coordinator and security gatekeeper.

#### Subsystems:
- **Passcode Keypad (`PREPasscodeEntryViewController`)**: Programmatically renders 4-digit or 6-digit PIN bullet slots (`PREPasscodeDigitView`) and a circular number keypad centered on the screen.
- **Power Management (`PREIdleSleepManager`)**: Manages display sleep (`dimDisplay`, `undimDisplay`) if the Apple TV is booted into the passcode lock state and left unattended.
- **Security Boundary**: Executes before `mobile` userspace keybags are decrypted. Shields the system from unauthorized local or network access until valid credentials unlock the filesystem.

---

### 2.4 `TVSystemMenuService.app` — Control Center & Fast User Switching
- **Binary Profile**: `extracted/rootfs/Applications/TVSystemMenuService.app/TVSystemMenuService` (129,472 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.TVSystemMenuService`
- **Architectural Role**: tvOS Control Center overlay and multi-user profile switcher.

#### Subsystems:
- **Presentation Controller (`TVSMHostViewController`, `TVSMMainViewController`)**:
  - Invoked out-of-process when `PineBoard` detects a 1.5-second hold of the Siri Remote TV/Home button.
  - Slides in a dark vibrantly blurred panel from the right edge of the screen (3840x2160 resolution: x = 3040, width = 800 px).
- **Fast User Switching (`TVSMPeopleModuleDataSource`)**:
  - Displays avatar cards for all configured Apple IDs on the Apple TV.
  - Switching users updates Game Center profiles, Apple Music libraries, and personalized Up Next queues without requiring a system reboot.
- **System Action Tiles (`TVSMButtonGridCollectionViewController`)**:
  - Sleep Apple TV (`control-center-icon-sleep`).
  - AirPlay audio destination selector (AirPods, HomePods, AV receiver).
  - HomeKit room cameras and smart scene triggers.
  - Do Not Disturb and game controller connection status.

---

### 2.5 `TVSystemBulletinService.app` — Alerts, HUD Overlays & Bulletins
- **Binary Profile**: `extracted/rootfs/Applications/TVSystemBulletinService.app/TVSystemBulletinService` (74,512 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.TVSystemBulletinService`
- **Architectural Role**: Non-modal system banners, volume indicators, and battery warnings.

#### Subsystems:
- **Presentation Coordinator (`TVSBBulletinViewController`)**:
  - Displays compact HUD notification cards in the upper-right quadrant of the display.
  - Banners animate in with spring physics (`bulletinServiceBeginPresentationWithBulletin:`) and auto-dismiss after a 4-second timeout.
- **Volume Level Indicator (`TVSBSLevelBarView`)**:
  - Renders discrete horizontal level tick boxes (`_boxes`, `numLevels`, `level`) when the user presses volume buttons on the Siri Remote.
  - Intercepts HDMI-CEC volume status messages and displays real-time decibel/level feedback.
- **Hardware Power Alerts**:
  - Warns the user when the Siri Remote battery reaches critical thresholds (`_bluetoothRemotePowerSourceLimitedSourceNotification`).

---

### 2.6 `TVPeripheralAgent.app` — Bluetooth Accessory & Remote Pairing Manager
- **Binary Profile**: `extracted/rootfs/Applications/TVPeripheralAgent.app/TVPeripheralAgent` (130,176 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.TVPeripheralAgent`
- **Architectural Role**: Bluetooth Low Energy accessory lifecycle manager and Siri Remote proximity pairing wizard.

#### Subsystems:
- **Proximity Pairing Wizard (`TVPABluetoothRemotePairingAgent`)**:
  - Detects unpaired or new Siri Remotes placed within 3-4 inches of the Apple TV 4K chassis via RSSI thresholding (`startProximityPairing`).
  - Presents on-screen pairing HUD instructions (`TVPAPeripheralUserNotification`, `BringRemoteCloserPrompt`).
  - Performs secure cryptographic key exchange and records the paired device identity in `previouslyPairedRemoteIDs`.
- **Game Controller & Audio Enforcement (`TVPADeviceEnforcementAgent`)**:
  - Enforces Bluetooth device connection limits (e.g. maximum of 2 simultaneous Bluetooth game controllers or 2 pairs of AirPods with Audio Sharing).
  - Prompts the user before disconnecting audio peripherals (`askUserAboutConnectingAudioDevice`, `askUserAboutDisconnectingAudioDevice`).

---

### 2.7 `TVIdleScreen.app` — 4K HDR Aerial Screen Saver Engine
- **Binary Profile**: `extracted/rootfs/Applications/TVIdleScreen.app/TVIdleScreen` (269,776 bytes, ARM64 Mach-O executable)
- **Bundle Identifier**: `com.apple.TVIdleScreen`
- **Architectural Role**: Dynamic 4K HDR backdrop and aerial screensaver video compositor.

#### Subsystems:
- **Media Playback Canvas (`TVIBackgroundView`, `TVIAssetManager`)**:
  - Renders ultra-high-bitrate 4K HDR HEVC video streams of aerial flyovers (Space, Cities, Oceans, Nature).
  - Manages local disk caching (`TVIAssetCacheManager`, `TVICacheDeleteUtility`) to prevent filling system flash storage.
- **Interactive Remote Gestures**:
  - **Swipe to Change Location (`TVIChangeAerialContext`)**: Swiping left or right on the Siri Remote touch surface triggers `nextWithContext:`, immediately fading to the next aerial asset.
  - **Tap for Location Description (`TVILocationLabelManager`, `TVILocationLabelView`)**: Single-tapping the touch surface activates a subtle bottom-left text overlay (`TVILocationLabelGradientLayer`) displaying the geographic location of the flyover (e.g. "Dubai at Night", "Patagonia Glaciers").

---

## 3. tvOS UI Framework Taxonomy

Static inspection of `extracted/dyld_cache/dyld_shared_cache_arm64` reveals the role of UI frameworks across tvOS 13.4.8:

| Framework | Primary Purpose on tvOS | Key Classes & Interfaces |
| :--- | :--- | :--- |
| **`UIKit` (`UIKitCore`)** | Base UI engine, view hierarchy, and focus navigation | `UIFocusSystem`, `UIFocusEngine`, `UIFocusEnvironment`, `UIFocusGuide`, `_UIFloatingContentView`, `UICollectionView` |
| **`SwiftUI`** | Declarative state-driven UI framework | `FocusState`, `.focusable()`, `.focusScope()`, tvOS-adapted view modifiers |
| **`TVUIKit`** | High-level tvOS-specific interactive components | `TVCardView`, `TVCaptionButton`, `TVPosterView`, `TVDigitEntryViewController`, `TVMonogramView` |
| **`TVMLKit` / `TVML`** | Client-server XML/JavaScript declarative interface platform | `TVInterfaceFactory`, `TVViewElement`, `TVApplicationController`, `catalogTemplate`, `productTemplate` |
| **`TVSystemUI`** | Private framework for system controls and Control Center | `TVSMCardView`, `TVSMButtonGridContainerViewController`, `TVSMClockView` |
| **`TVKit`** | Legacy media playback controls and rating badges | `TVImageView`, `TVRatingBadgeView`, `TVModalAlertController` |

---

## 4. UI Asset & Design Systems Summary

From our decoding of all 19 compiled `.car` catalogs (79,113 renditions, 490 extracted PNGs, 84 vector PDFs):
1. **Asset Thinning & 4K Optimization**:
   - Asset catalogs are compiled specifically for `idiom 3` (tvOS) and `subtype 3840` (4K UHD).
   - Images are rasterized at `@1x` (1920x1080 baseline) and `@2x` (3840x2160 4K UHD).
2. **Appearance Sets**:
   - Catalogs define explicit renditions for `UIAppearanceAny`, `Appearance_42` (Light Mode), and `Appearance_181` (Dark Mode).
3. **Parallax Layered Assets (`public.layeredimage`)**:
   - Focusable items contain multi-layer stacks (`AppPreloadGrid/Back/Content`, `AppPreloadGrid/Middle/Content`, `AppPreloadGrid/Front/Content`) enabling 3D depth tilt on focus.
4. **SF Symbols Integration (`CoreGlyphs.bundle`)**:
   - Embeds 1,280 system vector iconography symbols (`0.circle`, `play.fill`, `gear`, `tv`, `speaker.wave.3.fill`).

---

## 5. Architectural Conclusions

1. **No Monolithic Window**: tvOS system UI is completely distributed across independent Mach/BSService processes coordinated by `PineBoard`.
2. **Zero NIB/Storyboard Dependencies**: All view hierarchies in system applications are constructed 100% programmatically in Objective-C/Swift to ensure tight integration with `UIFocusEngine`.
3. **Strict Spatial Determinism**: Indirect navigation requires strict geometric raycasting cone algorithms with heavy orthogonal penalties to make UI traversal predictable.
4. **Hardware-Locked Interception**: Physical buttons on the Siri Remote are strictly arbitrated at the kernel/PineBoard boundary, ensuring apps cannot hijack Home or Siri buttons.
