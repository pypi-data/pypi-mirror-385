#!/usr/bin/env python3
"""
Claude AI Analyzer for CloudWatch Alarms
使用 Claude API 深入分析 alarm 根本原因

此文件為向後兼容層，實際實作已移至 analyzers/claude_analyzer.py
使用集中管理的 prompt templates (config/prompts.py)
"""

# 為了向後兼容，從新的 analyzers package 導入
try:
    from analyzers.claude_analyzer import ClaudeAnalyzer as _ClaudeAnalyzer
    from analyzers.claude_analyzer import load_claude_settings as _load_claude_settings

    # 使用新的實作
    ClaudeAnalyzer = _ClaudeAnalyzer
    load_claude_settings = _load_claude_settings

except ImportError:
    # 如果新模組不可用，退回到舊的實作
    import json
    from typing import Dict, List, Optional
    from pathlib import Path
    import httpx


    class ClaudeAnalyzer:
        """使用 Claude API 分析 CloudWatch Alarms"""

        def __init__(self, settings: Dict[str, str]):
            """
            初始化 Claude Analyzer

            Args:
                settings: 從 ~/.claude/settings.json 讀取的設定
            """
            self.base_url = settings.get('ANTHROPIC_BASE_URL')
            self.auth_token = settings.get('ANTHROPIC_AUTH_TOKEN')
            self.model = settings.get('ANTHROPIC_MODEL', 'claude-4.5-sonnet')

            # 建立 HTTP client (用於 RDSEC proxy)
            self.http_client = httpx.Client(
                base_url=self.base_url,
                headers={
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                timeout=60.0
            )

    def analyze_alarm(
        self,
        alarm_details: Dict,
        logs: List[Dict],
        region: str,
        is_timeout: bool = False,
        api_gateway_context: Optional[Dict] = None
    ) -> Optional[Dict[str, str]]:
        """
        分析 alarm 並返回根本原因

        Args:
            alarm_details: Alarm 詳細資訊
            logs: 相關的錯誤日誌
            region: AWS region
            is_timeout: 是否為 timeout 錯誤
            api_gateway_context: API Gateway 錯誤上下文（如果適用）

        Returns:
            分析結果 dict，包含 root_cause, recommendation, severity
        """
        try:
            prompt = self._build_analysis_prompt(alarm_details, logs, region, is_timeout, api_gateway_context)

            # 直接使用 HTTP client 呼叫 API
            response = self.http_client.post(
                '/v1/messages',
                json={
                    'model': self.model,
                    'max_tokens': 4000,  # 增加到 4000 以容納更詳細的分析
                    'messages': [{
                        'role': 'user',
                        'content': prompt
                    }]
                }
            )

            response.raise_for_status()
            result = response.json()

            # 解析回應
            if 'content' in result and len(result['content']) > 0:
                analysis_text = result['content'][0]['text']
                return self._parse_analysis(analysis_text)
            else:
                return None

        except Exception as e:
            print(f"    AI 分析時發生錯誤: {e}")
            return None

    def _build_analysis_prompt(
        self,
        alarm_details: Dict,
        logs: List[Dict],
        region: str,
        is_timeout: bool = False,
        api_gateway_context: Optional[Dict] = None
    ) -> str:
        """建立分析 prompt"""

        # 格式化 logs - 提供完整的日誌給 AI 分析（不限制字元數）
        log_text = "\n".join([
            f"[{log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {log['message']}"  # 完整日誌內容
            for log in logs[:500]  # 最多 500 條日誌
        ])

        if not log_text:
            log_text = "(無相關日誌)"

        # API Gateway 錯誤上下文
        api_gateway_info = ""
        if api_gateway_context:
            api_gateway_info = f"""

**API Gateway 錯誤資訊:**
- Request ID: {api_gateway_context.get('request_id', 'N/A')}
- HTTP Status Code: {api_gateway_context.get('status_code', 'N/A')}
- Error Message: {api_gateway_context.get('error_message', 'N/A')}
- 觸發時間: {api_gateway_context.get('timestamp', 'N/A')}
- 後端 Lambda: {api_gateway_context.get('lambda_function', 'N/A')}

**特別注意 (API Gateway + Lambda 分析):**
這是一個 API Gateway 5XX 錯誤，已經追蹤到後端 Lambda function 的執行日誌。
請綜合分析：
1. Lambda 執行過程中發生了什麼錯誤？
2. 為什麼 Lambda 返回了 5XX status code？
3. 是程式邏輯錯誤、外部服務異常，還是資源不足？
4. 從 Lambda logs 中找出具體的失敗點
"""

        # 針對 timeout 提供特殊的分析指引
        timeout_guidance = ""
        if is_timeout:
            timeout_guidance = """

**特別注意 (Timeout 分析):**
這是一個 Lambda timeout 錯誤。以下日誌包含了完整的執行過程 (從 START 到 timeout)。
請特別分析:
1. Lambda 在執行什麼操作時卡住了？(查看 timeout 前的最後幾條日誌)
2. 是否有重複的操作或迴圈？
3. 是否在等待外部服務回應？(資料庫、API、檔案 I/O 等)
4. 執行時間分布如何？哪個步驟耗時最久？

**重要**: 在 ROOT_CAUSE 中必須直接引用原始日誌內容,例如:
- 如果卡在 API 呼叫,請寫出具體的 API endpoint 或 URL
- 如果是資料庫查詢,請寫出 SQL 語句或 table 名稱
- 如果是外部服務,請寫出服務名稱和操作
- 直接從日誌中複製關鍵的錯誤訊息或操作描述
"""

        prompt = f"""你是一個 AWS CloudWatch 和分散式系統的專家。請分析以下的 CloudWatch Alarm 並找出根本原因。

**Alarm 資訊:**
- 名稱: {alarm_details.get('alarm_name', 'N/A')}
- Region: {region}
- Namespace: {alarm_details.get('namespace', 'N/A')}
- Metric: {alarm_details.get('metric_name', 'N/A')}
{api_gateway_info}{timeout_guidance}
**相關日誌 (按時間順序，完整內容):**
{log_text}

請以繁體中文回答，格式如下:

ROOT_CAUSE: [詳細描述根本原因,必須包含具體的 API/資料庫/服務名稱,直接引用原始日誌中的關鍵內容]
RECOMMENDATION: [具體的修復建議，1-2 句話]
SEVERITY: [Critical/High/Medium/Low 其中之一]

範例 (timeout):
ROOT_CAUSE: Lambda 在呼叫 "POST https://xlogr-ase1.xdr.trendmicro.com/v3.0/workbench/events" 時發生 "context deadline exceeded" 錯誤,每次請求耗時接近 30 秒導致 timeout
RECOMMENDATION: 降低 HTTP 請求 timeout 至 10 秒並優化重試邏輯,同時檢查與 xlogr-ase1.xdr.trendmicro.com 的網路連線狀況
SEVERITY: Critical

範例 (資料庫):
ROOT_CAUSE: Lambda 執行 "SELECT * FROM evaluation_events WHERE cluster_id = ? AND timestamp > ?" 查詢時因缺少索引導致全表掃描,耗時超過 30 秒
RECOMMENDATION: 在 evaluation_events table 的 (cluster_id, timestamp) 欄位建立複合索引,或實作分頁查詢機制
SEVERITY: High
"""
        return prompt

    def _parse_analysis(self, analysis_text: str) -> Dict[str, str]:
        """解析 Claude 的回應"""
        result = {
            'root_cause': '',
            'recommendation': '',
            'severity': 'Medium'
        }

        lines = analysis_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('ROOT_CAUSE:'):
                result['root_cause'] = line.replace('ROOT_CAUSE:', '').strip()
            elif line.startswith('RECOMMENDATION:'):
                result['recommendation'] = line.replace('RECOMMENDATION:', '').strip()
            elif line.startswith('SEVERITY:'):
                result['severity'] = line.replace('SEVERITY:', '').strip()

        return result


def load_claude_settings() -> Optional[Dict[str, str]]:
    """
    從 ~/.claude/settings.json 讀取 Claude 設定

    Returns:
        設定 dict 或 None (如果設定不存在或無效)
    """
    settings_path = Path.home() / '.claude' / 'settings.json'

    if not settings_path.exists():
        return None

    try:
        with open(settings_path) as f:
            settings = json.load(f)

        env = settings.get('env', {})

        # 檢查必要欄位
        required_fields = [
            'ANTHROPIC_BASE_URL',
            'ANTHROPIC_AUTH_TOKEN',
            'ANTHROPIC_MODEL'
        ]

        if all(env.get(field) for field in required_fields):
            return env
        else:
            return None

    except Exception:
        return None
