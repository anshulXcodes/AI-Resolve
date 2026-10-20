import asyncio
from playwright.async_api import async_playwright

async def capture_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        # 1. Landing Page
        print("Capturing Landing Page...")
        await page.goto("http://127.0.0.1:3000/")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="screenshots/01_landing_hero.png", full_page=True)
        
        # 2. Submit Page
        print("Capturing Submit Page...")
        await page.click("text=Submit Issue")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/02_submit_portal.png")
        
        # Click on Case 2 preset to fill and show preview
        print("Submitting Case 2 preset...")
        await page.click("text=Slide 4 Case 2")
        await page.wait_for_timeout(500)
        await page.click("button:has-text('Process & Route Complaint')")
        await page.wait_for_timeout(2500)
        await page.screenshot(path="screenshots/03_case2_duplicate_detected.png")
        
        # 3. Dashboard Page
        print("Capturing Admin Dashboard...")
        await page.click("text=Admin Triage")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/04_admin_dashboard.png")
        
        # Click on Review button
        review_btn = page.locator("button:has-text('Review')").first
        if await review_btn.count() > 0:
            await review_btn.click()
            await page.wait_for_timeout(800)
            await page.screenshot(path="screenshots/05_human_review_modal.png")
            # Close modal
            await page.click("text=✕")
            await page.wait_for_timeout(500)
            
        # 4. Workflow View
        print("Capturing n8n Workflow...")
        await page.click("text=n8n Workflow")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/06_n8n_workflow_graph.png")
        
        # 5. Benchmark View
        print("Capturing Benchmark & Ablation...")
        await page.click("text=Benchmark & USP")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshots/07_empirical_benchmark.png")
        
        await browser.close()
        print("All screenshots captured successfully in screenshots/ directory!")

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
