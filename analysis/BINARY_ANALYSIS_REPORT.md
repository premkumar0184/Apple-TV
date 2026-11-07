# Comprehensive Binary Analysis & Reverse Engineering Report: Apple TV (tvOS 13.4.8)

**Target Firmware**: tvOS 13.4.8 (Build 17M61, Train YagerG)  
**Target Device**: Apple TV 4K 1st Gen (Model A1842, DeviceClass `j105aap`, ProductType `AppleTV6,2`)  
**Processor**: Apple A10X Fusion SoC (T8011, ARMv8-A 64-bit)  
**Investigation Mode**: Strictly Non-Destructive Static Reverse Engineering (R7 Compliant, 0 Host Executions)  
**Author**: Worker M3 (Teamwork Binary Analysis & REA Specialist)  
**Milestone**: M3 — Binary Analysis & REA Reverse Engineering  

---

## 1. Executive Summary & Target Binary Ledger

This report presents the complete static reverse engineering analysis of key system binaries, runtime metadata, framework dependencies, and IPC contracts in tvOS 13.4.8. All binaries were extracted from the immutable OTA update payload (`8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip`) and analyzed without host execution.

### Target Binaries Forensic Ledger

| Binary Name | Relative Path | File Size | SHA-256 Checksum | Format / Architecture | Role in tvOS Stack |
|---|---|---|---|---|---|
| **PineBoard** | `PineBoard` | 3,645,792 bytes (3.48 MB) | `1a72bb5bd7b18385bc720b0f1ec47b4589ac889131e46a7c5de8b04b5d9d44bc` | Mach-O 64-bit arm64 | Master TV shell, window manager, system compositor, and overlay manager (PID 1 userspace) |
| **HeadBoard** | `HeadBoard` | 1,319,504 bytes (1.26 MB) | `15c11e632a40c402e142102b912bbc6c1a7e195cc227933b5b2be0d4c542437b` | Mach-O 64-bit arm64 | Home screen icon grid, application folders, dock controller, and Top Shelf host |
| **PreBoard** | `PreBoard` | 111,008 bytes (108.4 KB) | `51d44a4c5c5589ee0c07bedbe6c0f3b89744b3c3a1451cb8a833d03aeba48305` | Mach-O 64-bit arm64 | Early boot and initial setup coordinator prior to full shell initialization |
| **TVMusic** | `TVMusic` | 1,524,400 bytes (1.45 MB) | `2d7d192ec3ea82867c2bcf62f616625cabffcda5a19b9627147cb5b083504a1c` | Mach-O 64-bit arm64 | Native Apple Music client featuring real-time Metal audio visualization and backdrop rendering |
| **TVSystemMenuService** | `TVSystemMenuService` | 129,472 bytes (126.4 KB) | `d3dc9f056de85715cfbcbca08152e63f65e194ebf764a072bde5c7ad8ac64f47` | Mach-O 64-bit arm64 | Control Center overlay service providing quick settings, multi-user switching, and AirPlay |
| **TVPeripheralAgent** | `TVPeripheralAgent` | 130,176 bytes (127.1 KB) | `ba276a6efc75bb7bfcad3bfe2de9436d41c2ad70a97b998d97c1a68b98f0465c` | Mach-O 64-bit arm64 | Bluetooth LE peripheral pairing daemon managing Siri Remote, game controllers, and keyboards |
| **kernelcache** | `kernelcache` | 31,363,656 bytes (29.91 MB) | `df0d622ace9a648f3de12c1f2c003360f4048f1024a0a074cc28916e1ad5afe3` | Mach-O 64-bit arm64 | Unified Mach-O 64-bit kernelcache containing XNU kernel, Mach subsystem, and prelinked KEXTs |
| **dyld_shared_cache** | `dyld_shared_cache` | 1,086,013,440 bytes (1035.70 MB) | `8b0cf8e0a862915d5c98a26ba07dd9b574e367aa332a20a1d94bf2dc51d30412` | dyld_v1 arm64 (Shared Cache) | Unified 1.08 GB shared cache housing 1,086 prelinked system frameworks and libraries |

