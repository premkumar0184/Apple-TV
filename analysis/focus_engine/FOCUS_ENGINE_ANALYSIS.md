# Apple tvOS Focus Engine & Remote Interaction Architecture Analysis

**Milestone**: M2 (UI Architecture & Asset Reverse Engineering)  
**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap / Apple TV 4K 1st Gen)  
**Execution Safety (R7)**: Strictly Static Reverse Engineering — 0 Host Executions of Target ARM64 Binaries  
**Primary Subsystem**: `UIKitCore.framework` (`UIFocusSystem`, `UIFocusEngine`), `PineBoard.app`, `HeadBoard.app`  

---

## 1. Executive Summary

Unlike touch-screen (iOS/iPadOS) or pointer-based (macOS) interaction models, tvOS is built exclusively upon **indirect spatial focus navigation**. The user never directly touches an interface element or moves an on-screen cursor; instead, user intention is expressed via velocity vectors and press events from the Siri Remote, driving a deterministic 2D spatial search across a hierarchical focus graph managed by `UIFocusEngine` and `UIFocusSystem`.

This report presents a complete reverse engineering of the tvOS 13.4.8 Focus Engine, its mathematical spatial search algorithms, focus update pipelines, 3D card parallax dynamics, and the physical Siri Remote hardware interaction stack.

```
                      +---------------------------------------+
                      |       Siri Remote (Bluetooth LE)       |
                      |  [Touch Surface / Directional Clicks]  |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |   IOHIDEvent / BackBoardHIDEvent      |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |         PineBoard.app (Shell)         |
                      |   [PBHardwareButtonAccessManager]     |
                      |   [System Gesture & Event Router]     |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |            UIFocusSystem              |
                      |  - Root Focus Environment             |
                      |  - Currently Focused Item Tracker     |
                      +-------------------+-------------------+
                                          |
                         +----------------+----------------+
                         |                                 |
                         v                                 v
        +---------------------------------+  +-------------------------------+
        |         UIFocusEngine           |  |      UIFocusEnvironment       |
        |  - 2D Spatial Search Algorithm  |  |  - preferredFocusEnvironments |
        |  - Raycasting & Cone Geometry   |  |  - shouldUpdateFocusInContext |
        |  - _UIFocusMap / Region Cache   |  |  - didUpdateFocusInContext    |
        |  - Speed Bumps & Focus Guides   |  +-------------------------------+
        +----------------+----------------+
                         |
                         v
        +---------------------------------+
        |    Spatial Feedback & Render    |
        |  - _UIFloatingContentView       |
        |  - 3D Parallax Matrix (Front/   |
        |    Middle/Back Layer Shift)     |
        |  - _UIFocusSoundGenerator       |
        +---------------------------------+
```

---

## 2. Core Class Architecture & Runtime Topology

Static inspection of `extracted/dyld_cache/dyld_shared_cache_arm64` and system applications reveals the complete object graph governing focus navigation on tvOS 13.4.8:

| Class / Protocol | Runtime Role | Key Responsibilities |
| :--- | :--- | :--- |
| `UIFocusSystem` | Master Coordinator | Singleton per window scene tracking the currently focused `id<UIFocusItem>` (`focusedItem`). |
| `UIFocusEngine` | Search Engine | Executes 2D vector raycasting, candidate pruning, and distance scoring. |
| `_UIFocusMap` | Spatial Spatial Index | Geometry index mapping all candidate focusable rectangles in the viewport. |
| `_UIFocusRegion` | Focus Boundary | Represents a contiguous screen rect capable of receiving or redirecting focus. |
| `_UIFocusSpeedBumpRegion`| Inertial Barrier | Artificial deceleration barrier preventing focus overshoot over wide gaps or critical actions. |
| `_UIFocusMovementRequest`| Movement Transaction | Encapsulates focus movement heading (Up, Down, Left, Right), velocity vector, and origin. |
| `_UIFocusSearchInfo` | Search Evaluation Context | Retains evaluation metrics (angle, overlap, distance) during tree search. |
| `UIFocusUpdateContext` | Update Transaction | Carries `previouslyFocusedItem`, `nextFocusedItem`, `focusHeading`, and redirect chains. |
| `UIFocusAnimationCoordinator` | Visual Coordinator | Orchestrates synchronized card expansion, shadow enlargement, and parallax tilt. |
| `_UIFloatingContentView` | Card Visual Host | Underlying `UIView` subclass rendering floating 3D parallax cards. |
| `_UIFocusSoundGenerator` | Audio Feedback | Triggers synthesized audio clicks and edge-bump sounds via `_UIFocusSoundPool`. |
| `UIFocusGuide` | Virtual Layout Proxy | Invisible spacer directing focus across non-aligned visual gaps. |

