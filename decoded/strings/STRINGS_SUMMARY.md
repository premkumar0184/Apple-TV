# Apple tvOS Localization & Strings Master Summary

**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap)
**Total `.strings` files processed**: 900
**Total Applications / Bundles**: 10
**Total String Instances**: 25,490

| Application / Service | Supported Locales | Unique Keys | Total String Entries | Sample English Terms |
| :--- | :--- | :--- | :--- | :--- |
| **AppStore** | 39 locales | 37 | 1,443 | `ONBOARDING_TV_SPLASH_PICKER_ARCADE`, `OFFER_BUTTON_TITLE_BUY`, `INFO_LIST_REQUIREMENTS_SUMMARY` |
| **AppleTV** | 39 locales | 9 | 351 | `NSLocationWhenInUseUsageDescription`, `CFBundleDisplayName`, `CFBundleDisplayName#CH` |
| **HeadBoard** | 39 locales | 70 | 2,730 | `News`, `Role Playing Games`, `Strategy Games` |
| **PineBoard** | 39 locales | 136 | 5,304 | `NSLocationAlwaysUsageDescription`, `OSUpdateVersion`, `OSUpdateConfirmNotReadySubtext` |
| **PreBoard** | 39 locales | 6 | 234 | `PREConfirmationMessage`, `PREResetAllSettingsButton`, `PREDialogTitle` |
| **Setup** | 39 locales | 213 | 8,307 | `REGION_TITLE`, `CLOUD_CONFIG_AWAITING_CONFIGURATION_DESCRIPTION_%@`, `ACTIVATION_ERROR_TRY_AGAIN` |
| **TVIdleScreen** | 39 locales | 1 | 39 | `TVIDefaultAssetSubtitle` |
| **TVMusic** | 39 locales | 138 | 5,382 | `CreatePlaylistButton`, `HUDConfirmationFollowingTitle`, `HUDConfirmationPlayLaterTitle` |
| **TVPeripheralAgent** | 39 locales | 40 | 1,560 | `AccessoryHUDTitleBatteryLow`, `AccessoryHUDTitleKeyboard`, `BTLEDeviceLimitExceededTitle` |
| **CoreGlyphs** | 1 locales | 140 | 140 |  |

## UI Terminology & Architectural Insights from Localization

### 1. PineBoard (Shell Daemon)
- System alert dialogs: `OSUpdateConfirmReadyPrompt`, `OSUpdateFailedNeedToRestartSubtext`, `AppStorageFullDefaultButton`
- Privacy and Siri consent flows: `DictationPrivacyTitle`, `SiriDataSharingOptInTitle`
- Managed profiles & enterprise barriers: `AppProfileExpiredTitleWithNameFormat`

### 2. HeadBoard (Home Screen Launcher)
- App folder creation, management, and editing: `RenameFolder`, `DeleteFolder`, `JiggleMode`
- Focus and remote interaction instructions: `PressPlayPauseForOptions`

### 3. TVPeripheralAgent (Remote & Bluetooth Management)
- Siri Remote pairing wizard: `RemotePairingTitle`, `BringRemoteCloserPrompt`, `BatteryLowHUD`
- Bluetooth game controller pairing (MFi, DualShock 4, Xbox Wireless Controller): `GameControllerConnectedHUD`
