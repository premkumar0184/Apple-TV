import os
import unittest
import struct
from PIL import Image

class TestIPSW_M3_UI(unittest.TestCase):
    """Integrity and comparative evolution test suite for Milestone IPSW-M3."""

    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    ERASE_DIR = os.path.join(PROJECT_ROOT, "extracted/ipsw/ramdisk_erase")
    UPDATE_DIR = os.path.join(PROJECT_ROOT, "extracted/ipsw/ramdisk_update")
    FIRMWARE_DIR = os.path.join(PROJECT_ROOT, "extracted/ipsw/firmware")
    REPORT_PATH = os.path.join(PROJECT_ROOT, "analysis/ipsw/UI_EVOLUTION_REPORT.md")

    def test_01_report_existence_and_sections(self):
        """Verify UI_EVOLUTION_REPORT.md exists, is non-empty, and contains all required sections."""
        self.assertTrue(os.path.exists(self.REPORT_PATH), f"Missing report: {self.REPORT_PATH}")
        with open(self.REPORT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertGreater(len(content), 4000, "Report is too short")
        required_headers = [
            "Executive Summary",
            "Recoverable UI Graphic Assets",
            "Plist & Localization Footprint",
            "Comprehensive Comparative Evolution",
            "Architectural Deep Dive: New System Applications",
            "Synthesis & Downstream Integration",
        ]
        for header in required_headers:
            self.assertIn(header, content, f"Report missing section header: {header}")

    def test_02_progressui_1080p_assets(self):
        """Verify 1080p ProgressUI assets exist, are non-empty, and have authentic dimensions."""
        dir_1080 = os.path.join(self.ERASE_DIR, "usr/share/progressui/images-AppleTV-1080")
        self.assertTrue(os.path.isdir(dir_1080))
        logo_path = os.path.join(dir_1080, "applelogo.tga")
        self.assertTrue(os.path.exists(logo_path))
        with Image.open(logo_path) as im:
            self.assertEqual(im.size, (225, 365))
            self.assertEqual(im.format, "TGA")

        required_assets = [
            "emptyfill.tga", "solidfill.tga",
            "leftcap1.tga", "rightcap1.tga",
            "leftfillcap1.tga", "rightfillcap1.tga",
        ]
        for asset in required_assets:
            p = os.path.join(dir_1080, asset)
            self.assertTrue(os.path.exists(p), f"Missing 1080p asset: {asset}")
            self.assertGreater(os.path.getsize(p), 0)

    def test_03_progressui_4k_assets(self):
        """Verify 4K UHD ProgressUI assets exist and have exact 2x dimensions of 1080p."""
        dir_2160 = os.path.join(self.ERASE_DIR, "usr/share/progressui/images-AppleTV-2160")
        self.assertTrue(os.path.isdir(dir_2160))
        logo_path = os.path.join(dir_2160, "applelogo.tga")
        self.assertTrue(os.path.exists(logo_path))
        with Image.open(logo_path) as im:
            self.assertEqual(im.size, (450, 730))
            self.assertEqual(im.format, "TGA")

        fill_path = os.path.join(dir_2160, "emptyfill.tga")
        self.assertTrue(os.path.exists(fill_path))
        with Image.open(fill_path) as im:
            self.assertEqual(im.size, (20, 104))

    def test_04_vector_screen_prompts(self):
        """Verify high-resolution vector screen prompts exist and have authentic dimensions."""
        pui_dir = os.path.join(self.ERASE_DIR, "usr/share/progressui")
        disconnect_prompt = os.path.join(pui_dir, "disconnect-prompt.tga")
        power_prompt = os.path.join(pui_dir, "power-button-prompt.tga")
        self.assertTrue(os.path.exists(disconnect_prompt))
        self.assertTrue(os.path.exists(power_prompt))

        with Image.open(disconnect_prompt) as im:
            self.assertEqual(im.size, (1536, 2048))
        with Image.open(power_prompt) as im:
            self.assertEqual(im.size, (1536, 2048))

    def test_05_companion_hardware_assets(self):
        """Verify the Apple Vision Pro Developer Strap graphic asset in CoreAccessories."""
        strap_path_update = os.path.join(
            self.UPDATE_DIR,
            "System/Library/PrivateFrameworks/CoreAccessories.framework/vision.pro.developer.strap-N301a.png"
        )
        self.assertTrue(os.path.exists(strap_path_update))
        with Image.open(strap_path_update) as im:
            self.assertEqual(im.size, (1024, 1024))
            self.assertEqual(im.format, "PNG")

    def test_06_bootloader_decoded_images(self):
        """Verify decoded early boot images in extracted/ipsw/firmware/."""
        logo_png = os.path.join(self.FIRMWARE_DIR, "applelogo.png")
        recovery_png = os.path.join(self.FIRMWARE_DIR, "recoverymode.png")
        self.assertTrue(os.path.exists(logo_png))
        self.assertTrue(os.path.exists(recovery_png))

        with Image.open(logo_png) as im:
            self.assertEqual(im.size, (108, 131))
        with Image.open(recovery_png) as im:
            self.assertEqual(im.size, (582, 154))

    def test_07_plists_and_locales_count(self):
        """Verify plist and localization bundle counts in the restore ramdisk."""
        plists = []
        locales = set()
        for root, dirs, files in os.walk(self.ERASE_DIR):
            for f in files:
                if f.endswith(".plist"):
                    plists.append(f)
            for d in dirs:
                if d.endswith(".lproj"):
                    locales.add(d[:-6])
        self.assertGreaterEqual(len(plists), 110)
        self.assertGreaterEqual(len(locales), 38)

    def test_08_frameworks_count_and_swift_infrastructure(self):
        """Verify framework count and modern Swift infrastructure in the ramdisk."""
        frameworks = set()
        for root, dirs, files in os.walk(self.ERASE_DIR):
            for d in dirs:
                if d.endswith(".framework"):
                    frameworks.add(d)
        self.assertGreaterEqual(len(frameworks), 70)
        required_swift_fw = ["Combine.framework", "CryptoKit.framework", "AlgorithmsInternal.framework"]
        for fw in required_swift_fw:
            self.assertIn(fw, frameworks, f"Missing expected Swift framework: {fw}")

if __name__ == "__main__":
    unittest.main()