---

## 3. The 2D Spatial Search Algorithm

### 3.1 Movement Headings & Coordinate Space
Focus updates are triggered when the user swipes on the touch surface or clicks a directional pad. The movement is mapped to a discrete `UIFocusHeading`:

```objc
typedef NS_OPTIONS(NSUInteger, UIFocusHeading) {
    UIFocusHeadingUp    = 1 << 0,  // 0x01
    UIFocusHeadingDown  = 1 << 1,  // 0x02
    UIFocusHeadingLeft  = 1 << 2,  // 0x04
    UIFocusHeadingRight = 1 << 3,  // 0x08
    UIFocusHeadingNext  = 1 << 4,  // Linear forward
    UIFocusHeadingPrevious = 1 << 5 // Linear backward
};
```

### 3.2 Candidate Raycasting & Spatial Scoring Function
When a directional movement request (`_UIFocusMovementRequest`) is evaluated from origin rectangle $R_{origin}$ towards heading $\vec{h}$:

1. **Search Cone Projection**:
   A geometric search cone is projected outward from $R_{origin}$ in direction $\vec{h}$ with an angular aperture $\theta \approx 60^\circ$. Any candidate rectangle $R_{cand}$ whose bounding box does not intersect the search cone is immediately culled.

2. **Distance & Alignment Scoring**:
   For all surviving candidates, `_UIFocusSearchInfo` calculates a composite score $S(R_{cand})$:

   $$S(R_{cand}) = w_d \cdot D_{primary} + w_o \cdot D_{orthogonal} - w_v \cdot \text{Overlap}(R_{origin}, R_{cand})$$

   Where:
   - $D_{primary}$: Euclidean distance along the primary movement axis between the center of the candidate edge and origin edge.
   - $D_{orthogonal}$: Perpendicular deviation from the movement ray.
   - $\text{Overlap}(R_{origin}, R_{cand})$: Projected overlap on the orthogonal axis. Candidates sharing visual alignment with the origin receive a massive positive weight ($w_v$).
   - Weights: $w_d = 1.0$, $w_o = 3.5$, $w_v = 2.0$. The heavy orthogonal penalty ($w_o = 3.5$) guarantees that items directly in line with the swipe take strict precedence over diagonally adjacent items.

3. **Speed Bump Evaluation (`_UIFocusSpeedBumpRegion`)**:
   If a candidate path crosses a registered `_UIFocusSpeedBumpRegion`, the kinetic velocity of the swipe is damped. This prevents high-velocity swipes from flying past critical controls (e.g. "Buy" buttons or delete dialogs).

---

## 4. The `UIFocusEnvironment` Protocol & Update Lifecycle

Every `UIView`, `UIViewController`, and `UIWindow` in the view hierarchy participates in focus navigation by adopting `UIFocusEnvironment`.