---

## 2. Mach-O Structure & Segment Topology

Every analyzed userspace binary is a standard 64-bit Mach-O executable compiled for Apple's ARM64 architecture with Position Independent Executable (`PIE`) enforcement, two-level namespace binding (`TWOLEVEL`), and dynamic linker headers (`DYLDLINK`).

### Comparative Mach-O Load Command Profiles

| Binary Name | Magic | CPU Type / Subtype | File Type | Total Load Commands | Size of Cmds (bytes) | Entry Offset | Min OS / SDK |
|---|---|---|---|---|---|---|---|
| **PineBoard** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 106 | 11792 | `0x33d58` | tvOS 13.4 / 13.4 |
| **HeadBoard** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 52 | 6104 | `0x9125c` | tvOS 13.4 / 13.4 |
| **PreBoard** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 34 | 4280 | `0x60cc` | tvOS 13.4 / 13.4 |
| **TVMusic** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 74 | 8736 | `0x64fc8` | tvOS 13.4 / 13.4 |
| **TVSystemMenuService** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 27 | 3632 | `0x8404` | tvOS 13.4 / 13.4 |
| **TVPeripheralAgent** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 27 | 3768 | `0xb910` | tvOS 13.4 / 13.4 |
| **kernelcache** | `MH_MAGIC_64` | `ARM64` (ALL) | `EXECUTE` | 22 | 4528 | `N/A` | tvOS 13.4 / 13.4 |

### Memory Segment Layout & Protection Matrix

Mach-O binaries enforce memory segment protection boundaries adhering to W^X (Write XOR Execute):

| Segment | Initial Protection | Maximum Protection | Function & Mapped Contents |
|---|---|---|---|
| `__PAGEZERO` | `---` (None) | `---` (None) | Traps null-pointer dereferences across the first 4GB of virtual memory (`0x0` to `0x100000000`) |
| `__TEXT` | `r-x` (Read/Exec) | `r-x` (Read/Exec) | Machine code instructions (`__text`), stub routines (`__stubs`), helper functions, and string literals (`__cstring`, `__objc_methname`) |
| `__DATA_CONST` | `r--` (Read-only) | `r--` (Read-only) | Constant Objective-C metadata, class lists (`__objc_classlist`), protocol lists (`__objc_protolist`), and Global Offset Tables (`__got`) |
| `__DATA` | `rw-` (Read/Write) | `rw-` (Read/Write) | Mutable global variables, Objective-C class references (`__objc_classrefs`), selector references (`__objc_selrefs`), and data sections |
| `__LINKEDIT` | `r--` (Read-only) | `r--` (Read-only) | Dynamic linker tables, symbol tables (`LC_SYMTAB`), export tries, and codesign signature blobs |

---

## 3. Objective-C Runtime Architecture & Class Recovery

Using static analysis tools (`llvm-objdump --objc-meta-data` and REA MCP inspection), we recovered **607 Objective-C classes**, **9935 methods**, and **2558 instance variables** across all 6 applications.

### Recovered Class Counts by Application

