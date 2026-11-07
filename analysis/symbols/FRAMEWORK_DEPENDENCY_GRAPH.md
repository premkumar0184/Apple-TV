# tvOS 13.4.8 System Framework Dependency Graph & Architecture

Synthesized from Mach-O load commands (`LC_LOAD_DYLIB`, `LC_LOAD_WEAK_DYLIB`, `LC_REEXPORT_DYLIB`) across core tvOS system applications.

## 1. High-Level Dependency Statistics

- **Applications Analyzed**: 11
- **Total Unique Frameworks & Libraries**: 161
  - **Public Frameworks (`/System/Library/Frameworks/`)**: 38
  - **Private Frameworks (`/System/Library/PrivateFrameworks/`)**: 94
  - **System Dynamic Libraries (`/usr/lib/`)**: 10
  - **Swift Runtime Libraries (`/usr/lib/swift/`)**: 19

## 2. Application Dependency Footprint

| Application | Binary Path | Linked Dylibs | Public Frameworks | Private Frameworks | Swift Runtimes |
|---|---|---|---|---|---|
| **PineBoard** | `extracted/rootfs/Applications/PineBoard.app/PineBoard` | **91** | 24 | 59 | 0 |
| **TVMusic** | `extracted/rootfs/Applications/TVMusic.app/TVMusic` | **58** | 21 | 16 | 18 |
| **Setup** | `extracted/rootfs/Applications/Setup.app/Setup` | **58** | 19 | 33 | 0 |
| **AppStore** | `extracted/rootfs/Applications/AppStore.app/AppStore` | **44** | 13 | 11 | 17 |
| **HeadBoard** | `extracted/rootfs/Applications/HeadBoard.app/HeadBoard` | **36** | 16 | 15 | 0 |
| **TVIdleScreen** | `extracted/rootfs/Applications/TVIdleScreen.app/TVIdleScreen` | **22** | 10 | 7 | 0 |
| **PreBoard** | `extracted/rootfs/Applications/PreBoard.app/PreBoard` | **19** | 5 | 9 | 0 |
| **AppleTV** | `extracted/rootfs/Applications/AppleTV.app/AppleTV` | **19** | 8 | 7 | 0 |
| **TVSystemBulletinService** | `extracted/rootfs/Applications/TVSystemBulletinService.app/TVSystemBulletinService` | **13** | 7 | 3 | 0 |
| **TVSystemMenuService** | `extracted/rootfs/Applications/TVSystemMenuService.app/TVSystemMenuService` | **12** | 5 | 4 | 0 |
| **TVPeripheralAgent** | `extracted/rootfs/Applications/TVPeripheralAgent.app/TVPeripheralAgent` | **11** | 5 | 3 | 0 |

---

## 3. Core Subsystem Framework Clusters

### A. Shell & Window Management (PineBoard Subsystem)
- `PineBoardServices.framework`: Inter-process communication client library for all tvOS applications communicating with PineBoard.
- `FrontBoard.framework` & `FrontBoardServices.framework`: Low-level application lifecycle, scene creation, process assertions, and display layout management.
- `BackBoardServices.framework`: HID event routing, discrete dispatching rules, and display fence handles.
- `BaseBoard.framework` & `BaseBoardUI.framework`: Foundational primitives (`BSTransaction`, `BSSimpleAssertion`, `BSAnimationSettings`).
- `RunningBoardServices.framework`: Process identity, target tracking, and lifecycle assertion management.

### B. User Interface & Home Grid (HeadBoard Subsystem)
- `HeadBoardModel.framework`: Data model representing the tvOS home screen icon grid, folders, and layout persistency.
- `HeadBoardUI.framework`: Visual presentation layer, focus-aware icon cells, and folder animation physics.
- `TVUIKit.framework` & `TVMLKit.framework`: tvOS-specific TV card views, poster buttons, and XML template rendering.
- `UIKit.framework`: Root UI framework (`UIApplication`, `UICollectionView`, `UIFocusEngine`).