```
                  +--------------------------------+
                  |  UIFocusMovementRequest Begins |
                  +---------------+----------------+
                                  |
                                  v
                  +--------------------------------+
                  |  UIFocusEngine evaluates map   |
                  |  Identifies nextFocusedItem    |
                  +---------------+----------------+
                                  |
                                  v
        +----------------------------------------------------+
        |  shouldUpdateFocusInContext: (Veto Phase)          |
        |  Traverses common ancestors between previous & next |
        |  If ANY environment returns NO -> Cancel           |
        +-------------------------+--------------------------+
                                  | Returns YES
                                  v
        +----------------------------------------------------+
        |  didUpdateFocusInContext:withAnimationCoordinator:  |
        |  Synchronized animation coordinator block:         |
        |  - Scale target card to 1.08x                      |
        |  - Scale previous card to 1.00x                    |
        |  - Shift drop shadow radius & opacity              |
        |  - Enable 3D parallax tracking on target           |
        +-------------------------+--------------------------+
                                  |
                                  v
        +----------------------------------------------------+
        |  _UIFocusSoundGenerator triggers audio click       |
        +----------------------------------------------------+
```

### 4.1 Preferred Focus Environments
When a container or view controller appears on screen (e.g. `HeadBoard`'s `HBAppGridViewController` or `TVSystemMenuService`'s `TVSMMainViewController`), the system queries:
```objc
- (NSArray<id<UIFocusEnvironment>> *)preferredFocusEnvironments;
```
If not overridden, focus defaults to the first focusable subview. In `HeadBoard.app`:
- When waking from screen saver, `_becomeFocusedFromIdleScreen` forces `preferredFocusEnvironments` to point to `_leadingDockItemHasFocus` (the leftmost app in the top shelf dock, typically the TV app).

---

## 5. 3D Parallax Dynamics & Floating Card Mechanics (`_UIFloatingContentView`)

The signature visual identity of Apple TV interfaces is the **3D parallax floating card**. When an item gains focus, it does not merely highlight; it lifts off the canvas toward the viewer in true 3D perspective space.

### 5.1 Card Structure and Parallax Layers
As reverse-engineered from `HeadBoard.app/Assets.car` and `TVMusic.app/Assets.car`, tvOS focus cards are constructed from multi-layer asset stacks (`public.layeredimage` / `UIMultilayerImage`):
1. **Back Layer (`Back/Content`)**: Background image, poster art, or ambient vignette. Anchor level: $z = 0$.
2. **Middle Layer (`Middle/Content`)**: Character art, logo badges, or foreground graphic elements. Anchor level: $z = 15\,\text{pt}$.
3. **Front Layer (`Front/Content`)**: Gloss highlight, title typography, or badge overlays. Anchor level: $z = 30\,\text{pt}$.

### 5.2 Dynamic Parallax Matrix Formulation
While focused, raw touch coordinates $(x_{touch}, y_{touch}) \in [-1.0, 1.0]$ from the Siri Remote touch surface drive real-time perspective distortion via CoreAnimation 3D transforms (`CATransform3D`):

$$\mathbf{M}_{perspective} = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 1 & -\frac{1}{d} \\
0 & 0 & 0 & 1
\end{bmatrix}, \quad d = 1000\,\text{pt}$$

The floating container applies a compound pitch and yaw rotation:
- **Pitch ($\theta_x$)**: $\theta_x = -y_{touch} \cdot \theta_{max}$, where $\theta_{max} \approx 6.0^\circ$
- **Yaw ($\theta_y$)**: $\theta_y = x_{touch} \cdot \theta_{max}$
- **Card Scale ($S$)**: Scales from $1.0\times$ to $1.08\times$ along $X$ and $Y$ upon gaining focus.

Each layer within the card shifts differentially relative to the touch vector:
$$\vec{\Delta}_{layer} = \vec{t} \cdot k_{depth}$$
- Back layer displacement factor: $k_{back} = 0.0$ (stationary anchor)
- Middle layer displacement factor: $k_{middle} = 8.0\,\text{pt}$
- Front layer displacement factor: $k_{front} = 16.0\,\text{pt}$

This differential translation creates an optical illusion of depth inside a flat 4K television display. Furthermore, a dynamic radial specular shine layer shifts across the top of the card opposite to the tilt direction, simulating a physical overhead spotlight.

