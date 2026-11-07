# tvOS 13.4.8 Inter-Process Communication (IPC) & Service Contracts

Synthesized from static binary analysis of core system applications (`PineBoard`, `HeadBoard`, `TVSystemMenuService`, `TVPeripheralAgent`, `TVMusic`).

## 1. Architectural IPC Overview

Apple TV (tvOS 13.4.8) utilizes a multi-layered IPC topology:
1. **Mach Services (`bootstrap_register` / `bootstrap_look_up`)**: Low-level kernel port-based communication used for core daemon readiness and BackBoard/FrontBoard event routing.
2. **XPC Services & `NSXPCInterface`**: High-level, type-safe bidirectional RPC channels connecting applications to system daemons (`PineBoardServices`, `HeadBoard.topShelf`).
3. **Distributed Notifications (`NSDistributedNotificationCenter` / `notify_post`)**: Cross-process publish/subscribe message bus for system state changes (sleep/awake, display mode changes, thermal alerts, pairing events).
4. **View Services (`PBSViewServicePresenter` / `_UIHostedWindow`)**: Out-of-process UI compositing for system overlays (Control Center, Siri, PIN entry, power dialogues).

---

## 2. PineBoard System Services (`com.apple.PBSystemService.XPCListener`)

- **Daemon**: `PineBoard.app/PineBoard` (PID 1 userspace shell compositor)
- **Mach Service Endpoint**: `com.apple.PBSystemService.XPCListener`
- **Client Framework**: `PineBoardServices.framework` (`PBSSystemService`, `PBSSystemServiceConnection`)
- **Role**: Master administrative IPC interface allowing privileged and unprivileged applications to query system state, request power state transitions, trigger kiosk animations, and observe display settings.

### Formal Contract: `PBSSystemServiceInterface`

```objc
@protocol PBSSystemServiceInterface <NSObject>

// Power Management & Lifecycle
- (void)sleepSystemWithReason:(NSString *)reason completion:(void (^)(BOOL success, NSError *error))completion;
- (void)wakeSystemWithReason:(NSString *)reason completion:(void (^)(BOOL success, NSError *error))completion;
- (void)rebootSystemWithReason:(NSString *)reason;

// Display Modes & Video Calibration
- (void)fetchCurrentDisplayModeWithCompletion:(void (^)(PBSDisplayMode *mode))completion;
- (void)updateDisplayModeWithRequest:(PBSDisplayManagerUpdateRequest *)request completion:(void (^)(BOOL success))completion;
- (void)presentDisplayAssistantWithRequest:(PBSDisplayAssistantPresentationRequest *)request;

// OS Update & Migration
- (void)scanForOSUpdatesWithOptions:(PBSOSUpdateScanOptions *)options completion:(void (^)(PBSOSUpdateDescriptor *descriptor, NSError *error))completion;
- (void)startOSUpdateDownloadWithDescriptor:(PBSOSUpdateDescriptor *)descriptor progressHandler:(void (^)(PBSOSUpdateOperationProgress *progress))progress;
- (void)reportRecoveryModeState:(PBSRecoveryModeReporter *)reporter;

// Application Icon, Switcher & Kiosk Management
- (void)fetchAppInfoConfigurationWithCompletion:(void (^)(PBSAppInfoConfiguration *config))completion;
- (void)prepareKioskApplicationAnimation:(PBSPrepareKioskApplicationAnimationAction *)action reply:(void (^)(PBSPrepareKioskApplicationAnimationActionResponse *response))reply;
- (void)performKioskAnimation:(PBSPerformKioskAnimationAction *)action reply:(void (^)(PBSPerformKioskAnimationActionResponse *response))reply;

// System Overlays & Bulletins
- (void)presentSystemOverlayWithRequest:(PBSUserPresentationRequest *)request completion:(void (^)(BOOL success))completion;
- (void)dismissSystemOverlayWithIdentifier:(NSString *)overlayID;
@end
```

### Discovered PineBoard Mach Services

