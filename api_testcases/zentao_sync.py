"""
禅道同步脚本：将 pytest + Allure 测试结果同步到禅道
功能：
  1. 创建测试任务
  2. 更新测试用例执行结果（通过更新 lastRunResult 字段）
  3. 自动创建 Bug（失败用例）
"""
import asyncio
import json
import os
import re
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright

BASE_URL = "https://sub2.hermes.cn.mt/zentao"
ALLURE_RESULTS_DIR = Path(__file__).parent / "reports" / "allure_results"


class ZentaoSync:
    def __init__(self):
        self.token = None
        self.headers = None
        self.product_id = 1
        self.task_id = None
        # 禅道项目配置
        self.project_id = 2
        self.execution_id = 3
        self.build_id = 1

    async def init(self):
        """登录并获取 token"""
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

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
        self.headers = {"Token": token, "Content-Type": "application/json"}
        self.pw = pw
        self.browser = browser
        self.page = page
        print(f"[Zentao] 登录成功，token: {token[:20]}...")

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.pw:
            await self.pw.stop()

    def parse_allure_results(self):
        """解析 Allure 结果文件"""
        results = []
        if not ALLURE_RESULTS_DIR.exists():
            print(f"[Zentao] Allure 结果目录不存在: {ALLURE_RESULTS_DIR}")
            return results

        for result_file in ALLURE_RESULTS_DIR.glob("*-result.json"):
            try:
                with open(result_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append(data)
            except Exception as e:
                print(f"[Zentao] 解析失败 {result_file.name}: {e}")

        print(f"[Zentao] 解析到 {len(results)} 条测试结果")
        return results

    def extract_test_info(self, allure_result):
        """从 Allure 结果中提取测试信息"""
        name = allure_result.get("name", "")
        status = allure_result.get("status", "unknown")

        # 提取标签
        labels = {label["name"]: label["value"] for label in allure_result.get("labels", [])}
        priority = labels.get("tag", "P2")

        return {
            "name": name,
            "status": status,
            "priority": priority,
        }

    async def create_testtask(self, name, testcase_ids):
        """创建测试任务"""
        print(f"\n[Zentao] 创建测试任务: {name}")
        print(f"[Zentao] 包含用例数: {len(testcase_ids)}")

        task_data = {
            "product": self.product_id,
            "execution": self.execution_id,
            "build": self.build_id,
            "name": f"API自动化测试-{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "begin": datetime.now().strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d"),
            "owner": "qa_girl_02",
            "type": "acceptance",
            "pri": 1,
            "status": "wait",
            "desc": "API创建测试任务",
            "testcases": testcase_ids,
        }

        # 使用正确的 API 路径
        resp = await self.page.request.post(
            f"{BASE_URL}/api.php/v1/projects/{self.project_id}/testtasks",
            headers=self.headers,
            data=json.dumps(task_data, ensure_ascii=False)
        )

        print(f"[Zentao] 创建测试任务状态: {resp.status}")
        resp_text = await resp.text()
        print(f"[Zentao] 响应: {resp_text[:300]}")

        if resp.status in [200, 201]:
            try:
                result = await resp.json()
                self.task_id = result.get("id")
                print(f"[Zentao] 测试任务ID: {self.task_id}")
                return self.task_id
            except Exception as e:
                print(f"[Zentao] 解析任务响应失败: {e}")

        return None

    async def update_test_result(self, case_id, result):
        """更新单个测试用例的执行结果（通过更新 lastRunResult 字段）"""
        status_map = {
            "passed": "pass",
            "failed": "fail",
            "broken": "fail",
            "skipped": "blocked"
        }
        zentao_status = status_map.get(result["status"], "blocked")

        # 直接更新用例的 lastRunResult 字段
        update_data = {
            "lastRunResult": zentao_status
        }

        resp = await self.page.request.put(
            f"{BASE_URL}/api.php/v1/testcases/{case_id}",
            headers=self.headers,
            data=json.dumps(update_data, ensure_ascii=False)
        )

        if resp.status == 200:
            print(f"  [{case_id}] {result['name'][:40]} -> {zentao_status}")
        else:
            resp_text = await resp.text()
            print(f"  [{case_id}] 更新失败: {resp.status} - {resp_text[:100]}")

    async def create_bug(self, case_id, result):
        """为失败的测试用例创建 Bug"""
        bug_data = {
            "product": self.product_id,
            "title": f"[自动] {result['name'][:100]}",
            "pri": 2 if result.get("priority") == "P0" else 3,
            "severity": 2,
            "type": "bug",  # 必填字段
            "status": "active",
            "steps": f"## 复现步骤\n\n{result['name']}\n\n## 预期结果\n\n测试通过\n\n## 实际结果\n\n测试失败\n\n## 测试用例ID\n{case_id}",
            "openedBy": "qa_girl_02",
        }

        resp = await self.page.request.post(
            f"{BASE_URL}/api.php/v1/bugs",
            headers=self.headers,
            data=json.dumps(bug_data, ensure_ascii=False)
        )

        if resp.status == 200:
            try:
                bug = await resp.json()
                bug_id = bug.get("id")
                print(f"  [Bug] 创建成功: {bug_id} - {result['name'][:40]}")
            except Exception:
                print(f"  [Bug] 创建响应解析失败")
        else:
            resp_text = await resp.text()
            print(f"  [Bug] 创建失败: {resp.status} - {resp_text[:100]}")

    async def sync(self):
        """主同步流程"""
        await self.init()

        try:
            # 1. 解析 Allure 结果
            results = self.parse_allure_results()
            if not results:
                print("[Zentao] 没有找到测试结果")
                return

            # 2. 提取测试信息
            test_infos = [self.extract_test_info(r) for r in results]
            passed = [t for t in test_infos if t["status"] == "passed"]
            failed = [t for t in test_infos if t["status"] == "failed"]
            broken = [t for t in test_infos if t["status"] == "broken"]
            skipped = [t for t in test_infos if t["status"] == "skipped"]

            print(f"\n[Zentao] 测试结果统计:")
            print(f"  通过: {len(passed)}")
            print(f"  失败: {len(failed)}")
            print(f"  错误: {len(broken)}")
            print(f"  跳过: {len(skipped)}")

            # 3. 创建测试任务（使用禅道已有的用例 ID 321-418）
            case_ids = list(range(321, 321 + len(test_infos)))
            task_id = await self.create_testtask("API自动化测试", case_ids)
            if not task_id:
                print("[Zentao] 创建测试任务失败，停止同步")
                return

            # 4. 更新测试结果
            print(f"\n[Zentao] 更新测试结果...")
            for i, test_info in enumerate(test_infos):
                if i < len(case_ids):
                    case_id = case_ids[i]
                    await self.update_test_result(case_id, test_info)

                    # 5. 为失败的用例创建 Bug
                    if test_info["status"] in ["failed", "broken"]:
                        await self.create_bug(case_id, test_info)

            print(f"\n[Zentao] 同步完成! 测试任务ID: {task_id}")

        finally:
            await self.close()


async def main():
    sync = ZentaoSync()
    await sync.sync()


if __name__ == "__main__":
    asyncio.run(main())