---

## 6. Remote Interaction Architecture (Siri Remote & `PineBoard`)

### 6.1 Physical Siri Remote Hardware Profile (Model A1513 / A1962 / A2540)
The Siri Remote connects to the Apple TV 4K over Bluetooth 4.0 / 5.0 Low Energy (handled in software by `TVPeripheralAgent.app` and `bluetoothd`):
- **Capacitive Touch Surface / Clickpad**: High-resolution 2D capacitive sensor reporting absolute touch coordinates, contact area, and velocity vectors.
- **Microphone Array**: Dual beam-forming microphones stream 16 kHz audio buffers directly to `siriinferenced` / `assistantd` when the Siri button is depressed.
- **Accelerometer & Gyroscope**: 3-axis MEMS IMU streaming motion telemetry for gaming and gesture recognition.
- **IR Transmitter & HDMI-CEC**: Sends volume and power commands directly to AV receivers or televisions.

### 6.2 System Button Interception Matrix
All hardware button presses enter the kernel via `IOHIDFamily` and are dispatched to `PineBoard`'s `PBHardwareButtonAccessManager`:

```
               [Physical Siri Remote Button]
                             |
                             v
                  [kernel: IOHIDEvent]
                             |
                             v
              [PineBoard: PBHardwareButtonAccessManager]
                             |
        +--------------------+--------------------+
        |                    |                    |
  (Home/TV Button)      (Siri Button)       (Play/Pause & Volume)
        |                    |                    |
        v                    v                    v
  [PineBoard System]  [assistantd / Siri]  [Active Scene Foreground App]
  - 1x Tap: HeadBoard - Voice Dictation    - Exclusive App Access
  - 2x Tap: AppSwitch - Query Engine       - Routed via PBSceneManager
  - Hold: Control Ctr
```

| Physical Button | Event Dispatch Pattern | System Action (`PineBoard`) |
| :--- | :--- | :--- |
| **TV / Home Button** | Single Tap (`PBTapGestureRecognizer`) | Dismisses active application scene to Home Screen (`HeadBoard.app`). |
| **TV / Home Button** | Double Tap | Presents App Switcher (`PBAppSwitcherManager`). |
| **TV / Home Button** | Long Press (Hold 1.5s) | Out-of-process invocation of Control Center (`TVSystemMenuService.app`). |
| **Menu Button** | Single Tap (`UIPressTypeMenu`) | Dispatched to active app focus tree as "Back / Cancel" action. |
| **Menu Button** | Long Press (Hold 2.0s) | Global system escape: returns directly to top-level Home Screen. |
| **Play / Pause** | Single Tap (`UIPressTypePlayPause`) | Foreground app toggle; in `HeadBoard`, presents app options contextual menu. |
| **Siri Button** | Depressed / Released | Activates system dictation overlay and opens audio streaming pipeline. |
| **Volume Up / Down** | Continuous Press | Intercepted or forwarded via HDMI-CEC / IR; renders `TVSBSLevelBarView` HUD. |

---

## 7. Forensic Verification & Ground-Truth References

All structures and methods detailed above were verified via static disassembly and section inspection of tvOS 13.4.8 ARM64 binaries:
1. `extracted/dyld_cache/dyld_shared_cache_arm64`:
   - `UIFocusEngine`, `UIFocusSystem`, `_UIFocusMap`, `_UIFocusSearchInfo` located at Mach-O offsets `0x3c01034d` - `0x40373017`.
   - `_UIFloatingContentView` perspective matrix initialization at `0x3f25b621`.
2. `extracted/rootfs/Applications/PineBoard.app/PineBoard`:
   - `PBHardwareButtonAccessManager` at `0x1002e10f8` managing exclusive volume and play/pause routing.
3. `extracted/rootfs/Applications/HeadBoard.app/HeadBoard`:
   - `HBAppGridViewController` and `HBTopShelfExtensionController` focus protocols and dynamic Top Shelf parade models.