### C. Audio/Video, Playback & Control
- `TVPlayback.framework`: Comprehensive playback controller (`TVPPlayer`, audio sessions, routing).
- `MediaRemote.framework`: Siri remote playback events, command center transport controls.
- `MediaPlaybackCore.framework`: Audio spectrum analysis and queue management.
- `TVCoreSettings.framework` & `ATVSystemState.framework`: Hardware display modes, LED indicators, and audio output sinks.

## 4. Top Most Widely Linked Frameworks & Libraries

| Rank | Framework / Library Name | Category | Dependent Apps Count | Dependent System Apps |
|---|---|---|---|---|
| 1 | `CoreFoundation` | Public Framework | **11** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService, TVSystemMenuService |
| 2 | `Foundation` | Public Framework | **11** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService, TVSystemMenuService |
| 3 | `PineBoardServices` | Private Framework | **11** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService, TVSystemMenuService |
| 4 | `dyld` | System Dynamic Library | **11** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService, TVSystemMenuService |
| 5 | `libSystem.B.dylib` | System Dynamic Library | **11** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService, TVSystemMenuService |
| 6 | `libobjc.A.dylib` | System Dynamic Library | **11** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService, TVSystemMenuService |
| 7 | `UIKit` | Public Framework | **10** | AppStore, AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVSystemBulletinService, TVSystemMenuService |
| 8 | `TVServices` | Public Framework | **9** | AppStore, AppleTV, HeadBoard, PineBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent, TVSystemBulletinService |
| 9 | `CoreGraphics` | Public Framework | **8** | AppStore, HeadBoard, PineBoard, Setup, TVIdleScreen, TVMusic, TVSystemBulletinService, TVSystemMenuService |
| 10 | `QuartzCore` | Public Framework | **8** | AppStore, HeadBoard, PineBoard, Setup, TVIdleScreen, TVMusic, TVSystemBulletinService, TVSystemMenuService |
| 11 | `CoreServices` | Public Framework | **7** | AppStore, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic |
| 12 | `IOKit` | Public Framework | **7** | HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen, TVMusic, TVPeripheralAgent |
| 13 | `AVFoundation` | Public Framework | **6** | AppStore, AppleTV, HeadBoard, PineBoard, TVIdleScreen, TVMusic |
| 14 | `TVMLKit` | Public Framework | **6** | AppleTV, HeadBoard, PineBoard, Setup, TVMusic, TVSystemBulletinService |
| 15 | `TVPlayback` | Private Framework | **6** | AppleTV, HeadBoard, PineBoard, Setup, TVIdleScreen, TVMusic |
| 16 | `TVSystemUI` | Private Framework | **6** | HeadBoard, PineBoard, Setup, TVIdleScreen, TVMusic, TVSystemBulletinService |
| 17 | `libMobileGestalt.dylib` | System Dynamic Library | **6** | AppleTV, HeadBoard, PineBoard, PreBoard, Setup, TVIdleScreen |
| 18 | `Accounts` | Public Framework | **5** | AppStore, HeadBoard, PineBoard, Setup, TVMusic |
| 19 | `AppleMediaServices` | Private Framework | **5** | AppStore, HeadBoard, PineBoard, TVIdleScreen, TVMusic |
| 20 | `AppSupport` | Private Framework | **4** | HeadBoard, PineBoard, Setup, TVIdleScreen |
| 21 | `ManagedConfiguration` | Private Framework | **4** | HeadBoard, PineBoard, Setup, TVMusic |
| 22 | `MediaRemote` | Private Framework | **4** | PineBoard, TVIdleScreen, TVMusic, TVSystemBulletinService |
| 23 | `StoreServices` | Private Framework | **4** | AppStore, AppleTV, PineBoard, Setup |
| 24 | `AVKit` | Public Framework | **3** | AppStore, PineBoard, TVMusic |
| 25 | `AggregateDictionary` | Private Framework | **3** | HeadBoard, PineBoard, Setup |

---

## 5. Complete System Framework Catalog