- `com.apple.HeadBoard`
- `com.apple.Magellan`
- `com.apple.MobileAsset.MobileSoftwareUpdate.UpdateBrain`
- `com.apple.MobileAsset.SoftwareUpdate`
- `com.apple.MobileBluetooth.debug`
- `com.apple.NANDInfo.LogicalDeferredWrites`
- `com.apple.NANDInfo.LogicalImmediateWrites`
- `com.apple.NANDInfo.LogicalInvalidatedWrites`
- `com.apple.NANDInfo.LogicalMetadataWrites`
- `com.apple.PBAppIconCache.access`
- `com.apple.PBAppIconCache.work`
- `com.apple.PBAppInfoPolicy.access`
- `com.apple.PBLinkHandler`
- `com.apple.PBSnapshotService.imageProcessing`
- `com.apple.PBSystemService.XPCListener`
- `com.apple.PineBoard`
- `com.apple.PineBoard.AVSystemControllerCache`
- `com.apple.PineBoard.Asleep`
- `com.apple.PineBoard.Awake`
- `com.apple.PineBoard.BBDataProvider`
- `com.apple.PineBoard.BluetoothObserver`
- `com.apple.PineBoard.DataReportingService`
- `com.apple.PineBoard.DidReceivePeripheralPairingRequest`
- `com.apple.PineBoard.MediaRemote.MetadataUpdate`
- `com.apple.PineBoard.NANDReporting`
- `com.apple.PineBoard.PBAVSystemControllerCache.CacheDataAccessQueue`
- `com.apple.PineBoard.PBAVSystemControllerCache.DataProviderQueue`
- `com.apple.PineBoard.PBAppInfoController`
- `com.apple.PineBoard.PBAppInfoService`
- `com.apple.PineBoard.PBAppInfoStateDataSource.BBObserver`

---

## 3. HeadBoard Top Shelf Protocol (`com.apple.HeadBoard.topShelf`)

- **Host Shell**: `HeadBoard.app/HeadBoard` (tvOS Home Screen Grid)
- **Extension Service**: `com.apple.HeadBoard.topShelf`
- **Architecture**: When an application resides in the tvOS Dock (top row of Home Screen), `HeadBoard` invokes the application's `TVTopShelfExtension` out-of-process via XPC to populate dynamic carousel or sectioned banners.

### Formal Contract: `TVTopShelfProvider`

```objc
@protocol TVTopShelfProvider <NSObject>
@property (nonatomic, readonly) id<TVTopShelfContent> topShelfContent;
- (void)loadTopShelfContentWithCompletionHandler:(void (^)(id<TVTopShelfContent> content))completion;
@end

// Supported Content Models Discovered in HeadBoard:
// 1. TVTopShelfSectionedContent (HBTopShelfSectionedModel) -> Grid of titled sections with image cards
// 2. TVTopShelfInsetCarouselContent (HBTopShelfBannerModel) -> Full-width or inset hero carousel
// 3. TVTopShelfItem -> Interactive item with primaryAction, secondaryAction, rottenTomatoesRating
```

### HeadBoard IPC Endpoints & Services

- `com.apple.Arcade`
- `com.apple.HeadBoard`
- `com.apple.HeadBoard.AppMayUninstall`
- `com.apple.HeadBoard.CloudServices`
- `com.apple.HeadBoard.HBCloudSyncAppDownloadUninstallService.error`
- `com.apple.HeadBoard.HBCloudSyncDatabaseFacade`
- `com.apple.HeadBoard.HBCloudSyncDatabaseServices`
- `com.apple.HeadBoard.HBCloudSyncManager`
- `com.apple.HeadBoard.HBFolderIconVendor`
- `com.apple.HeadBoard.HBIconCache`
- `com.apple.HeadBoard.HBIconCache.preheat`
- `com.apple.HeadBoard.LaunchManager`
- `com.apple.HeadBoard.PPT`
- `com.apple.HeadBoard.analytics`
- `com.apple.HeadBoard.analytics.appGridProperties`
- `com.apple.HeadBoard.appInfo`
- `com.apple.HeadBoard.appOrder`
- `com.apple.HeadBoard.applaunch`
- `com.apple.HeadBoard.aps`
- `com.apple.HeadBoard.editing`
- `com.apple.HeadBoard.icons`
- `com.apple.HeadBoard.topshelf`
- `com.apple.TVAppStore`
- `com.apple.TVHomeSharing`
- `com.apple.TVMovies`
- `com.apple.TVMusic`
- `com.apple.TVPhotos`
- `com.apple.TVSettings`
- `com.apple.TVShows`
- `com.apple.TVWatchList`
- `com.apple.appletv.backgroundstate`
- `com.apple.appletv.mainmenu.appgrid.editfavoriteapps`
- `com.apple.appletv.mainmenu.appgrid.longpress`
- `com.apple.appletv.mainmenu.appgrid.openfolder`
- `com.apple.appletv.mainmenu.appgrid.playpausepress`
- `com.apple.appletv.mainmenu.event.arrowpress`
- `com.apple.appletv.mainmenu.topshelf.selectitem`
- `com.apple.appletv.mainmenu.topshelf.swipeup`
- `com.apple.appletv.topshelf.editapps`
- `com.apple.atx`
- `com.apple.iTunesStore.downloadInfo`
- `com.apple.icloud-container.com.apple.HeadBoard`
- `com.apple.podcasts`