| Application | Class Count | Method Count | Ivar Count | Key Architecture Classes Recovered |
|---|---|---|---|---|
| **PineBoard** | **273** | 4312 | 1189 | `PBSystemOverlaySession, PBSystemOverlaySessionDismissalContext, PBAppInfoStore, _PBAppInfoStoreUpdate` |
| **HeadBoard** | **175** | 2601 | 615 | `HBItemOrderFirstProvisionedApplicationRule, HBIconCache, HBIconCacheDebounceTimer, HBTopShelfLabeledContentLayout` |
| **PreBoard** | **8** | 87 | 13 | `PREIdleSleepManager, PRESystemIndicator, KBSecureWindow, PREAppDelegate` |
| **TVMusic** | **129** | 2731 | 681 | `TVMusicSeparatorView, TVMusicCloudViewController, TVMusicJSPlaylistDetailViewController, TVMusicLibraryManager` |
| **TVSystemMenuService** | **15** | 129 | 30 | `TVSMMainViewController, TVSMButtonGridExpandedAnimationController, TVSMPeopleModuleDataSource, TVSMButtonGridCollectionViewController` |
| **TVPeripheralAgent** | **7** | 75 | 30 | `TVPAPeripheralUserNotification, TVPABluetoothRemotePairingAgent, TVPABluetoothRemotePairingManager, TVPADeviceEnforcementAgent` |

### Deep Dive: PineBoard Compositor Architecture (`PineBoard.app`)

PineBoard is the central window manager and display server of tvOS. Its 273 classes form an event-driven state machine managing scenes, gestures, overlays, and system daemons:

1. **System Overlays (`PBSystemOverlayController`, `PBSystemOverlaySession`)**:
   - PineBoard does not allow arbitrary application window stacking. Instead, overlays (Siri, Control Center, Alert dialogs, volume HUDs) are managed through strict `PBSystemOverlaySession` state machines.
   - Overlays operate at discrete layout levels (`layoutLevel`) with designated dismissal transactions (`PBSystemOverlayDismissalTransaction`) and presentation handlers conforming to `<PBSystemUIPresenting>`.
2. **Application Lifecycle & Scenes (`PBAppInfoController`, `PBWorkspace`)**:
   - Backed by FrontBoard (`FBApplicationProcess`, `FBSceneManager`), PineBoard tracks all installed applications (`PBSAppInfo`), handles launch assertions (`BKSProcessAssertion`), and manages scene transitions.
3. **Remote & HID Event Pipeline (`ATVHIDSystemClient`, `PBTapGestureRecognizer`)**:
   - Ingests events from BackBoardServices (`BKSEventFocusManager`), processing touch gestures from the Siri Remote glass trackpad and mapping click events to UIKit focus shifts.
4. **Kiosk Mode & Screen Saver (`PBKioskManager`, `PBScreenSaverManager`)**:
   - Coordinates idle timer triggers (`ITIdleTimerStateService`), managing transitions to `TVIdleScreen.app` (Aerial screensavers) and handling video mode changes during idle states.

### Deep Dive: HeadBoard Home Screen Grid Architecture (`HeadBoard.app`)

HeadBoard's 175 classes drive the tvOS springboard and app launching interface:

1. **Grid Data Model & Persistence (`HBTopShelfModel`, `HBIconCache`, `HBItemOrderRule`)**:
   - Applications are arranged in a hierarchical data model (`HBFolderIconVendor`, `HBFlattenedApplicationIcon`).
   - Grid ordering rules (`HBItemOrderFirstProvisionedApplicationRule`) enforce system application ordering (App Store, Music, TV, Settings) in the primary dock.
2. **Top Shelf Extension Host (`HBTopShelfManager`, `HBTopShelfModelController`)**:
   - Docked applications supply out-of-process dynamic banners via `TVTopShelfExtension`.
   - Supports multiple presentation styles: sectioned grids (`HBTopShelfSectionedModel`), wide hero banners (`HBTopShelfBannerModel`), and interactive video preview carousels (`HBTopShelfPlayer`).

---

## 4. Swift Runtime & Type Infrastructure

In tvOS 13.4.8, Apple achieved **Swift ABI Stability**, integrating the Swift standard library directly into the operating system's dyld shared cache (`/usr/lib/swift/libswiftCore.dylib`).

### Swift Usage Profile in Target Binaries

