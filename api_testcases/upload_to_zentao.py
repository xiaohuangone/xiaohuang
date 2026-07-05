"""登录禅道，尝试导入测试用例（已发现权限问题）"""
import asyncio
import os

from playwright.async_api import async_playwright

BASE_URL = "https://sub2.hermes.cn.mt/zentao"
EXCEL_PATH = r"E:\AI\LearningSpace\web-wenrui\api_testcases\ProjectKu_API_TestCases.xlsx"
OUTPUT_DIR = r"E:\AI\LearningSpace\web-wenrui\api_testcases\reports\screenshots"


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = await context.new_page()

        # 登录
        print("[PW] 登录禅道...")
        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector("#account", timeout=30000)
        await page.fill("#account", "qa_girl_02")
        await page.fill("#password", "bndBiGCEn9oEZA4k8XAa1!")
        await page.click("#submit")
        await page.wait_for_url("**/zentao/**", timeout=30000)
        await page.wait_for_timeout(3000)
        print("[PW] 登录成功")

        # 进入用例浏览页
        print("\n[PW] 进入用例浏览页...")
        await page.goto(f"{BASE_URL}/index.php?m=testcase&f=browse&productID=1", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)

        # 获取 iframe
        print("\n[PW] 查找 iframe...")
        iframe = await page.query_selector('iframe#iframe, iframe#appIframe-qa, iframe')
        if iframe:
            iframe_frame = await iframe.content_frame()
            if iframe_frame:
                print("[PW] 获取到 iframe frame")

                # 滚动到底部并点击导入
                print("\n[PW] 滚动到底部并点击'导入'...")
                await iframe_frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await iframe_frame.wait_for_timeout(2000)

                # 用 JS 点击
                await iframe_frame.evaluate("""() => {
                    const spans = Array.from(document.querySelectorAll('span.text'));
                    const span = spans.find(s => s.textContent.trim() === '导入');
                    if (span) {
                        const btn = span.closest('button');
                        if (btn) {
                            btn.click();
                            return 'clicked';
                        }
                    }
                    return 'not found';
                }""")

                # 等待响应
                await iframe_frame.wait_for_timeout(8000)

                # 检查模态框内容
                modals = await iframe_frame.query_selector_all('.modal')
                for modal in modals:
                    cls = await modal.get_attribute('class')
                    visible = await modal.is_visible()
                    if visible:
                        text = await modal.inner_text()
                        print(f"\n[PW] 模态框内容 (class={cls}):")
                        print(text)

                # 检查是否有文件上传框
                file_inputs = await iframe_frame.query_selector_all('input[type="file"]')
                print(f"\n[PW] 文件上传框数量: {len(file_inputs)}")

                # 当前 URL
                print(f"[PW] 当前 URL: {page.url}")

        # 保存登录态
        state_path = r"E:\AI\LearningSpace\web-wenrui\api_testcases\zentao_auth.json"
        await context.storage_state(path=state_path)

        print("\n[PW] === 完成 ===")
        await browser.close()
        print("\n[DONE]")


if __name__ == "__main__":
    asyncio.run(main())
