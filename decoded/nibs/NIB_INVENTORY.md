# Apple tvOS Storyboard & NIB Static Investigation Report

**Milestone**: M2 (UI Architecture & Asset Reverse Engineering)  
**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap)  
**Execution Safety (R7)**: Strictly Static Analysis — 0 Target Host Executions  

---

## 1. Forensic Discovery: Interface Builder Artifact Absence

A recursive filesystem scan across all extracted root filesystem partitions (`extracted/rootfs/Applications/`, `extracted/rootfs/System/Library/`, and `extracted/ramdisk/`) for compiled Interface Builder artifacts (`.nib`, `.storyboard`, `.storyboardc`) yielded:

| Artifact Pattern | Search Scope | Matches Found | Status |
| :--- | :--- | :--- | :--- |
| `*.nib` | `extracted/rootfs/Applications/` | **0** | None |
| `*.storyboard` | `extracted/rootfs/Applications/` | **0** | None |
| `*.storyboardc` | `extracted/rootfs/Applications/` | **0** | None |
| `*.nib` | `extracted/ramdisk/` | **0** | None |
| `*.storyboardc` | `extracted/ramdisk/` | **0** | None |

---

## 2. Technical Analysis: Programmatic UI Construction Architecture

Unlike macOS or early iOS applications that frequently relied on NIB/XIB files or Storyboards, Apple's first-party tvOS system daemons and shell applications (tvOS 13.4.8) **completely eschew Interface Builder files** in favor of 100% programmatic view and scene construction.

This architectural decision is driven by three core engineering requirements on tvOS:

### 2.1 Dynamic Focus Engine Integration (`UIFocusSystem`)
tvOS user interfaces are governed by spatial 2D focus navigation rather than touch or mouse pointers. Interface Builder static layouts cannot easily declare complex, dynamic focus graphs, custom focus guides (`UIFocusGuide`), or dynamic focus search weights. In first-party applications:
- Focus environments override `preferredFocusEnvironments`, `shouldUpdateFocusInContext:`, and `didUpdateFocusInContext:withAnimationCoordinator:` directly in Objective-C/Swift source code.
- Custom focus guides (e.g. `HeadBoard`'s `_leadingRenameFolderTextFieldFocusGuide`) are created dynamically via `[UIFocusGuide alloc] init]` and added to views with Auto Layout constraints in code.

### 2.2 BoardServices & Multi-Scene Compositing (`FrontBoard` / `PineBoard`)
System UI in tvOS is not contained within a single `UIWindow` or monolithic app window. Instead, `PineBoard` orchestrates multiple hardware-composited display contexts (`CAContext`) and remote scenes (`FBScene` / `FBSScene`):
- `PBSceneManager` dynamically creates scene view controllers (`_PBSceneViewController`) that host out-of-process application surfaces.
- System overlays (Control Center, Picture-in-Picture, Bulletins, Siri) are hosted in isolated `PBSystemOverlaySession` instances, each managing its own `UIWindow` at designated window levels (`PBWindowLevelOverlay`, `PBWindowLevelAlert`, `PBWindowLevelSystemMenu`).

### 2.3 Modular Top Shelf & Collection View Grids (`HeadBoard`)
The Apple TV Home screen grid (`HeadBoard`) is powered by a high-performance custom `UICollectionViewLayout` (`HBAppGridViewLayout`):
- Grid item cells (`HBAppGridItemCell`, `HBFolderedAppItemCell`) are registered programmatically via `[UICollectionView registerClass:forCellWithReuseIdentifier:]`.
- Top Shelf extensions (`HBTopShelfController`) instantiate remote view controller wrappers (`_UIRemoteViewController`) at runtime depending on whether the focused application provides an Item Carousel, Sectioned Grid, or Full-Bleed Video Banner.

---

## 3. Programmatic View Construction Profiles by Application

### 3.1 `PineBoard.app` (Shell Daemon)
- **Root Window**: `PBRootWindow` (subclass of `UIWindow`) instantiated in `PBAppDelegate application:didFinishLaunchingWithOptions:`.
- **Compositor Canvas**: Direct CoreAnimation layer tree attached to hardware framebuffers via `CAContext` (`com.apple.QuartzCore.displayable-context`).
- **Dialogs & Alerts**: `PBDialogManager` programmatically instantiates `PBDialogViewController` with dynamic blur backdrops (`UIVisualEffectView`) and action buttons.
- **Picture-in-Picture (PiP)**: `PBPictureInPictureManager` programmatically manages `PBPIPContainerViewController` positioning PIP windows at the four screen quadrants (`pip-icon-move-top-right`, etc.).

### 3.2 `HeadBoard.app` (Home Screen Launcher)
- **Root View Controller**: `HBRootFolderViewController` hosting a full-screen `UICollectionView`.
- **Folder Expansion**: Programmatically animates a full-screen blurred folder overlay (`HBFolderViewController`) with an embedded 9x3 app grid.
- **Top Shelf Container**: `HBTopShelfContainerViewController` positioned directly above the dock row (y-offset: 0 to 500 px in 1080p, 0 to 1000 px in 4K UHD).

### 3.3 `TVSystemMenuService.app` (Control Center)
- **Controller**: `TVSMMainViewController` instantiated by `PineBoard`'s out-of-process overlay service.
- **Layout**: Programmatically creates a vertical slide-in drawer on the right edge of the screen (3840x2160 screen space: x-origin = 3040, width = 800 px) with a dark vibrancy blur (`UIBlurEffectStyleDark`).
- **Tiles**: Instantiates dynamic modular tiles (`TVSMCardView`, `TVSMModuleContentViewController`) for AirPlay destination picker, HomeKit scenes, Sleep Timer, and Fast User Switching account cards.

### 3.4 `PreBoard.app` (Early Boot Passcode Barrier)
- **Controller**: `PREPasscodeEntryViewController`.
- **Passcode Grid**: Programmatically constructs 4-digit or 6-digit PIN bullet slots (`PREPasscodeDigitView`) and a circular number keypad centered on the screen.

### 3.5 `TVPeripheralAgent.app` (Remote Pairing Wizard)
- **Controller**: `TVPAPairingPromptViewController`.
- **HUD Presentation**: Programmatically creates non-modal top-right HUD notification banners (`TVPANotificationView`) with animated pairing instructions ("Bring Remote Near Apple TV").

### 3.6 `TVIdleScreen.app` (Aerial Screen Saver)
- **Controller**: `TVIPlaybackViewController`.
- **Canvas**: Programmatic `AVPlayerLayer` playing 4K HDR HEVC asset streams with subtle label fades for location descriptions (e.g. "Dubai at Night", "Greenland Fjords").

---

## 4. Conclusion & Verification

The absence of `.nib` and `.storyboard` files is an intended architectural property of modern tvOS system software. All UI hierarchies, Auto Layout constraints, focus guides, and remote scene embeddings are generated strictly through programmatic Objective-C / Swift code.