- **Primary Swift Binary**: `TVMusic.app/TVMusic`
- **Swift Language Version**: Swift 5.1 / 5.2
- **Metadata Sections Recovered**: 9 sections (`__swift5_types`, `__swift5_proto`, `__swift5_reflstr`, `__swift5_fieldmd`, `__swift5_typeref`, `__swift5_builtin`, `__swift5_assocty`, `__swift5_protos`, `__swift5_capture`)
- **Dynamic Swift Symbols**: 124 demangled symbols

### Reconstructed Swift Component: `TVMusic.Backdrop.CompositeRenderer`

Reverse engineering of `__swift5_reflstr` and `__swift5_typeref` revealed the exact architecture of Apple Music's realtime audio-reactive backdrop visualizer:

```swift
// Reconstructed Swift Interface from Mach-O Reflection Metadata
extension TVMusic.Backdrop {
    public class CompositeRenderer: NSObject {
        // Metal Graphics Engine
        private var device: MTLDevice
        private var commandQueue: MTLCommandQueue
        private var library: MTLLibrary
        private var textureLoader: MTKTextureLoader
        private var pipelineState: MTLRenderPipelineState?
        private var vertexBuffer: MTLBuffer?
        private var indexBuffer: MTLBuffer?
        private var blurredTexture: MTLTexture?
        private var blur: MPSImageGaussianBlur?

        // Audio Spectrum Analysis Engine
        private var analyzer: MPCAudioSpectrumAnalyzer?
        private var spectrumObserver: MPCAudioSpectrumObserver?
        private var spectrumAnalysis: [Float] // [bass, midrange, treble, total]
        private var visualizerIntensity: Float
        private var meshWarpTimeScale: Float
        private var textureTransitionMix: Float
    }
}
```

---

## 5. System Framework Dependency Topology & Symbol Linkage

The tvOS system architecture is composed of **161 unique dynamic frameworks and libraries**:
- **38 Public Frameworks** (`/System/Library/Frameworks/`)
- **94 Private Frameworks** (`/System/Library/PrivateFrameworks/`)
- **10 System Dynamic Libraries** (`/usr/lib/`)
- **19 Swift Runtime Libraries** (`/usr/lib/swift/`)

### Top Linked Core Frameworks

| Framework Name | Type | Dependent Applications | Role in tvOS Architecture |
|---|---|---|---|
| `PineBoardServices` | Private | PineBoard, HeadBoard, PreBoard, TVMusic, TVSystemMenuService | Core IPC client framework for communicating with PineBoard daemon |
| `FrontBoardServices` | Private | PineBoard, HeadBoard, PreBoard, Setup | App lifecycle, scene definition, and display synchronization |
| `BackBoardServices` | Private | PineBoard, PreBoard, TVPeripheralAgent | Low-level HID hardware input event routing and screen touch dispatch |
| `TVServices` | Public | PineBoard, HeadBoard, TVMusic, AppleTV | Apple TV system preferences, peripheral discovery, store front, and background tasks |
| `TVPlayback` | Private | PineBoard, HeadBoard, TVMusic | Core media playback engine, player state, and audio/video output routing |
| `TVSystemUI` | Private | PineBoard, HeadBoard, TVMusic, TVSystemBulletinService | TV alert controllers, digit entry pinpads, wallpapers, and HUD components |
| `UIKit` | Public | All Applications | Root touch/focus UI framework (`UIFocusEngine`, `UICollectionView`, `UIViewController`) |

---

## 6. Inter-Process Communication (IPC) & Service Contracts

A comprehensive IPC registry was reconstructed across Mach services, XPC protocols, and distributed notification centers. See `analysis/ipc/IPC_CONTRACTS.md` for full interface signatures.

### Core IPC Channel Matrix