---

## 4. TVPeripheralAgent Remote Pairing & Device Endpoints

- **Daemon**: `TVPeripheralAgent.app/TVPeripheralAgent`
- **Service Scope**: Bluetooth Low Energy (BTLE) proximity discovery, Siri Remote pairing, Game Controller pairing, and battery status reporting.

### Pairing & Lifecycle IPC Endpoints

| Service Endpoint | Purpose | Direction / Event |
|---|---|---|
| `com.apple.PineBoard.DidReceivePeripheralPairingRequest` | PineBoard notifies Peripheral Agent of incoming pairing gesture | Incoming to Agent |
| `com.apple.TVPeripheralAgent.DidStartProximityPairing` | Remote brought within proximity (< 10cm) initiates fast pairing | Darwin Notification |
| `com.apple.TVPeripheralAgent.DidStopProximityPairing` | Proximity pairing session timeout or cancellation | Darwin Notification |
| `com.apple.TVPeripheralAgent.addAppleTVRemote` | Siri Remote paired and bound to system HID bus | Method Trigger |
| `com.apple.TVPeripheralAgent.dropAppleTVRemote` | Siri Remote unlinked or battery disconnected | Method Trigger |
| `com.apple.TVPeripheralAgent.addGameController` | MFi / Xbox / PlayStation Bluetooth controller paired | Method Trigger |
| `com.apple.TVPeripheralAgent.dropGameController` | Game controller unlinked | Method Trigger |
| `com.apple.TVPeripheralAgent.addKeyboard` | Bluetooth keyboard connected | Method Trigger |
| `com.apple.TVPeripheralAgent.addAudio` | AirPods or Bluetooth headphones connected | Method Trigger |
| `com.apple.TVPeripheralAgent.showPanels` | Requests PineBoard to render pairing HUD overlay | HUD Trigger |

---

## 5. TVSystemMenuService Control Center IPC Architecture

- **Host Service**: `TVSystemMenuService.app/TVSystemMenuService`
- **Presentation Protocol**: `PBSViewServicePresenter`
- **Manager**: `TVSMSystemMenuManager` (`sharedInstance`)
- **Activation Mechanism**: Long-press TV/Home button on Siri Remote triggers PineBoard overlay session, launching `TVSystemMenuService` as an out-of-process view service overlaid on the right edge of the screen.

### Control Center Module Endpoints

| Module Identifier | Module Name | Architectural Function |
|---|---|---|
| `com.apple.TVSystemMenu.People-Picker-Module` | User Profile Switcher | Fast multi-user account switching and Game Center profiles |
| `com.apple.TVSystemMenu.Sleep-Module` | System Sleep Control | Puts Apple TV into low-power standby mode |
| `com.apple.TVSystemMenu.Now-Playing-Module` | Now Playing Transport | Mini-player widget displaying track artwork and scrub controls |
| `com.apple.TVSystemMenu.Audio-Routing-Module` | AirPlay 2 Audio Output | Dynamic selection of HomePods, AirPods, and HDMI eARC speakers |
| `com.apple.TVSystemMenu.Mute-Module` | Audio Mute | Immediate global audio mute toggle |
| `com.apple.TVSystemMenu.Search-Module` | Global Search | Instant activation of TVSearch and Siri dictation |
| `com.apple.TVSystemMenu.Tracking-Module` | Do Not Track & Privacy | Privacy controls for cross-app tracking |

---

## 6. Distributed & Darwin Notification Bus

### Discovered System State Notifications

| Notification Name | Broadcaster | Listener(s) | Architectural Semantics |
|---|---|---|---|
| `com.apple.PineBoard.Awake` | PineBoard | All Daemons | System transitioned from standby to active display output |
| `com.apple.PineBoard.Asleep` | PineBoard | All Daemons | System entered standby mode; video signal terminated |
| `PBSDisplayStateChangedModification` | PineBoard | HeadBoard, TVMusic | HDMI resolution, refresh rate, or HDR format altered |
| `BluetoothAvailabilityChangedNotification` | BluetoothManager | PeripheralAgent | Bluetooth radio power state toggled |
| `com.apple.HeadBoard.AppMayUninstall` | HeadBoard | PineBoard | User initiated app deletion from home screen |
| `TVCollectionViewDidScrollNotification` | TVMusic, HeadBoard | TopShelf | Focus engine scroll position updated |

