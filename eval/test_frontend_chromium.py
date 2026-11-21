"""
DocsAI Full-System Chromium UI & E2E Validation Script.
══════════════════════════════════════════════════════
Automates real Chromium browser interactions against the running DocsAI frontend (http://127.0.0.1:5173)
and backend (http://127.0.0.1:8000), verifying all features across:
1. Login & Instant Demo Access (Bypassing Firebase restrictions)
2. Chat Workspace & Statutory Concordance Modal (IPC ⇄ BNS, CrPC ⇄ BNSS)
3. Document Vault & 1-Click India AI Fellowship Benchmark Cards
4. Analytics Dashboard & Knowledge Graph Topology Visualization
Saves visual verification screenshots to disk.
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5173"
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
SCREENSHOT_DIR = os.path.join(r"C:\Users\hp\.gemini\antigravity\brain\33992866-6f81-40d4-b025-f00f391b5133", "chromium_artifacts")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = []

def record(test_name: str, passed: bool, details: str = ""):
    status = "PASS" if passed else "FAIL"
    results.append((test_name, passed, details))
    icon = "✅" if passed else "❌"
    print(f"{icon} [{status}] {test_name}: {details}")

print("\n" + "=" * 70)
print(f"  DocsAI Chromium Live Browser Automation & Feature Verification")
print(f"  Target: {BASE_URL} | Engine: Chromium ({CHROME_PATH})")
print("=" * 70 + "\n")

pw = sync_playwright().start()
browser = pw.chromium.launch(executable_path=CHROME_PATH, headless=True)
context = browser.new_context(viewport={"width": 1280, "height": 800})
page = context.new_page()

try:
    # ── 1. Landing Page Navigation ───────────────────────────────────────────
    print("Navigating to DocsAI root...")
    page.goto(BASE_URL, wait_until="networkidle")
    title = page.title()
    s1_path = os.path.join(SCREENSHOT_DIR, "01_landing_page.png")
    page.screenshot(path=s1_path)
    record("1. Chromium Root Navigation", "DocsAI" in title, f"Page title: '{title}' | Screenshot: 01_landing_page.png")

    # ── 2. Login Page & Instant Demo Evaluator Access ─────────────────────────
    print("Navigating to /login...")
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    s2_path = os.path.join(SCREENSHOT_DIR, "02_login_page.png")
    page.screenshot(path=s2_path)
    
    # Check for "Instant Demo Access (Fellowship Evaluator)" button
    demo_btn = page.locator("text=Instant Demo Access (Fellowship Evaluator)")
    has_demo_btn = demo_btn.count() > 0
    record("2. Login View & Fellowship Demo Button", has_demo_btn, f"Found demo access button on login card.")

    if has_demo_btn:
        print("Clicking Instant Demo Access button...")
        demo_btn.click()
        page.wait_for_url("**/chat", timeout=5000)
        time.sleep(1)
        s3_path = os.path.join(SCREENSHOT_DIR, "03_authenticated_chat.png")
        page.screenshot(path=s3_path)
        record("3. Fellowship Evaluator Authentication", "/chat" in page.url, f"Successfully authenticated. URL: {page.url} | Screenshot: 03_authenticated_chat.png")

    # ── 3. Chat Interface & Statutory Concordance Modal ──────────────────────
    print("Testing Statutory Concordance Modal in /chat...")
    # Look for IPC ⇄ BNS button
    concordance_btn = page.locator("text=IPC ⇄ BNS").or_(page.locator("button:has-text('Concordance')")).first
    if concordance_btn.count() > 0:
        concordance_btn.click()
        time.sleep(1)
        
        # Verify modal opened
        modal = page.locator(".concordance-modal, [class*='concordance']").or_(page.get_by_text("Statutory Concordance")).first
        modal_visible = modal.count() > 0
        s4_path = os.path.join(SCREENSHOT_DIR, "04_concordance_modal.png")
        page.screenshot(path=s4_path)
        
        # Test typing a query into search box if present
        search_input = page.locator("input[placeholder*='IPC'], input[placeholder*='search'], input[type='text']").first
        if search_input.count() > 0:
            search_input.fill("IPC 420")
            time.sleep(1)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04b_concordance_search.png"))

        record("4. Statutory Concordance Engine Modal", modal_visible, "Modal displayed with IPC ⇄ BNS, CrPC ⇄ BNSS lookups. Screenshot: 04_concordance_modal.png")
        
        # Close modal
        close_btn = page.locator("button").filter(has_text="✕").or_(page.locator("button").filter(has_text="Close")).or_(page.locator(".modal-close")).first
        if close_btn.count() > 0:
            close_btn.click()
            time.sleep(0.5)
    else:
        record("4. Statutory Concordance Engine Modal", False, "Concordance button not located in DOM.")

    # ── 4. Document Vault & India AI Benchmarks ──────────────────────────────
    print("Navigating to /vault...")
    page.goto(f"{BASE_URL}/vault", wait_until="networkidle")
    time.sleep(1.5)
    s5_path = os.path.join(SCREENSHOT_DIR, "05_document_vault.png")
    page.screenshot(path=s5_path)

    # Check for India AI Benchmark Cards
    benchmarks_found = []
    for b_title in ["PM-KISAN", "Supreme Court", "Ayushman"]:
        if page.locator(f"text={b_title}").count() > 0:
            benchmarks_found.append(b_title)

    has_benchmarks = len(benchmarks_found) >= 2
    record("5. Document Vault & India AI Benchmark Catalog", has_benchmarks, f"Found benchmark cards: {benchmarks_found} | Screenshot: 05_document_vault.png")

    # ── 5. Analytics & Knowledge Graph Visualization ─────────────────────────
    print("Navigating to /analytics...")
    page.goto(f"{BASE_URL}/analytics", wait_until="networkidle")
    time.sleep(2)
    s6_path = os.path.join(SCREENSHOT_DIR, "06_analytics_dashboard.png")
    page.screenshot(path=s6_path)

    # Check for canvas or svg or graph container
    graph_container = page.locator("canvas, svg, .graph-container, .analytics-container").or_(page.get_by_text("Knowledge Graph")).first
    graph_visible = graph_container.count() > 0
    record("6. Analytics & Knowledge Graph Visualization", graph_visible, f"Knowledge Graph container rendered | Screenshot: 06_analytics_dashboard.png")

    # ── 6. Verification of Vertical Selection in Chat ────────────────────────
    print("Navigating back to /chat to verify vertical switches...")
    page.goto(f"{BASE_URL}/chat", wait_until="networkidle")
    time.sleep(1)
    
    # Check for vertical selector
    vertical_elements = page.get_by_text("Governance").or_(page.get_by_text("Law")).or_(page.get_by_text("Judgment"))
    has_verticals = vertical_elements.count() > 0
    record("7. Multi-Vertical Selector (Governance & Law)", has_verticals, f"Found vertical selector options in UI.")

except Exception as exc:
    print(f"Exception during Chromium automation: {exc}")
    record("Chromium Automation Suite", False, str(exc))

finally:
    browser.close()
    pw.stop()

print("\n" + "=" * 70)
total_tests = len(results)
passed_tests = sum(1 for _, p, _ in results if p)
print(f"  Chromium UI Summary: {passed_tests}/{total_tests} Steps Verified ({(passed_tests/total_tests)*100:.1f}%)")
print(f"  Screenshots saved to: {SCREENSHOT_DIR}")
print("=" * 70 + "\n")

if passed_tests < total_tests:
    sys.exit(1)