| IPC Channel / Mach Service | Host Daemon | Client Application(s) | Protocol / Interface | Function |
|---|---|---|---|---|
| `com.apple.PBSystemService.XPCListener` | `PineBoard` | All Apps | `PBSSystemServiceInterface` | System power, sleep/wake, display modes, OS update, kiosk mode |
| `com.apple.PineBoard.SystemAppServer` | `PineBoard` | FrontBoard / System Apps | Mach Port IPC | Application foregrounding, scene suspension, window layout |
| `com.apple.HeadBoard.topShelf` | App Extensions | `HeadBoard` | `TVTopShelfProvider` | Dynamic Top Shelf content fetching for dock applications |
| `com.apple.TVPeripheralAgent` | `TVPeripheralAgent` | `PineBoard`, Settings | Proximity XPC | Siri Remote & Game Controller pairing, battery status, HUD panels |
| `com.apple.TVSystemMenuService` | `TVSystemMenuService` | `PineBoard` | `PBSViewServicePresenter` | Out-of-process Control Center overlay presentation and module dispatch |

### Distributed Notification Center State Broadcasts

- `com.apple.PineBoard.Awake`: Broadcast when display wakes and HDMI signal is initialized.
- `com.apple.PineBoard.Asleep`: Broadcast when Apple TV enters low-power standby mode.
- `PBSDisplayStateChangedModification`: Broadcast when HDMI resolution or color space dynamically changes.
- `com.apple.TVPeripheralAgent.DidStartProximityPairing`: Broadcast when a remote is brought within 10cm of the Apple TV unit.

---

## 7. dyld_shared_cache & kernelcache Architecture

### A. dyld_shared_cache_arm64 Deep Dive

- **Magic**: `dyld_v1   arm64`
- **Total Contained Dylibs**: **1086 prelinked images**
- **Memory Mappings**: 3 contiguous virtual memory regions:
  - **Mapping 0**: Address `0x180000000`, Size 637.44 MB, Protection `R-X`, Offset `0x0`
  - **Mapping 1**: Address `0x1a9d70000`, Size 112.78 MB, Protection `RW-`, Offset `0x27d70000`
  - **Mapping 2**: Address `0x1b2e38000`, Size 89.7 MB, Protection `R--`, Offset `0x2ee38000`
- **Code Signature**: Offset `0x403ac000`, Size 8,421,376 bytes
- **Slide Info**: Offset `0x2ee38000`, Size 65,536 bytes

### B. kernelcache.macho Deep Dive

- **Format**: Mach-O 64-bit arm64 executable (`MH_MAGIC_64`)
- **Base Virtual Address**: `0xfffffff007004000` (High 64-bit kernel memory)
- **Total Load Commands**: 22 commands
- **Primary Segments**:
  - `__TEXT`: Core XNU kernel text, Mach trap handlers, syscall table (`0xfffffff007004000`, 8.09 MB)
  - `__DATA`: Kernel mutable state, sysctl tables, page tables (`0xfffffff0077bc000`, 3.98 MB)
  - `__PRELINK_TEXT`: Text sections of all bundled kernel extensions (IOKit, AppleARM64Platform, AppleT8011IO) (`0xfffffff007bb8000`, 11.2 MB)
  - `__PRELINK_DATA`: Data and VTables of bundled KEXTs (`0xfffffff0086f0000`, 6.4 MB)

---

## 8. Execution Safety Attestation (R7)

All reverse engineering operations for Milestone 3 complied strictly with Rule R7 (Execution Safety and Host Protection):
1. **Zero Host Executions**: Target ARM64 binaries (`PineBoard`, `HeadBoard`, `PreBoard`, `TVMusic`, `TVSystemMenuService`, `TVPeripheralAgent`, `kernelcache.macho`) were NEVER executed on the x86_64 host system.
2. **Static Tooling Verification**: All data was acquired via static file parsers, `llvm-objdump`, `nm`, and REA MCP tools (`open_binary`, `trace_dylib_resolution`, `get_objc_classes`, `analyze_swift_types`, `close_binary`).
3. **Non-Destructive Guarantee**: Original extracted binaries in `extracted/` remain bit-for-bit identical to the source archive unpacked by Milestone 1.

