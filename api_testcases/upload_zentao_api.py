"""通过禅道 REST API 导入测试用例"""
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = "https://sub2.hermes.cn.mt/zentao"
EXCEL_PATH = r"E:\AI\LearningSpace\web-wenrui\api_testcases\ProjectKu_API_TestCases.xlsx"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

        # 登录并获取 token
        print("[API] 登录禅道...")
        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector("#account", timeout=30000)
        await page.fill("#account", "qa_girl_02")
        await page.fill("#password", "bndBiGCEn9oEZA4k8XAa1!")
        await page.click("#submit")
        await page.wait_for_url("**/zentao/**", timeout=30000)
        await page.wait_for_timeout(3000)

        resp = await page.request.post(f"{BASE_URL}/api.php/v1/tokens", data={
            "account": "qa_girl_02",
            "password": "bndBiGCEn9oEZA4k8XAa1!"
        })
        token = (await resp.json())["token"]
        headers = {"Token": token}
        print(f"[API] Token: {token}")

        # 验证导入结果
        print("\n[API] 验证导入结果...")

        # 检查 321-418 号用例
        print("\n[API] 检查 321, 418 号用例...")
        for cid in [321, 418]:
            r = await page.request.get(f"{BASE_URL}/api.php/v1/testcases/{cid}", headers=headers)
            if r.status == 200:
                data = await r.json()
                print(f"  [{cid}] {data.get('title', 'N/A')[:60]}")
                print(f"        product={data.get('product')}, type={data.get('type')}, pri={data.get('pri')}")
                steps = data.get('steps', [])
                if steps:
                    print(f"        steps: {len(steps)} 步")
                    print(f"        第1步: {str(steps[0].get('step', ''))[:80]}")
            else:
                print(f"  [{cid}] 状态: {r.status}")

        # 检查产品下的用例总数
        print("\n[API] 检查产品 1 的用例总数...")
        # 通过浏览页统计
        await page.goto(f"{BASE_URL}/index.php?m=testcase&f=browse&productID=1", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        iframe = await page.query_selector('iframe')
        if iframe:
            iframe_frame = await iframe.content_frame()
            if iframe_frame:
                # 查找总数
                total_text = await iframe_frame.evaluate("""() => {
                    const el = document.querySelector('.pager .lighter');
                    return el ? el.textContent.trim() : '';
                }""")
                print(f"  页面显示总数: {total_text}")

                # 获取页面上的用例ID
                case_ids = await iframe_frame.evaluate("""() => {
                    return Array.from(document.querySelectorAll('td.cell-id input[type="checkbox"]'))
                        .map(cb => cb.getAttribute('data-id'))
                        .filter(id => id)
                        .slice(0, 10);
                }""")
                print(f"  页面用例IDs: {case_ids}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