| Framework Name | Install Name | Category | Version | Apps Count |
|---|---|---|---|---|
| `AMPCoreUI` | `/System/Library/PrivateFrameworks/AMPCoreUI.framework/AMPCoreUI` | Private Framework | `1.0.0` | 1 |
| `ATVSystemState` | `/System/Library/PrivateFrameworks/ATVSystemState.framework/ATVSystemState` | Private Framework | `1.0.0` | 2 |
| `AVFoundation` | `/System/Library/Frameworks/AVFoundation.framework/AVFoundation` | Public Framework | `2.0.0` | 6 |
| `AVKit` | `/System/Library/Frameworks/AVKit.framework/AVKit` | Public Framework | `1.0.0` | 3 |
| `AXRuntime` | `/System/Library/PrivateFrameworks/AXRuntime.framework/AXRuntime` | Private Framework | `1.0.0` | 1 |
| `Accounts` | `/System/Library/Frameworks/Accounts.framework/Accounts` | Public Framework | `1.0.0` | 5 |
| `AggregateDictionary` | `/System/Library/PrivateFrameworks/AggregateDictionary.framework/AggregateDictionary` | Private Framework | `1.0.0` | 3 |
| `AppStoreDaemon` | `/System/Library/PrivateFrameworks/AppStoreDaemon.framework/AppStoreDaemon` | Private Framework | `1.0.0` | 3 |
| `AppStoreKit` | `/System/Library/PrivateFrameworks/AppStoreKit.framework/AppStoreKit` | Private Framework | `1.0.0` | 1 |
| `AppSupport` | `/System/Library/PrivateFrameworks/AppSupport.framework/AppSupport` | Private Framework | `29.0.0` | 4 |
| `AppleAccount` | `/System/Library/PrivateFrameworks/AppleAccount.framework/AppleAccount` | Private Framework | `1.0.0` | 2 |
| `AppleMediaServices` | `/System/Library/PrivateFrameworks/AppleMediaServices.framework/AppleMediaServices` | Private Framework | `1.0.0` | 5 |
| `ApplePushService` | `/System/Library/PrivateFrameworks/ApplePushService.framework/ApplePushService` | Private Framework | `1.0.0` | 1 |
| `AskPermission` | `/System/Library/PrivateFrameworks/AskPermission.framework/AskPermission` | Private Framework | `1.0.0` | 2 |
| `AssetCacheServices` | `/System/Library/PrivateFrameworks/AssetCacheServices.framework/AssetCacheServices` | Private Framework | `111.0.0` | 1 |
| `AssistantServices` | `/System/Library/PrivateFrameworks/AssistantServices.framework/AssistantServices` | Private Framework | `1.0.0` | 1 |
| `AttentionAwareness` | `/System/Library/PrivateFrameworks/AttentionAwareness.framework/AttentionAwareness` | Private Framework | `82.100.1` | 2 |
| `AudioToolbox` | `/System/Library/Frameworks/AudioToolbox.framework/AudioToolbox` | Public Framework | `1000.0.0` | 2 |
| `AuthKit` | `/System/Library/PrivateFrameworks/AuthKit.framework/AuthKit` | Private Framework | `1.0.0` | 2 |
| `AuthKitUI` | `/System/Library/PrivateFrameworks/AuthKitUI.framework/AuthKitUI` | Private Framework | `1.0.0` | 1 |
| `BackBoardServices` | `/System/Library/PrivateFrameworks/BackBoardServices.framework/BackBoardServices` | Private Framework | `1.0.0` | 2 |
| `BaseBoard` | `/System/Library/PrivateFrameworks/BaseBoard.framework/BaseBoard` | Private Framework | `0.0.0` | 3 |
| `BaseBoardUI` | `/System/Library/PrivateFrameworks/BaseBoardUI.framework/BaseBoardUI` | Private Framework | `0.0.0` | 2 |
| `BluetoothManager` | `/System/Library/PrivateFrameworks/BluetoothManager.framework/BluetoothManager` | Private Framework | `1.0.0` | 2 |
| `BulletinBoard` | `/System/Library/PrivateFrameworks/BulletinBoard.framework/BulletinBoard` | Private Framework | `1.0.0` | 1 |
| `CFNetwork` | `/System/Library/Frameworks/CFNetwork.framework/CFNetwork` | Public Framework | `0.0.0` | 1 |
| `Celestial` | `/System/Library/PrivateFrameworks/Celestial.framework/Celestial` | Private Framework | `1.0.0` | 2 |
| `CloudKit` | `/System/Library/Frameworks/CloudKit.framework/CloudKit` | Public Framework | `867.0.0` | 3 |
| `Contacts` | `/System/Library/Frameworks/Contacts.framework/Contacts` | Public Framework | `0.0.0` | 1 |
| `CoreAnalytics` | `/System/Library/PrivateFrameworks/CoreAnalytics.framework/CoreAnalytics` | Private Framework | `1.0.0` | 2 |
| `CoreBluetooth` | `/System/Library/Frameworks/CoreBluetooth.framework/CoreBluetooth` | Public Framework | `1.0.0` | 2 |
| `CoreCDP` | `/System/Library/PrivateFrameworks/CoreCDP.framework/CoreCDP` | Private Framework | `1.0.0` | 1 |
| `CoreCDPUI` | `/System/Library/PrivateFrameworks/CoreCDPUI.framework/CoreCDPUI` | Private Framework | `1.0.0` | 1 |
| `CoreControl` | `/System/Library/PrivateFrameworks/CoreControl.framework/CoreControl` | Private Framework | `1.0.0` | 1 |
| `CoreFoundation` | `/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation` | Public Framework | `1677.104.0` | 11 |
| `CoreGraphics` | `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics` | Public Framework | `1355.22.0` | 8 |
| `CoreImage` | `/System/Library/Frameworks/CoreImage.framework/CoreImage` | Public Framework | `5.0.0` | 2 |
| `CoreLocation` | `/System/Library/Frameworks/CoreLocation.framework/CoreLocation` | Public Framework | `2394.2.24` | 2 |
| `CoreMedia` | `/System/Library/Frameworks/CoreMedia.framework/CoreMedia` | Public Framework | `1.0.0` | 2 |
| `CoreServices` | `/System/Library/Frameworks/CoreServices.framework/CoreServices` | Public Framework | `1069.25.0` | 7 |
| `CoreSpotlight` | `/System/Library/Frameworks/CoreSpotlight.framework/CoreSpotlight` | Public Framework | `1.0.0` | 1 |
| `CoreText` | `/System/Library/Frameworks/CoreText.framework/CoreText` | Public Framework | `1.0.0` | 3 |
| `CoreTime` | `/System/Library/PrivateFrameworks/CoreTime.framework/CoreTime` | Private Framework | `266.3.0` | 2 |
| `CoreUtils` | `/System/Library/PrivateFrameworks/CoreUtils.framework/CoreUtils` | Private Framework | `1.0.0` | 2 |
| `CoreVideo` | `/System/Library/Frameworks/CoreVideo.framework/CoreVideo` | Public Framework | `1.5.0` | 1 |
| `CrashReporterSupport` | `/System/Library/PrivateFrameworks/CrashReporterSupport.framework/CrashReporterSupport` | Private Framework | `1.0.0` | 1 |
| `DuetActivityScheduler` | `/System/Library/PrivateFrameworks/DuetActivityScheduler.framework/DuetActivityScheduler` | Private Framework | `1.0.0` | 1 |
| `FamilyCircle` | `/System/Library/PrivateFrameworks/FamilyCircle.framework/FamilyCircle` | Private Framework | `1.0.0` | 1 |
| `Foundation` | `/System/Library/Frameworks/Foundation.framework/Foundation` | Public Framework | `1677.104.0` | 11 |
| `FrontBoard` | `/System/Library/PrivateFrameworks/FrontBoard.framework/FrontBoard` | Private Framework | `0.0.0` | 2 |
| `FrontBoardServices` | `/System/Library/PrivateFrameworks/FrontBoardServices.framework/FrontBoardServices` | Private Framework | `0.0.0` | 3 |
| `GameKit` | `/System/Library/Frameworks/GameKit.framework/GameKit` | Public Framework | `665.26.0` | 1 |
| `GeoServices` | `/System/Library/PrivateFrameworks/GeoServices.framework/GeoServices` | Private Framework | `1624.56.4` | 1 |
| `GraphicsServices` | `/System/Library/PrivateFrameworks/GraphicsServices.framework/GraphicsServices` | Private Framework | `14.0.0` | 1 |
| `HeadBoardModel` | `/System/Library/PrivateFrameworks/HeadBoardModel.framework/HeadBoardModel` | Private Framework | `1.0.0` | 1 |
| `HeadBoardUI` | `/System/Library/PrivateFrameworks/HeadBoardUI.framework/HeadBoardUI` | Private Framework | `1.0.0` | 1 |
| `HomeKit` | `/System/Library/Frameworks/HomeKit.framework/HomeKit` | Public Framework | `621.7.3` | 2 |
| `IOKit` | `/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit` | Public Framework | `275.0.0` | 7 |
| `IOMobileFramebuffer` | `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer` | Private Framework | `1.0.0` | 1 |
| `IOSurface` | `/System/Library/Frameworks/IOSurface.framework/IOSurface` | Public Framework | `1.0.0` | 1 |
| `ITMLKit` | `/System/Library/PrivateFrameworks/ITMLKit.framework/ITMLKit` | Private Framework | `1.0.0` | 2 |
| `IdleTimerServices` | `/System/Library/PrivateFrameworks/IdleTimerServices.framework/IdleTimerServices` | Private Framework | `1.0.0` | 1 |
| `ImageIO` | `/System/Library/Frameworks/ImageIO.framework/ImageIO` | Public Framework | `0.0.0` | 2 |
| `InstallCoordination` | `/System/Library/PrivateFrameworks/InstallCoordination.framework/InstallCoordination` | Private Framework | `1.0.0` | 1 |
| `IntlPreferences` | `/System/Library/PrivateFrameworks/IntlPreferences.framework/IntlPreferences` | Private Framework | `301.6.0` | 1 |
| `JavaScriptCore` | `/System/Library/Frameworks/JavaScriptCore.framework/JavaScriptCore` | Public Framework | `609.3.5` | 2 |
| `JetEngine` | `/System/Library/PrivateFrameworks/JetEngine.framework/JetEngine` | Private Framework | `1.0.0` | 1 |
| `JetUI` | `/System/Library/PrivateFrameworks/JetUI.framework/JetUI` | Private Framework | `1.0.0` | 1 |
| `ManagedConfiguration` | `/System/Library/PrivateFrameworks/ManagedConfiguration.framework/ManagedConfiguration` | Private Framework | `1.0.0` | 4 |
| `MediaPlaybackCore` | `/System/Library/PrivateFrameworks/MediaPlaybackCore.framework/MediaPlaybackCore` | Private Framework | `0.0.0` | 1 |
| `MediaPlayer` | `/System/Library/Frameworks/MediaPlayer.framework/MediaPlayer` | Public Framework | `1.0.0` | 3 |
| `MediaRemote` | `/System/Library/PrivateFrameworks/MediaRemote.framework/MediaRemote` | Private Framework | `1.0.0` | 4 |
| `MediaServices` | `/System/Library/PrivateFrameworks/MediaServices.framework/MediaServices` | Private Framework | `1.0.0` | 1 |
| `Metal` | `/System/Library/Frameworks/Metal.framework/Metal` | Public Framework | `213.5.3` | 1 |
| `MetalKit` | `/System/Library/Frameworks/MetalKit.framework/MetalKit` | Public Framework | `141.0.0` | 1 |
| `MetalPerformanceShaders` | `/System/Library/Frameworks/MetalPerformanceShaders.framework/MetalPerformanceShaders` | Public Framework | `122.5.5` | 1 |
| `MobileActivation` | `/System/Library/PrivateFrameworks/MobileActivation.framework/MobileActivation` | Private Framework | `0.0.0` | 2 |
| `MobileAsset` | `/System/Library/PrivateFrameworks/MobileAsset.framework/MobileAsset` | Private Framework | `1.0.0` | 1 |
| `MobileBluetooth` | `/System/Library/PrivateFrameworks/MobileBluetooth.framework/MobileBluetooth` | Private Framework | `1.0.0` | 1 |
| `MobileCoreServices` | `/System/Library/Frameworks/MobileCoreServices.framework/MobileCoreServices` | Public Framework | `1069.25.0` | 2 |
| `MobileIcons` | `/System/Library/PrivateFrameworks/MobileIcons.framework/MobileIcons` | Private Framework | `372.0.0` | 1 |
| `MobileObliteration` | `/System/Library/PrivateFrameworks/MobileObliteration.framework/MobileObliteration` | Private Framework | `1.0.0` | 2 |
| `MobileSoftwareUpdate` | `/System/Library/PrivateFrameworks/MobileSoftwareUpdate.framework/MobileSoftwareUpdate` | Private Framework | `1.0.0` | 1 |
| `MobileStoreDemoKit` | `/System/Library/PrivateFrameworks/MobileStoreDemoKit.framework/MobileStoreDemoKit` | Private Framework | `1.0.0` | 2 |
| `MobileWiFi` | `/System/Library/PrivateFrameworks/MobileWiFi.framework/MobileWiFi` | Private Framework | `1.0.0` | 1 |
| `OSASubmissionClient` | `/System/Library/PrivateFrameworks/OSASubmissionClient.framework/OSASubmissionClient` | Private Framework | `1.0.0` | 1 |
| `OnBoardingKit` | `/System/Library/PrivateFrameworks/OnBoardingKit.framework/OnBoardingKit` | Private Framework | `1.0.0` | 3 |
| `Pegasus` | `/System/Library/PrivateFrameworks/Pegasus.framework/Pegasus` | Private Framework | `1.0.0` | 1 |
| `PersistentConnection` | `/System/Library/PrivateFrameworks/PersistentConnection.framework/PersistentConnection` | Private Framework | `1.0.0` | 1 |
| `PineBoardServices` | `/System/Library/PrivateFrameworks/PineBoardServices.framework/PineBoardServices` | Private Framework | `1.0.0` | 11 |
| `Preferences` | `/System/Library/PrivateFrameworks/Preferences.framework/Preferences` | Private Framework | `1.0.0` | 2 |
| `QuartzCore` | `/System/Library/Frameworks/QuartzCore.framework/QuartzCore` | Public Framework | `1.11.0` | 8 |
| `RTCReporting` | `/System/Library/PrivateFrameworks/RTCReporting.framework/RTCReporting` | Private Framework | `1.0.0` | 1 |
| `Radio` | `/System/Library/PrivateFrameworks/Radio.framework/Radio` | Private Framework | `1.0.0` | 1 |
| `RemoteUI` | `/System/Library/PrivateFrameworks/RemoteUI.framework/RemoteUI` | Private Framework | `1.0.0` | 1 |
| `RunningBoardServices` | `/System/Library/PrivateFrameworks/RunningBoardServices.framework/RunningBoardServices` | Private Framework | `223.140.2` | 1 |
| `Security` | `/System/Library/Frameworks/Security.framework/Security` | Public Framework | `59306.140.5` | 1 |
| `Seeding` | `/System/Library/PrivateFrameworks/Seeding.framework/Seeding` | Private Framework | `1.0.0` | 1 |
| `SettingsFoundation` | `/System/Library/PrivateFrameworks/SettingsFoundation.framework/SettingsFoundation` | Private Framework | `1.0.0` | 3 |
| `SetupAssistant` | `/System/Library/PrivateFrameworks/SetupAssistant.framework/SetupAssistant` | Private Framework | `1.0.0` | 2 |
| `SetupAssistantUI` | `/System/Library/PrivateFrameworks/SetupAssistantUI.framework/SetupAssistantUI` | Private Framework | `1.0.0` | 1 |
| `Sharing` | `/System/Library/PrivateFrameworks/Sharing.framework/Sharing` | Private Framework | `1526.37.0` | 1 |
| `SplashBoard` | `/System/Library/PrivateFrameworks/SplashBoard.framework/SplashBoard` | Private Framework | `1.0.0` | 1 |
| `SpringBoardServices` | `/System/Library/PrivateFrameworks/SpringBoardServices.framework/SpringBoardServices` | Private Framework | `1.0.0` | 1 |
| `StoreServices` | `/System/Library/PrivateFrameworks/StoreServices.framework/StoreServices` | Private Framework | `1.0.0` | 4 |
| `SystemConfiguration` | `/System/Library/Frameworks/SystemConfiguration.framework/SystemConfiguration` | Public Framework | `1061.140.1` | 1 |
| `TVContentPartnerKitUI` | `/System/Library/PrivateFrameworks/TVContentPartnerKitUI.framework/TVContentPartnerKitUI` | Private Framework | `1.0.0` | 3 |
| `TVControlServices` | `/System/Library/PrivateFrameworks/TVControlServices.framework/TVControlServices` | Private Framework | `1.0.0` | 1 |
| `TVCoreSettings` | `/System/Library/PrivateFrameworks/TVCoreSettings.framework/TVCoreSettings` | Private Framework | `1.0.0` | 2 |
| `TVHomeSharingServices` | `/System/Library/PrivateFrameworks/TVHomeSharingServices.framework/TVHomeSharingServices` | Private Framework | `1.0.0` | 1 |
| `TVIdleScreenServices` | `/System/Library/PrivateFrameworks/TVIdleScreenServices.framework/TVIdleScreenServices` | Private Framework | `1.0.0` | 2 |
| `TVMLKit` | `/System/Library/Frameworks/TVMLKit.framework/TVMLKit` | Public Framework | `1.0.0` | 6 |
| `TVPhotoSources` | `/System/Library/PrivateFrameworks/TVPhotoSources.framework/TVPhotoSources` | Private Framework | `1.0.0` | 1 |
| `TVPlayback` | `/System/Library/PrivateFrameworks/TVPlayback.framework/TVPlayback` | Private Framework | `1.0.0` | 6 |
| `TVSemanticContextServices` | `/System/Library/PrivateFrameworks/TVSemanticContextServices.framework/TVSemanticContextServices` | Private Framework | `1.0.0` | 1 |
| `TVServices` | `/System/Library/Frameworks/TVServices.framework/TVServices` | Public Framework | `1.0.0` | 9 |
| `TVSystemMenuUI` | `/System/Library/PrivateFrameworks/TVSystemMenuUI.framework/TVSystemMenuUI` | Private Framework | `1.0.0` | 1 |
| `TVSystemUI` | `/System/Library/PrivateFrameworks/TVSystemUI.framework/TVSystemUI` | Private Framework | `1.0.0` | 6 |
| `TVUIKit` | `/System/Library/Frameworks/TVUIKit.framework/TVUIKit` | Public Framework | `1.0.0` | 2 |
| `TVWhatsNewServices` | `/System/Library/PrivateFrameworks/TVWhatsNewServices.framework/TVWhatsNewServices` | Private Framework | `1.0.0` | 2 |
| `TextInput` | `/System/Library/PrivateFrameworks/TextInput.framework/TextInput` | Private Framework | `1.0.0` | 1 |
| `TouchRemote` | `/System/Library/PrivateFrameworks/TouchRemote.framework/TouchRemote` | Private Framework | `1.0.0` | 1 |
| `UIKit` | `/System/Library/Frameworks/UIKit.framework/UIKit` | Public Framework | `61000.0.0` | 10 |
| `UIKitServices` | `/System/Library/PrivateFrameworks/UIKitServices.framework/UIKitServices` | Private Framework | `61000.0.0` | 2 |
| `UserNotificationsServer` | `/System/Library/PrivateFrameworks/UserNotificationsServer.framework/UserNotificationsServer` | Private Framework | `1.0.0` | 1 |
| `VideoSubscriberAccount` | `/System/Library/Frameworks/VideoSubscriberAccount.framework/VideoSubscriberAccount` | Public Framework | `331.70.6` | 1 |
| `VideoToolbox` | `/System/Library/Frameworks/VideoToolbox.framework/VideoToolbox` | Public Framework | `1.0.0` | 1 |
| `VideosUI` | `/System/Library/PrivateFrameworks/VideosUI.framework/VideosUI` | Private Framework | `450.70.7` | 1 |
| `VideosUICore` | `/System/Library/PrivateFrameworks/VideosUICore.framework/VideosUICore` | Private Framework | `450.70.7` | 1 |
| `WatchListKit` | `/System/Library/PrivateFrameworks/WatchListKit.framework/WatchListKit` | Private Framework | `1.0.0` | 1 |
| `dyld` | `/usr/lib/dyld` | System Dynamic Library | `1.0.0` | 11 |
| `iTunesCloud` | `/System/Library/PrivateFrameworks/iTunesCloud.framework/iTunesCloud` | Private Framework | `1.0.0` | 1 |
| `iTunesStore` | `/System/Library/PrivateFrameworks/iTunesStore.framework/iTunesStore` | Private Framework | `1.0.0` | 1 |
| `libAccessibility.dylib` | `/usr/lib/libAccessibility.dylib` | System Dynamic Library | `1.0.0` | 3 |
| `libMobileGestalt.dylib` | `/usr/lib/libMobileGestalt.dylib` | System Dynamic Library | `1.0.0` | 6 |
| `libSystem.B.dylib` | `/usr/lib/libSystem.B.dylib` | System Dynamic Library | `1281.100.1` | 11 |
| `libapp_launch_measurement.dylib` | `/usr/lib/libapp_launch_measurement.dylib` | System Dynamic Library | `1.0.0` | 1 |
| `libarchive.2.dylib` | `/usr/lib/libarchive.2.dylib` | System Dynamic Library | `9.2.0` | 1 |
| `liblockdown.dylib` | `/usr/lib/liblockdown.dylib` | System Dynamic Library | `1.0.0` | 2 |
| `libobjc.A.dylib` | `/usr/lib/libobjc.A.dylib` | System Dynamic Library | `228.0.0` | 11 |
| `libsqlite3.dylib` | `/usr/lib/libsqlite3.dylib` | System Dynamic Library | `308.5.0` | 1 |
| `libswiftAVFoundation.dylib` | `/usr/lib/swift/libswiftAVFoundation.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftCore.dylib` | `/usr/lib/swift/libswiftCore.dylib` | Swift Runtime | `1103.2.25` | 2 |
| `libswiftCoreAudio.dylib` | `/usr/lib/swift/libswiftCoreAudio.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftCoreFoundation.dylib` | `/usr/lib/swift/libswiftCoreFoundation.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftCoreGraphics.dylib` | `/usr/lib/swift/libswiftCoreGraphics.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftCoreImage.dylib` | `/usr/lib/swift/libswiftCoreImage.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftCoreMedia.dylib` | `/usr/lib/swift/libswiftCoreMedia.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftDarwin.dylib` | `/usr/lib/swift/libswiftDarwin.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftDispatch.dylib` | `/usr/lib/swift/libswiftDispatch.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftFoundation.dylib` | `/usr/lib/swift/libswiftFoundation.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftMetal.dylib` | `/usr/lib/swift/libswiftMetal.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftMetalKit.dylib` | `/usr/lib/swift/libswiftMetalKit.dylib` | Swift Runtime | `0.0.0` | 1 |
| `libswiftModelIO.dylib` | `/usr/lib/swift/libswiftModelIO.dylib` | Swift Runtime | `0.0.0` | 1 |
| `libswiftNetwork.dylib` | `/usr/lib/swift/libswiftNetwork.dylib` | Swift Runtime | `0.0.0` | 1 |
| `libswiftObjectiveC.dylib` | `/usr/lib/swift/libswiftObjectiveC.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftQuartzCore.dylib` | `/usr/lib/swift/libswiftQuartzCore.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftUIKit.dylib` | `/usr/lib/swift/libswiftUIKit.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftos.dylib` | `/usr/lib/swift/libswiftos.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libswiftsimd.dylib` | `/usr/lib/swift/libswiftsimd.dylib` | Swift Runtime | `0.0.0` | 2 |
| `libutil.dylib` | `/usr/lib/libutil.dylib` | System Dynamic Library | `1.0.0` | 1 |
