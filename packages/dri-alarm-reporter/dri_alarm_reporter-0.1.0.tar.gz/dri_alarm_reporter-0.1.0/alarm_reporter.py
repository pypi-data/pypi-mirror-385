#!/usr/bin/env python3
"""
CloudWatch Alarm Daily Reporter
每日分析 CloudWatch Alarms 並追蹤到對應的 Lambda logs
"""

import boto3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional
import json
from collections import defaultdict

# 嘗試載入 Claude Analyzer (可選)
try:
    from claude_analyzer import ClaudeAnalyzer, load_claude_settings
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

class AlarmReporter:
    def __init__(self, regions=None):
        if regions is None:
            # 預設查詢所有 production rings 的 regions
            # Ring1: ap-southeast-2, ap-southeast-1
            # Ring2: us-east-1, ap-south-1
            # Ring3: ap-northeast-1, eu-central-1, me-central-1
            self.regions = [
                'ap-southeast-2', 'ap-southeast-1',  # Ring1
                'us-east-1', 'ap-south-1',           # Ring2
                'ap-northeast-1', 'eu-central-1', 'me-central-1'  # Ring3
            ]
        elif isinstance(regions, str):
            self.regions = [regions]
        else:
            self.regions = regions

        # 為每個 region 建立 clients
        self.clients = {}
        for region in self.regions:
            self.clients[region] = {
                'cloudwatch': boto3.client('cloudwatch', region_name=region),
                'logs': boto3.client('logs', region_name=region),
                'lambda': boto3.client('lambda', region_name=region),
                'apigateway': boto3.client('apigateway', region_name=region)
            }

        # 嘗試初始化 Claude AI 分析器
        self.ai_analyzer = None
        self.ai_enabled = False

        if CLAUDE_AVAILABLE:
            try:
                claude_settings = load_claude_settings()
                if claude_settings:
                    self.ai_analyzer = ClaudeAnalyzer(claude_settings)
                    self.ai_enabled = True
                    print("✨ AI 分析功能已啟用")
            except Exception as e:
                # 靜默失敗，不影響原有功能
                pass

    def get_tw_time_range(self, date: Optional[datetime] = None):
        """
        獲取台灣時間的工作時段 (9:00 - 18:00)
        返回 UTC 時間範圍
        """
        if date is None:
            date = datetime.now(ZoneInfo('Asia/Taipei'))

        # 設定台灣時間的工作時段
        tw_tz = ZoneInfo('Asia/Taipei')
        start_tw = date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_tw = date.replace(hour=18, minute=0, second=0, microsecond=0)

        # 轉換為 UTC (台灣 UTC+8)
        start_utc = start_tw.astimezone(ZoneInfo('UTC'))
        end_utc = end_tw.astimezone(ZoneInfo('UTC'))

        return start_utc, end_utc

    def get_alarm_history(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """
        獲取指定時間範圍內的 alarm history (跨所有 regions)
        """
        alarms_in_period = []

        for i, region in enumerate(self.regions, 1):
            print(f"  查詢 {region} ({i}/{len(self.regions)})...", end=' ', flush=True)
            try:
                cloudwatch = self.clients[region]['cloudwatch']
                paginator = cloudwatch.get_paginator('describe_alarm_history')

                page_iterator = paginator.paginate(
                    StartDate=start_time,
                    EndDate=end_time,
                    HistoryItemType='StateUpdate',
                    MaxRecords=100
                )

                region_alarms = 0
                for page in page_iterator:
                    for item in page['AlarmHistoryItems']:
                        history_data = json.loads(item['HistoryData'])
                        # 只記錄進入 ALARM 狀態的事件
                        if history_data.get('newState', {}).get('stateValue') == 'ALARM':
                            alarms_in_period.append({
                                'alarm_name': item['AlarmName'],
                                'timestamp': item['Timestamp'],
                                'summary': item.get('HistorySummary', ''),
                                'new_state': history_data.get('newState', {}),
                                'region': region  # 記錄 region
                            })
                            region_alarms += 1

                print(f"找到 {region_alarms} 個 alarms")
            except Exception as e:
                print(f"錯誤: {e}")

        return alarms_in_period

    def get_alarm_details(self, alarm_name: str, region: str) -> Optional[Dict]:
        """
        獲取 alarm 的詳細設定
        """
        try:
            cloudwatch = self.clients[region]['cloudwatch']
            response = cloudwatch.describe_alarms(AlarmNames=[alarm_name])
            if response['MetricAlarms']:
                alarm = response['MetricAlarms'][0]
                return {
                    'alarm_name': alarm['AlarmName'],
                    'namespace': alarm.get('Namespace'),
                    'metric_name': alarm.get('MetricName'),
                    'dimensions': alarm.get('Dimensions', []),
                    'state_reason': alarm.get('StateReason', ''),
                    'region': region
                }
        except Exception as e:
            print(f"Error getting alarm details for {alarm_name} in {region}: {e}")
        return None

    def extract_lambda_function(self, alarm_details: Dict) -> Optional[str]:
        """
        從 alarm dimensions 中提取 Lambda function name
        """
        if alarm_details['namespace'] != 'AWS/Lambda':
            return None

        for dim in alarm_details['dimensions']:
            if dim['Name'] == 'FunctionName':
                return dim['Value']
        return None

    def extract_lambda_log_group_from_text(self, text: str) -> Optional[str]:
        """
        從文字中提取 Lambda log group 路徑

        Args:
            text: 可能包含 log group 路徑的文字

        Returns:
            Lambda log group 路徑，例如: /aws/lambda/production-get-credit-usage
        """
        import re

        # 尋找 /aws/lambda/* 格式的路徑
        pattern = r'/aws/lambda/[\w\-]+'
        match = re.search(pattern, text)

        if match:
            return match.group(0)

        return None

    def get_api_gateway_log_group(self, api_name: str, region: str) -> Optional[str]:
        """
        從 API Gateway 名稱查詢對應的 execution log group

        Args:
            api_name: API Gateway 名稱 (例如: production-vcs-inventory)
            region: AWS region

        Returns:
            Log group 名稱，例如: API-Gateway-Execution-Logs_{api_id}/production
        """
        try:
            apigateway_client = self.clients[region]['apigateway']

            # 查詢所有 REST APIs
            response = apigateway_client.get_rest_apis()

            # 找到匹配的 API
            for api in response.get('items', []):
                if api['name'] == api_name:
                    api_id = api['id']
                    # 假設使用 production stage
                    return f'API-Gateway-Execution-Logs_{api_id}/production'

            return None
        except Exception as e:
            print(f"    Error querying API Gateway: {e}")
            return None

    def infer_lambda_from_api_gateway_alarm(self, alarm_name: str) -> Optional[str]:
        """
        從 API Gateway alarm 名稱推測後端 Lambda function name
        例如: production-vcs-inventory-5XX-Error -> /aws/lambda/production-vcs-inventory
        """
        import re
        # 匹配 production-{service-name}-5XX-Error 或類似模式
        match = re.match(r'production-([a-z0-9\-]+?)(?:-5XX-Error|-4XX-Error|-error)', alarm_name, re.IGNORECASE)
        if match:
            service_name = match.group(1)
            return f'/aws/lambda/production-{service_name}'
        return None

    def extract_log_group_from_custom_metric(self, alarm_details: Dict, region: str) -> Optional[str]:
        """
        從 custom metric alarm 中嘗試提取 log group name
        支援:
        - Lambda alarms
        - API Gateway alarms
        - Custom metric alarms
        """
        alarm_name = alarm_details['alarm_name']
        namespace = alarm_details['namespace']
        metric_name = alarm_details['metric_name']
        dimensions = alarm_details.get('dimensions', [])

        # 處理 API Gateway alarms
        if namespace == 'AWS/ApiGateway':
            # 從 dimensions 中提取 ApiName
            for dim in dimensions:
                if dim['Name'] == 'ApiName':
                    api_name = dim['Value']
                    return self.get_api_gateway_log_group(api_name, region)
            return None

        # 處理 vcs-inventory-production-* pattern
        if 'vcs-inventory-production' in alarm_name and 'logErrors' in alarm_name:
            # 提取 lambda function name
            # vcs-inventory-production-k8s-inventory-clusters-logErrors
            # -> k8s-inventory-clusters
            parts = alarm_name.replace('vcs-inventory-production-', '').replace('-logErrors', '')
            return f'/aws/lambda/production-{parts}'

        # 處理 container-security namespace pattern (這些也是 Lambda!)
        if namespace == 'container-security/production':
            # LogErrorCount/evaluator -> evaluator
            # LogErrorCount/healthInfoForwarder -> health-info-forwarder
            # LogErrorCount/startScan -> start-scan
            if 'LogErrorCount/' in metric_name:
                service_name = metric_name.split('/')[-1]
                # 轉換 camelCase 為 kebab-case
                import re
                kebab_name = re.sub(r'(?<!^)(?=[A-Z])', '-', service_name).lower()
                return f'/aws/lambda/production-{kebab_name}'

        # 處理 vcs-us-east-1-production-* pattern
        if alarm_name.startswith('vcs-us-east-1-production-'):
            # vcs-us-east-1-production-evaluator-ErrorCountGreaterThanZero
            # -> production-evaluator
            parts = alarm_name.replace('vcs-us-east-1-production-', '').split('-ErrorCount')[0]
            return f'/aws/lambda/production-{parts}'

        return None

    def get_error_logs(self, log_group_name: str, region: str, start_time: datetime,
                      end_time: datetime, max_logs: int = 10, include_all: bool = False) -> List[Dict]:
        """
        獲取指定 log group 的錯誤日誌
        支援多種日誌格式：JSON 和純文字
        """
        errors = []

        try:
            logs_client = self.clients[region]['logs']

            # 根據 log group 類型選擇 filter pattern
            is_api_gateway = log_group_name.startswith('API-Gateway-Execution-Logs_')

            if include_all:
                # 如果需要包含所有日誌,不使用 filter pattern
                response = logs_client.filter_log_events(
                    logGroupName=log_group_name,
                    startTime=int(start_time.timestamp() * 1000),
                    endTime=int(end_time.timestamp() * 1000),
                    limit=max_logs
                )

                for event in response.get('events', []):
                    errors.append({
                        'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000,
                                                           ZoneInfo('Asia/Taipei')),
                        'message': event['message'],
                        'log_stream': event['logStreamName']
                    })
            else:
                # 嘗試多種 filter patterns 來捕獲不同格式的錯誤日誌
                filter_patterns = []

                if is_api_gateway:
                    # API Gateway 執行日誌格式
                    filter_patterns = ['?"Status: 5" ?500 ?502 ?503 ?504 ?statusCode']
                else:
                    # Lambda 日誌支援多種格式
                    filter_patterns = [
                        # JSON 格式: {"level": "error"}
                        '{$.level = "error"}',
                        # JSON 格式: {"severity": "error"}
                        '{$.severity = "error"}',
                        # 純文字格式
                        '?ERROR ?Error ?error ?Exception ?exception ?Task timed out ?WARN ?Warning'
                    ]

                # 使用每個 pattern 查詢，直到找到足夠的 logs
                seen_messages = set()  # 用於去重

                for pattern in filter_patterns:
                    try:
                        response = logs_client.filter_log_events(
                            logGroupName=log_group_name,
                            startTime=int(start_time.timestamp() * 1000),
                            endTime=int(end_time.timestamp() * 1000),
                            filterPattern=pattern,
                            limit=max_logs
                        )

                        for event in response.get('events', []):
                            # 去重：同一條日誌可能被多個 pattern 匹配
                            msg_key = (event['timestamp'], event['message'])
                            if msg_key not in seen_messages:
                                seen_messages.add(msg_key)
                                errors.append({
                                    'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000,
                                                                       ZoneInfo('Asia/Taipei')),
                                    'message': event['message'],
                                    'log_stream': event['logStreamName']
                                })

                        # 如果已經找到足夠的 logs，不需要繼續嘗試其他 patterns
                        if len(errors) >= max_logs:
                            break

                    except Exception as pattern_error:
                        # 如果某個 pattern 失敗，繼續嘗試下一個
                        continue

        except logs_client.exceptions.ResourceNotFoundException:
            print(f"Log group not found: {log_group_name}")
        except Exception as e:
            print(f"Error fetching logs for {log_group_name} in {region}: {e}")

        return errors

    def query_api_gateway_5xx_errors_with_insights(
        self,
        log_group_name: str,
        region: str,
        start_time: datetime,
        end_time: datetime,
        max_results: int = 20
    ) -> List[Dict]:
        """
        使用 CloudWatch Logs Insights 查詢 API Gateway 5XX 錯誤

        返回: [
            {
                'timestamp': datetime,
                'request_id': str,
                'status_code': str,
                'error_message': str,
                'lambda_arn': str (如果有)
            }
        ]
        """
        errors = []

        try:
            logs_client = self.clients[region]['logs']

            # Insights 查詢語句
            query_string = f'''fields @timestamp, @message
| filter @message like /Status: 5/ or @message like /500/ or @message like /502/ or @message like /503/ or @message like /504/
| sort @timestamp desc
| limit {max_results}'''

            # 啟動查詢
            start_query_response = logs_client.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query_string
            )

            query_id = start_query_response['queryId']

            # 輪詢查詢結果 (最多等待 30 秒)
            import time
            max_wait = 30
            waited = 0

            while waited < max_wait:
                time.sleep(2)
                waited += 2

                result = logs_client.get_query_results(queryId=query_id)

                if result['status'] == 'Complete':
                    # 解析結果
                    for record in result.get('results', []):
                        message = ''
                        timestamp_str = ''

                        for field in record:
                            if field['field'] == '@message':
                                message = field['value']
                            elif field['field'] == '@timestamp':
                                timestamp_str = field['value']

                        if message and timestamp_str:
                            # 提取 request ID
                            import re
                            request_id_match = re.search(r'\(([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\)', message)
                            request_id = request_id_match.group(1) if request_id_match else None

                            # 提取 status code
                            status_code = None
                            if 'Status: 5' in message:
                                status_match = re.search(r'Status: (\d+)', message)
                                if status_match:
                                    status_code = status_match.group(1)
                            elif 'statusCode' in message:
                                status_match = re.search(r'statusCode["\']?:\s*(\d+)', message)
                                if status_match:
                                    status_code = status_match.group(1)

                            # 解析時間戳
                            try:
                                # CloudWatch Insights 返回格式: "2025-10-07 01:29:14.230"
                                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                                dt = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Taipei'))
                            except:
                                dt = datetime.now(ZoneInfo('Asia/Taipei'))

                            errors.append({
                                'timestamp': dt,
                                'request_id': request_id,
                                'status_code': status_code or '5XX',
                                'error_message': message[:500],  # 限制長度
                                'full_message': message
                            })

                    break
                elif result['status'] == 'Failed':
                    print(f"    Insights 查詢失敗: {result.get('statusMessage', 'Unknown error')}")
                    break

            if waited >= max_wait:
                print(f"    Insights 查詢超時")

        except Exception as e:
            print(f"    Insights 查詢錯誤: {e}")

        return errors

    def extract_lambda_from_request_id(
        self,
        log_group_name: str,
        region: str,
        request_id: str,
        error_timestamp: datetime,
        time_window_seconds: int = 10
    ) -> Optional[str]:
        """
        從 API Gateway logs 中找出特定 request ID 對應的 Lambda function

        查詢策略：
        1. 用 request_id 過濾日誌
        2. 找到 "Endpoint request URI" 包含 Lambda ARN 的行
        3. 提取 function name

        返回: "/aws/lambda/production-xxx" 或 None
        """
        try:
            logs_client = self.clients[region]['logs']

            # 在錯誤時間前後查詢
            start_time = error_timestamp - timedelta(seconds=time_window_seconds)
            end_time = error_timestamp + timedelta(seconds=time_window_seconds)

            # 使用 Insights 查詢
            query_string = f'''fields @timestamp, @message
| filter @message like "{request_id}"
| filter @message like /Endpoint request URI.*lambda/
| sort @timestamp asc
| limit 1'''

            start_query_response = logs_client.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query_string
            )

            query_id = start_query_response['queryId']

            # 輪詢結果
            import time
            for _ in range(10):  # 最多等 20 秒
                time.sleep(2)
                result = logs_client.get_query_results(queryId=query_id)

                if result['status'] == 'Complete':
                    if result.get('results'):
                        for field in result['results'][0]:
                            if field['field'] == '@message':
                                message = field['value']
                                # 提取 Lambda function name
                                # 格式: https://lambda.{region}.amazonaws.com/.../function:arn:aws:lambda:{region}:{account}:function:{name}/invocations
                                import re
                                lambda_match = re.search(r'function[:/]arn:aws:lambda:[^:]+:\d+:function:([^/]+)', message)
                                if lambda_match:
                                    function_name = lambda_match.group(1)
                                    return f'/aws/lambda/{function_name}'

                                # 另一種格式: .../functions/arn:aws:lambda:...:function:{name}/invocations
                                lambda_match2 = re.search(r'functions/arn:aws:lambda:[^:]+:\d+:function:([^/]+)', message)
                                if lambda_match2:
                                    function_name = lambda_match2.group(1)
                                    return f'/aws/lambda/{function_name}'
                    break
                elif result['status'] == 'Failed':
                    break

        except Exception as e:
            print(f"    提取 Lambda function 錯誤: {e}")

        return None

    def find_related_lambda_logs(self, alarm_name: str, region: str) -> List[str]:
        """
        根據 alarm 名稱找出相關的 Lambda log groups
        例如: production-vcs-inventory-5XX-Error
        -> 列出所有 /aws/lambda/production-*inventory* 的 log groups
        """
        import re

        # 從 alarm name 提取關鍵字
        keywords = []
        alarm_lower = alarm_name.lower()

        # 提取可能的服務名稱關鍵字
        if 'inventory' in alarm_lower:
            keywords.append('inventory')
        if 'vcs' in alarm_lower:
            keywords.append('vcs')
        if 'public-api' in alarm_lower:
            keywords.append('public')

        # 如果沒有明顯關鍵字，嘗試從 production-{service}-5XX 格式提取
        match = re.match(r'production-([a-z0-9\-]+?)-5XX', alarm_lower)
        if match:
            service_name = match.group(1)
            # 將 kebab-case 拆分為單詞
            words = service_name.split('-')
            keywords.extend(words)

        if not keywords:
            return []

        # 構建 log group prefix
        prefix = '/aws/lambda/production-'

        # 列出所有相關 log groups
        logs_client = self.clients[region]['logs']
        log_groups = []

        try:
            # 分頁查詢所有 log groups
            paginator = logs_client.get_paginator('describe_log_groups')
            pages = paginator.paginate(
                logGroupNamePrefix=prefix,
                PaginationConfig={'MaxItems': 100}
            )

            for page in pages:
                for log_group in page['logGroups']:
                    log_group_name = log_group['logGroupName']
                    log_group_lower = log_group_name.lower()

                    # 檢查是否包含任一關鍵字
                    if any(keyword in log_group_lower for keyword in keywords):
                        # 計算匹配分數：匹配的關鍵字越多，分數越高
                        score = sum(1 for keyword in keywords if keyword in log_group_lower)
                        log_groups.append((log_group_name, score))

        except Exception as e:
            print(f"    查詢 Lambda log groups 錯誤: {e}")

        # 按匹配分數降序排列，分數相同則按名稱排序
        log_groups.sort(key=lambda x: (-x[1], x[0]))

        return [lg[0] for lg in log_groups]

    def query_lambda_errors_with_insights(
        self,
        log_group_name: str,
        region: str,
        start_time: datetime,
        end_time: datetime,
        max_results: int = 20
    ) -> List[Dict]:
        """
        使用 CloudWatch Logs Insights 查詢 Lambda 錯誤日誌
        專門針對 JSON 格式的錯誤日誌
        """
        errors = []

        try:
            logs_client = self.clients[region]['logs']

            # Insights 查詢語句 - 查找各種錯誤格式
            query_string = f'''fields @timestamp, @message
| filter @message like /"level":"error"/ or @message like /"severity":"error"/ or @message like /ERROR/ or @message like /Exception/ or @message like /Failed/
| sort @timestamp desc
| limit {max_results}'''

            start_query_response = logs_client.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query_string
            )

            query_id = start_query_response['queryId']

            # 輪詢結果 (最多等待 30 秒)
            import time
            for _ in range(15):
                time.sleep(2)
                result = logs_client.get_query_results(queryId=query_id)

                if result['status'] == 'Complete':
                    for record in result.get('results', []):
                        message = ''
                        timestamp_str = ''

                        for field in record:
                            if field['field'] == '@message':
                                message = field['value']
                            elif field['field'] == '@timestamp':
                                timestamp_str = field['value']

                        if message and timestamp_str:
                            try:
                                # CloudWatch Insights 返回格式: "2025-10-17 09:36:39.829"
                                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                                dt = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Taipei'))
                            except:
                                try:
                                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                    dt = dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Asia/Taipei'))
                                except:
                                    dt = datetime.now(ZoneInfo('Asia/Taipei'))

                            errors.append({
                                'timestamp': dt,
                                'message': message,
                                'log_stream': log_group_name
                            })
                    break
                elif result['status'] == 'Failed':
                    break

        except Exception as e:
            print(f"    Lambda Insights 查詢錯誤: {e}")

        return errors

    def get_complete_execution_logs(self, log_group_name: str, region: str,
                                   error_logs: List[Dict], max_logs: int = 200,
                                   is_timeout: bool = False) -> List[Dict]:
        """
        獲取完整的執行日誌（支援 Lambda 和 API Gateway）
        對於每個錯誤日誌,收集該執行的完整日誌

        優化策略:
        - 只處理前 10 條 error logs
        - Timeout 錯誤收集 35 秒，一般錯誤收集 10 秒
        - 合併相同 log stream 的查詢
        - 達到 max_logs 即停止
        """
        complete_logs = []

        try:
            logs_client = self.clients[region]['logs']
            import re
            from collections import defaultdict

            # 偵測 log group 類型
            is_api_gateway = log_group_name.startswith('API-Gateway-Execution-Logs_')

            # 1. 限制處理數量：只處理前 10 條
            logs_to_process = error_logs[:10]

            # 2. 依錯誤類型決定時間範圍
            time_before = 35 if is_timeout else 10  # timeout 需要更長時間追蹤
            time_after = 5

            # 3. 按 log stream 分組，避免重複查詢
            stream_groups = defaultdict(list)
            for error_log in logs_to_process:
                log_stream = error_log['log_stream']
                stream_groups[log_stream].append(error_log)

            # 4. 對每個 log stream 只查詢一次
            for log_stream, errors in stream_groups.items():
                # 4. 提早終止：如果已經收集足夠的日誌，停止處理
                if len(complete_logs) >= max_logs:
                    break

                # 找到該 stream 中最早和最晚的錯誤時間
                earliest = min(errors, key=lambda x: x['timestamp'])
                latest = max(errors, key=lambda x: x['timestamp'])

                # 計算查詢時間範圍（涵蓋所有錯誤）
                execution_start = earliest['timestamp'] - timedelta(seconds=time_before)
                execution_end = latest['timestamp'] + timedelta(seconds=time_after)

                # 提取 request IDs（根據 log group 類型使用不同的 pattern）
                request_ids = set()
                for error in errors:
                    if is_api_gateway:
                        # API Gateway format: (uuid) at beginning of log lines
                        request_id_match = re.search(r'\(([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\)',
                                                    error['message'])
                    else:
                        # Lambda format: uuid in various places
                        request_id_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
                                                    error['message'])

                    if request_id_match:
                        request_ids.add(request_id_match.group(1))

                # 單次 API 呼叫取得該 stream 的所有相關日誌
                response = logs_client.filter_log_events(
                    logGroupName=log_group_name,
                    logStreamNames=[log_stream],
                    startTime=int(execution_start.timestamp() * 1000),
                    endTime=int(execution_end.timestamp() * 1000),
                    limit=max_logs - len(complete_logs)  # 只取剩餘需要的數量
                )

                # 收集日誌
                for event in response.get('events', []):
                    # 嘗試從日誌中找到 request ID
                    event_request_id = 'unknown'
                    for req_id in request_ids:
                        if req_id in event['message']:
                            event_request_id = req_id
                            break

                    complete_logs.append({
                        'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000,
                                                          ZoneInfo('Asia/Taipei')),
                        'message': event['message'],
                        'log_stream': event['logStreamName'],
                        'request_id': event_request_id
                    })

        except Exception as e:
            print(f"Error fetching complete execution logs: {e}")

        # 按時間排序並去重
        seen = set()
        unique_logs = []
        for log in sorted(complete_logs, key=lambda x: x['timestamp']):
            log_key = (log['timestamp'], log['message'][:100])  # 用時間戳和訊息前 100 字元作為 key
            if log_key not in seen:
                seen.add(log_key)
                unique_logs.append(log)

        return unique_logs

    def get_cloudwatch_alarm_url(self, alarm_name: str, region: str, account_id: str = "484917860638") -> str:
        """生成 CloudWatch Alarm 的 URL"""
        return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarm:name={alarm_name}"

    def get_grafana_dashboard_url(self, service_name: str, start_time: datetime, end_time: datetime) -> Optional[str]:
        """
        生成 Grafana Dashboard 深度連結

        Args:
            service_name: 服務名稱 (例如: vcs-inventory, event-forwarder)
            start_time: 開始時間（datetime with timezone）
            end_time: 結束時間（datetime with timezone）

        Returns:
            Grafana Dashboard URL，若無對應 dashboard 則返回 None
        """
        from config.constants import GRAFANA_DASHBOARD_URLS

        # 查找對應的 dashboard URL
        dashboard_base_url = GRAFANA_DASHBOARD_URLS.get(service_name)
        if not dashboard_base_url:
            return None

        # 轉換時間為毫秒時間戳
        from_ms = int(start_time.timestamp() * 1000)
        to_ms = int(end_time.timestamp() * 1000)

        # 構建帶時間範圍的 Grafana URL
        return f"{dashboard_base_url}?from={from_ms}&to={to_ms}"

    def get_cloudwatch_logs_url(
        self,
        log_group_name: str,
        region: str,
        start_time: datetime,
        end_time: datetime,
        filter_pattern: str = ""
    ) -> str:
        """
        生成 CloudWatch Logs Console 深度連結

        Args:
            log_group_name: Log group 名稱
            region: AWS region
            start_time: 開始時間（datetime with timezone）
            end_time: 結束時間（datetime with timezone）
            filter_pattern: 日誌過濾模式（可選）

        Returns:
            CloudWatch Logs Console URL，包含預填的時間範圍和過濾條件
        """
        from urllib.parse import quote

        # 將 log group name 編碼（需要特殊處理斜線）
        # /aws/lambda/production-xxx -> $252Faws$252Flambda$252Fproduction-xxx
        encoded_log_group = log_group_name.replace('/', '$252F')

        # 編碼過濾模式
        encoded_filter = quote(filter_pattern) if filter_pattern else ""

        # 轉換時間為毫秒時間戳
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)

        # 使用配置中的 URL 模板
        from config.constants import CLOUDWATCH_LOGS_URL_TEMPLATE

        url = CLOUDWATCH_LOGS_URL_TEMPLATE.format(
            region=region,
            encoded_log_group=encoded_log_group,
            encoded_filter=encoded_filter,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms
        )

        return url

    def check_alarm_recovery(
        self,
        alarm_name: str,
        region: str,
        alarm_trigger_time: datetime,
        check_window_hours: int = 2
    ) -> Optional[Dict]:
        """
        檢查 Synthetics alarm 是否已恢復

        Args:
            alarm_name: Alarm 名稱
            region: AWS region
            alarm_trigger_time: Alarm 觸發時間
            check_window_hours: 檢查時間窗口（小時）

        Returns:
            若已恢復，返回 {'recovered': True, 'recovery_time': datetime}
            若未恢復，返回 {'recovered': False}
            若無法判斷，返回 None
        """
        try:
            cloudwatch = self.clients[region]['cloudwatch']

            # 檢查觸發時間之後的 alarm history
            check_end_time = alarm_trigger_time + timedelta(hours=check_window_hours)
            now = datetime.now(ZoneInfo('UTC'))
            check_end_time = min(check_end_time, now)  # 不超過現在時間

            # 查詢 alarm history
            response = cloudwatch.describe_alarm_history(
                AlarmName=alarm_name,
                StartDate=alarm_trigger_time,
                EndDate=check_end_time,
                HistoryItemType='StateUpdate',
                MaxRecords=50
            )

            # 尋找從 ALARM -> OK 的狀態轉換
            for item in response.get('AlarmHistoryItems', []):
                history_data = json.loads(item['HistoryData'])
                new_state = history_data.get('newState', {}).get('stateValue')

                if new_state == 'OK':
                    return {
                        'recovered': True,
                        'recovery_time': item['Timestamp']
                    }

            # 未找到恢復記錄
            return {'recovered': False}

        except Exception as e:
            print(f"    檢查 alarm 恢復狀態時發生錯誤: {e}")
            return None

    def format_log_for_display(self, log_message: str, max_fields: int = 20, max_length: int = 1000) -> str:
        """
        格式化日誌訊息以便顯示

        嘗試解析 JSON 格式的日誌並顯示所有欄位
        若非 JSON 格式，則顯示原始訊息

        Args:
            log_message: 原始日誌訊息
            max_fields: 最多顯示多少個欄位
            max_length: 單一欄位值的最大顯示長度

        Returns:
            格式化後的日誌字串（Markdown 格式）
        """
        try:
            # 嘗試解析為 JSON
            log_data = json.loads(log_message)

            if not isinstance(log_data, dict):
                # 非字典格式，顯示原始訊息
                return log_message[:max_length]

            # 格式化 JSON 欄位
            formatted_lines = []
            field_count = 0

            for key, value in log_data.items():
                if field_count >= max_fields:
                    formatted_lines.append(f"... (還有 {len(log_data) - max_fields} 個欄位)")
                    break

                # 將值轉換為字串
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = str(value)

                # 限制長度
                if len(value_str) > max_length:
                    value_str = value_str[:max_length] + "..."

                # 格式化為鍵值對
                formatted_lines.append(f"**{key}**: {value_str}")
                field_count += 1

            return "<br>".join(formatted_lines)

        except json.JSONDecodeError:
            # 非 JSON 格式，顯示原始訊息（限制長度）
            if len(log_message) > max_length:
                return log_message[:max_length] + "..."
            return log_message

    def extract_service_name(self, alarm_details: Dict) -> str:
        """從 alarm 資訊中提取服務名稱"""
        alarm_name = alarm_details['alarm_name']
        namespace = alarm_details.get('namespace', '')

        # 嘗試從 Lambda function name 提取
        function_name = self.extract_lambda_function(alarm_details)
        if function_name:
            # production-list-k8s-sensor-events -> list-k8s-sensor-events
            return function_name.replace('production-', '')

        # 從 alarm name 提取
        if 'vcs-inventory' in alarm_name:
            return 'vcs-inventory'
        elif 'vcs-public-api' in alarm_name:
            return 'vcs-public-api'
        elif 'container-security' in namespace:
            return 'container-security'
        elif 'Synthetics' in alarm_name:
            return 'monitor'

        return 'unknown'

    def classify_alarm_status(self, alarm_details: Dict, error_logs: List[Dict],
                            recovery_info: Optional[Dict] = None) -> tuple[str, str]:
        """
        智能判斷 alarm 狀態

        Returns:
            (status_emoji, status_reason) - 例如 ('✅ recovered', '已自動恢復')
        """
        alarm_name = alarm_details.get('alarm_name', '')

        # 1. 檢查是否已恢復
        if recovery_info and recovery_info.get('recovered'):
            recovery_time = recovery_info['recovery_time'].astimezone(ZoneInfo('Asia/Taipei'))
            return '✅ recovered', f"已於 {recovery_time.strftime('%H:%M')} 恢復"

        # 2. 檢查是否為可忽略的客戶環境問題
        if error_logs:
            log_text = ' '.join([log['message'] for log in error_logs[:20]])

            # 客戶環境問題模式
            ignore_patterns = [
                ('Stack.*does not exist', '客戶未安裝該功能'),
                ('Stack with id.*does not exist', '客戶 CloudFormation Stack 不存在'),
                ('AWS account is in failed state', '客戶帳號狀態異常'),
                ('Container protection.*not enabled', '客戶未啟用容器防護'),
                ('No accounts found to scan', '無可掃描帳號')
            ]

            import re
            for pattern, reason in ignore_patterns:
                if re.search(pattern, log_text, re.IGNORECASE):
                    return '🟡 ignore', reason

        # 3. 檢查嚴重性 - Timeout + 外部服務
        if error_logs:
            log_text = ' '.join([log['message'] for log in error_logs[:50]])

            # Critical: Lambda timeout + 外部 API/服務
            if 'timed out' in log_text.lower() or 'timeout' in log_text.lower():
                if any(keyword in log_text.lower() for keyword in ['xlogr', 'api', 'http', 'request']):
                    return '🔴 critical', 'Lambda timeout 呼叫外部服務'
                return '🟠 high', 'Lambda execution timeout'

            # High: Exception/Error
            if any(keyword in log_text for keyword in ['Exception', 'ERROR', 'Failed', 'error']):
                return '🟠 high', '執行錯誤'

        # 4. 預設: 需要監控
        return '⚠️ monitor', '需要人工確認'

    def extract_key_errors(self, error_logs: List[Dict], max_errors: int = 5) -> List[str]:
        """
        從大量日誌中提取關鍵錯誤訊息

        Args:
            error_logs: 完整的錯誤日誌列表
            max_errors: 最多返回幾條關鍵錯誤

        Returns:
            關鍵錯誤訊息列表
        """
        if not error_logs:
            return []

        key_errors = []
        seen_errors = set()

        # 錯誤關鍵字優先級
        error_keywords = [
            ('timed out', '⏱️'),
            ('Exception', '❌'),
            ('ERROR', '❌'),
            ('Failed', '❌'),
            ('does not exist', '⚠️'),
            ('error', '⚠️'),
            ('warning', '⚠️')
        ]

        import re

        for log in error_logs:
            message = log.get('message', '')

            # 跳過太長或太短的訊息
            if len(message) < 20 or len(message) > 500:
                continue

            # 檢查是否包含錯誤關鍵字
            for keyword, emoji in error_keywords:
                if keyword.lower() in message.lower():
                    # 提取關鍵部分 (前 200 字元)
                    error_snippet = message[:200].strip()

                    # 去重：避免重複的錯誤
                    error_hash = hash(error_snippet[:100])
                    if error_hash not in seen_errors:
                        seen_errors.add(error_hash)
                        key_errors.append(f"{emoji} `{error_snippet}`")

                        if len(key_errors) >= max_errors:
                            return key_errors
                    break

        # 如果沒有找到關鍵錯誤，返回前幾條日誌
        if not key_errors and error_logs:
            for log in error_logs[:max_errors]:
                message = log.get('message', '')[:200].strip()
                if message:
                    key_errors.append(f"📝 `{message}`")

        return key_errors

    def identify_backend_service(self, error_logs: List[Dict]) -> Optional[str]:
        """
        從錯誤日誌推斷後端服務

        Args:
            error_logs: 錯誤日誌列表

        Returns:
            後端服務名稱，若無法識別則返回 None
        """
        if not error_logs:
            return None

        log_text = ' '.join([log.get('message', '') for log in error_logs[:50]])

        # 後端服務識別模式 (按優先順序排列，根據實際人工日誌調整)
        backend_patterns = [
            # BigTable (Google Cloud Bigtable) - 人工日誌中常見 "BT timeout", "Bigtable timeout"
            ('BigTable', ['bigtable', 'BT ', 'gcp.bigtable', 'google.bigtable', 'cloud.google.com/bigtable',
                         'query mgmt scope', 'mgmtscope']),  # mgmt scope queries 通常指向 BigTable

            # xdl/xlogr (Log forwarder service) - 人工日誌: "xdl timed out"
            ('xdl', ['xlogr', 'xdl', 'log-forwarder', 'xlogr-ase1', 'xlogr-ec1', 'xlogr-use1',
                    'xlogr-sg']),

            # SP (Service Provider / internal-api) - 人工日誌: "SP issue"
            ('SP (internal-api)', ['internal-api.xdr', 'internal-api-eu', 'internal-api-ap',
                                   'internal-api-sg', '/fbt/internal', 'SP API', 'SP issue']),

            # CAM API (Cloud Account Management)
            ('CAM API', ['/cam/external', 'cam/api', '/external/cam', 'GetAWSTemporaryCredential']),

            # Synthetics/Canary monitoring
            ('Synthetics', ['synthetics', 'canary', 'APIHealth']),

            # XDR API endpoints
            ('XDR API', ['api.xdr.trendmicro.com', 'api.eu.xdr', 'api.ap.xdr']),
        ]

        for service_name, patterns in backend_patterns:
            if any(pattern.lower() in log_text.lower() for pattern in patterns):
                return service_name

        return None

    def correlate_alarms(self, alarms: List[Dict]) -> List[Dict]:
        """
        關聯並分組相關的 alarms

        Args:
            alarms: Alarm 列表，每個包含 alarm_name, timestamp, service, region 等

        Returns:
            分組後的 alarm 列表，相關的 alarms 會被合併
        """
        if not alarms:
            return []

        # 建立關聯群組
        groups = []
        used_indices = set()

        for i, alarm1 in enumerate(alarms):
            if i in used_indices:
                continue

            # 建立新群組
            group = {
                'primary_alarm': alarm1,
                'related_alarms': [],
                'correlation_reason': []
            }

            # 尋找相關的 alarms
            for j, alarm2 in enumerate(alarms):
                if i == j or j in used_indices:
                    continue

                # 檢查關聯條件
                reasons = self._check_alarm_correlation(alarm1, alarm2)
                if reasons:
                    group['related_alarms'].append(alarm2)
                    group['correlation_reason'].extend(reasons)
                    used_indices.add(j)

            used_indices.add(i)
            groups.append(group)

        return groups

    def _check_alarm_correlation(self, alarm1: Dict, alarm2: Dict) -> List[str]:
        """
        檢查兩個 alarms 是否相關

        Returns:
            相關原因列表，若不相關則返回空列表
        """
        reasons = []

        # 條件 1: 時間接近 (±5分鐘內)
        time1 = alarm1.get('first_occurrence', {}).get('timestamp')
        time2 = alarm2.get('first_occurrence', {}).get('timestamp')

        if time1 and time2:
            time_diff = abs((time1 - time2).total_seconds())
            if time_diff <= 300:  # 5分鐘
                reasons.append('同時觸發')

        # 條件 2: 相同服務
        service1 = alarm1.get('service_name', '')
        service2 = alarm2.get('service_name', '')

        # 提取服務基礎名稱 (移除 region-specific 部分)
        base_service1 = service1.split('-')[0] if service1 else ''
        base_service2 = service2.split('-')[0] if service2 else ''

        if base_service1 and base_service1 == base_service2:
            reasons.append('相同服務')

        # 條件 3: 相同區域
        if alarm1.get('region') == alarm2.get('region'):
            reasons.append('相同區域')

        # 條件 4: 相似的錯誤模式
        desc1 = alarm1.get('description', '').lower()
        desc2 = alarm2.get('description', '').lower()

        # 檢查是否都是 timeout 錯誤
        if 'timeout' in desc1 and 'timeout' in desc2:
            reasons.append('相同錯誤類型(timeout)')

        # 檢查是否都是 5XX 錯誤
        if '5xx' in desc1 and '5xx' in desc2:
            reasons.append('相同錯誤類型(5XX)')

        # 只有在至少有 2 個關聯條件時才認為相關
        if len(reasons) >= 2:
            return reasons
        return []

    def extract_customer_impact(self, error_logs: List[Dict]) -> Dict:
        """
        從錯誤日誌中提取受影響的客戶資訊

        Args:
            error_logs: 錯誤日誌列表

        Returns:
            {
                'customer_ids': List[str],  # 受影響的客戶 ID 列表
                'count': int,               # 受影響客戶數量
                'summary': str              # 摘要文字
            }
        """
        import re

        if not error_logs:
            return {'customer_ids': [], 'count': 0, 'summary': ''}

        customer_ids = set()

        # Customer ID 識別模式 (UUID format) - 根據實際日誌格式優化
        customer_id_patterns = [
            # JSON 格式: "customerId": "uuid" 或 "customerId":"uuid"
            r'["\']?customerId["\']?\s*[:=]\s*["\']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["\']?',
            r'["\']?customerID["\']?\s*[:=]\s*["\']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["\']?',
            r'["\']?customer_id["\']?\s*[:=]\s*["\']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["\']?',

            # v1BusinessID format
            r'v1BusinessID["\']?\s*[:=]\s*["\']?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["\']?',

            # 直接在日誌中的 UUID (更寬鬆的模式，用於人工日誌中直接貼上的 ID)
            # 例如: customerId: d61a1eb5-a61d-4978-b7c0-17112f545f17
            r'customer[A-Za-z]*\s*[:\s]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        ]

        for log in error_logs:
            message = log.get('message', '')
            for pattern in customer_id_patterns:
                matches = re.findall(pattern, message, re.IGNORECASE)
                customer_ids.update(matches)

        customer_list = sorted(list(customer_ids))
        count = len(customer_list)

        # 生成摘要
        if count == 0:
            summary = ''
        elif count == 1:
            summary = f"影響 1 位客戶 ({customer_list[0][:8]}...)"
        elif count <= 3:
            preview = ', '.join([cid[:8] + '...' for cid in customer_list])
            summary = f"影響 {count} 位客戶 ({preview})"
        else:
            preview = ', '.join([cid[:8] + '...' for cid in customer_list[:3]])
            summary = f"影響 {count} 位客戶 ({preview}, ...)"

        return {
            'customer_ids': customer_list,
            'count': count,
            'summary': summary
        }

    def extract_error_context(self, error_logs: List[Dict], status: str,
                            alarm_details: Dict) -> str:
        """
        從 error logs 中智能提取 DRI 需要的關鍵資訊

        Args:
            error_logs: 完整的錯誤日誌列表
            status: Alarm 狀態（包含 emoji 和原因）
            alarm_details: Alarm 詳細資訊

        Returns:
            更具體的錯誤描述
        """
        import re

        if not error_logs:
            return "無法取得錯誤日誌"

        # 合併所有 log messages 用於分析
        log_text = ' '.join([log.get('message', '') for log in error_logs[:50]])
        alarm_name = alarm_details.get('alarm_name', '')

        # 1. Timeout 錯誤 - 提取呼叫的 API/Service
        if 'timeout' in status.lower() or 'timed out' in log_text.lower():
            # 首先識別後端服務
            backend_service = self.identify_backend_service(error_logs)

            # 找出 timeout 前的 HTTP request
            http_patterns = [
                r'https?://([a-zA-Z0-9\.-]+(?:\.[a-zA-Z]{2,})?)',  # URL
                r'calling\s+([a-zA-Z0-9\.-]+)',                    # calling <service>
                r'request\s+to\s+([a-zA-Z0-9\.-]+)',               # request to <service>
                r'fetch(?:ing)?\s+from\s+([a-zA-Z0-9\.-]+)',       # fetch from <service>
                r'connect(?:ing)?\s+to\s+([a-zA-Z0-9\.-]+)'        # connect to <service>
            ]

            api_endpoint = None
            for pattern in http_patterns:
                matches = re.findall(pattern, log_text, re.IGNORECASE)
                if matches:
                    # 取第一個匹配的服務
                    service = matches[0]
                    # 過濾掉內部服務 (IP, localhost, etc.)
                    if not re.match(r'^\d+\.\d+\.\d+\.\d+', service) and 'localhost' not in service:
                        api_endpoint = service
                        break

            # 組合描述：優先使用後端服務，再補充 API endpoint
            if backend_service and api_endpoint:
                return f"{backend_service} timeout (via {api_endpoint})"
            elif backend_service:
                return f"{backend_service} timeout"
            elif api_endpoint:
                return f"Lambda timeout 呼叫 {api_endpoint}"

            # 檢查是否為資料庫 timeout
            if 'database' in log_text.lower() or 'db' in log_text.lower():
                db_info = self._extract_database_info(log_text)
                if db_info:
                    return f"Lambda timeout 查詢 {db_info}"

            # 預設
            return "Lambda timeout (無法識別目標服務)"

        # 2. Database 錯誤 - 提取資料庫資訊
        if any(keyword in log_text.lower() for keyword in ['database', 'db', 'connection', 'postgres', 'mysql']):
            db_info = self._extract_database_info(log_text)
            if db_info:
                # 判斷錯誤類型
                if 'failed to connect' in log_text.lower() or 'connection refused' in log_text.lower():
                    return f"資料庫連線失敗: {db_info}"
                elif 'too many connections' in log_text.lower():
                    return f"資料庫連線數超限: {db_info}"
                elif 'timeout' in log_text.lower():
                    return f"資料庫查詢 timeout: {db_info}"
                else:
                    return f"資料庫錯誤: {db_info}"

        # 3. API Gateway 錯誤 - 提取 request path
        if 'API-Gateway' in alarm_name or 'apigateway' in alarm_name.lower():
            # 嘗試從 logs 提取 request path
            path_match = re.search(r'(?:Method Request path|resource path):\s*([^\s,]+)', log_text, re.IGNORECASE)
            if path_match:
                path = path_match.group(1)

                # 找出 status code
                status_match = re.search(r'Status:\s*(\d{3})', log_text)
                if status_match:
                    status_code = status_match.group(1)
                    return f"API {status_code} 錯誤: {path}"

                return f"API Gateway 錯誤: {path}"

            # 檢查是否為 authorizer 錯誤
            if 'authorizer' in log_text.lower():
                if 'timeout' in log_text.lower():
                    return "Lambda Authorizer timeout"
                elif 'failed' in log_text.lower():
                    return "Lambda Authorizer 驗證失敗"
                return "Lambda Authorizer 錯誤"

        # 4. 外部 API 錯誤 (401, 502, etc.)
        status_code_match = re.search(r'(\d{3})\s+(\d{3}\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', log_text)
        if status_code_match:
            status_code = status_code_match.group(1)
            error_name = status_code_match.group(3) if status_code_match.group(3) else ''

            # 嘗試找出服務名稱
            service_patterns = [
                r'([a-zA-Z0-9-]+)\s+(?:API|api|service)',
                r'request.*?to\s+([a-zA-Z0-9-]+)',
            ]

            service_name = None
            for pattern in service_patterns:
                match = re.search(pattern, log_text, re.IGNORECASE)
                if match:
                    service_name = match.group(1)
                    break

            # 推測原因
            reason = self._guess_error_reason(status_code, error_name)

            if service_name:
                return f"API {status_code} {error_name}: {service_name} ({reason})"
            else:
                return f"API {status_code} {error_name} ({reason})"

        # 5. CloudFormation 錯誤 - 提取 stack name
        if 'cloudformation' in log_text.lower() or 'stack' in log_text.lower():
            stack_match = re.search(r'Stack.*?([A-Za-z0-9_-]{10,})', log_text, re.IGNORECASE)
            if stack_match:
                stack_name = stack_match.group(1)
                if 'does not exist' in log_text.lower():
                    return f"CloudFormation Stack 不存在: {stack_name}"
                elif 'access denied' in log_text.lower() or 'permission' in log_text.lower():
                    return f"CloudFormation 權限不足: {stack_name}"
                return f"CloudFormation 錯誤: {stack_name}"

        # 6. SQS 錯誤
        if 'sqs' in log_text.lower():
            # 提取 operation
            operation_match = re.search(r'SQS:\s*([A-Za-z]+)', log_text)
            operation = operation_match.group(1) if operation_match else 'Operation'

            # 嘗試找出 queue name
            queue_match = re.search(r'queue[:/\s]+([a-zA-Z0-9_-]+)', log_text, re.IGNORECASE)
            if queue_match:
                queue_name = queue_match.group(1)
                return f"SQS {operation} 失敗: {queue_name}"

            return f"SQS {operation} 失敗"

        # 7. 其他執行錯誤 - 嘗試提取關鍵錯誤訊息
        error_patterns = [
            r'error:\s*(.{20,100})',
            r'failed to\s+(.{20,100})',
            r'exception:\s*(.{20,100})'
        ]

        for pattern in error_patterns:
            match = re.search(pattern, log_text, re.IGNORECASE)
            if match:
                error_msg = match.group(1).strip()
                # 清理過長的錯誤訊息
                if len(error_msg) > 80:
                    error_msg = error_msg[:77] + '...'
                return error_msg

        # 預設：返回狀態原因
        if 'Lambda timeout' in status or 'timeout' in status.lower():
            return "Lambda timeout"
        elif 'error' in status.lower() or 'failed' in status.lower():
            return "執行錯誤"

        return "未知錯誤"

    def _extract_database_info(self, log_text: str) -> Optional[str]:
        """
        從 log 中提取資料庫資訊

        Returns:
            格式: "database_name @ endpoint" 或 "database_name"
        """
        import re

        # 提取 database name
        db_name_match = re.search(r'database[=:\s]+[`"\']?([a-zA-Z0-9_-]+)[`"\']?', log_text, re.IGNORECASE)
        db_name = db_name_match.group(1) if db_name_match else None

        # 提取 endpoint (IP:port 或 hostname)
        endpoint_patterns = [
            r'(\d+\.\d+\.\d+\.\d+:\d+)',  # IP:port
            r'([a-zA-Z0-9-]+\.proxy[a-zA-Z0-9-]*)',  # proxy hostname
            r'([a-zA-Z0-9-]+-proxy-[a-zA-Z0-9-]+)'  # proxy pattern
        ]

        endpoint = None
        for pattern in endpoint_patterns:
            match = re.search(pattern, log_text)
            if match:
                endpoint = match.group(1)
                break

        # 組合結果
        if db_name and endpoint:
            return f"{db_name} @ {endpoint}"
        elif db_name:
            return db_name
        elif endpoint:
            return f"database @ {endpoint}"

        return None

    def _guess_error_reason(self, status_code: str, error_name: str) -> str:
        """根據 status code 推測可能的原因"""
        reason_map = {
            '400': '請求格式錯誤',
            '401': '認證失敗',
            '403': '權限不足',
            '404': '資源不存在',
            '408': '請求 timeout',
            '429': 'Rate limit 超限',
            '500': '伺服器內部錯誤',
            '502': '後端服務異常',
            '503': '服務不可用',
            '504': 'Gateway timeout'
        }

        return reason_map.get(status_code, '未知原因')

    def get_alarm_trend(self, alarm_name: str, region: str, days: int = 7) -> Dict:
        """
        獲取 alarm 的趨勢分析（過去 N 天的觸發次數）

        Args:
            alarm_name: Alarm 名稱
            region: AWS region
            days: 查詢天數（預設 7 天）

        Returns:
            {
                'trigger_count': int,  # 觸發次數
                'trend_emoji': str,    # 📈 📊 📉
                'trend_text': str,     # "12 次/週"
                'severity': str        # 'critical' | 'high' | 'medium' | 'low'
            }
        """
        try:
            cloudwatch = self.clients[region]['cloudwatch']
            now = datetime.now(ZoneInfo('UTC'))
            start_date = now - timedelta(days=days)

            # 查詢過去 N 天的 alarm history
            response = cloudwatch.describe_alarm_history(
                AlarmName=alarm_name,
                StartDate=start_date,
                EndDate=now,
                HistoryItemType='StateUpdate',
                MaxRecords=100  # 最多查 100 次
            )

            # 統計進入 ALARM 狀態的次數
            trigger_count = 0
            for item in response.get('AlarmHistoryItems', []):
                history_data = json.loads(item['HistoryData'])
                if history_data.get('newState', {}).get('stateValue') == 'ALARM':
                    trigger_count += 1

            # 計算趨勢
            if trigger_count >= 15:
                trend_emoji = '📈'
                severity = 'critical'
            elif trigger_count >= 5:
                trend_emoji = '📊'
                severity = 'high'
            elif trigger_count >= 1:
                trend_emoji = '📉'
                severity = 'medium'
            else:
                trend_emoji = '✅'
                severity = 'low'

            trend_text = f"{trigger_count} 次/{days}天"

            return {
                'trigger_count': trigger_count,
                'trend_emoji': trend_emoji,
                'trend_text': trend_text,
                'severity': severity
            }

        except Exception as e:
            print(f"    查詢趨勢時發生錯誤: {e}")
            return {
                'trigger_count': 0,
                'trend_emoji': '❓',
                'trend_text': '無法取得',
                'severity': 'unknown'
            }

    def generate_action_items(self, alarm_details: Dict, status: str, description: str,
                             note: str, error_logs: List[Dict]) -> List[str]:
        """
        根據 alarm 資訊自動生成可執行的 Action Items

        Args:
            alarm_details: Alarm 詳細資訊
            status: Alarm 狀態（🔴 critical, 🟠 high, etc.）
            description: 描述文字
            note: AI 建議
            error_logs: 錯誤日誌

        Returns:
            Action items 列表
        """
        actions = []
        alarm_name = alarm_details.get('alarm_name', '')
        log_text = ' '.join([log['message'] for log in error_logs[:20]]) if error_logs else ''

        # 根據狀態生成 actions
        if '🔴 critical' in status or 'Lambda timeout 呼叫外部服務' in status:
            # Critical: Timeout + 外部服務
            if 'xlogr' in log_text.lower():
                actions.append("檢查 xlogr API 服務健康度和回應時間")
                actions.append("降低 Lambda HTTP client timeout 設定為 10 秒")
                actions.append("實作 circuit breaker 機制避免級聯故障")
            elif 'timeout' in description.lower():
                actions.append(f"檢查 {alarm_name} Lambda 的 timeout 設定")
                actions.append("分析 Lambda CloudWatch Logs 確認慢查詢或外部服務延遲")
                actions.append("考慮增加 timeout 或優化程式邏輯")

        elif '🟡 ignore' in status:
            # Ignore: 客戶環境問題
            if '客戶未安裝' in status or 'Stack.*does not exist' in log_text:
                actions.append("確認此 alarm 是否為正常的客戶環境差異")
                actions.append("考慮調整 alarm 觸發條件，排除未安裝服務的帳號")

        elif '🟠 high' in status:
            # High: 執行錯誤
            if 'database' in log_text.lower() or 'db' in log_text.lower():
                actions.append("檢查資料庫連線池狀態和連線數")
                actions.append("確認資料庫 proxy 和 read-only endpoint 健康度")
            elif 'sqs' in log_text.lower():
                actions.append("檢查 SQS queue 健康度和訊息堆積情況")
                actions.append("確認 SQS permissions 和 IAM role 設定")
            elif 'unauthorized' in log_text.lower() or '401' in log_text:
                actions.append("檢查 API authentication token 或憑證有效性")
                actions.append("確認 service account 權限設定")

        # 通用 actions
        if not actions:
            actions.append(f"查看 {alarm_name} 的 CloudWatch Logs 確認根本原因")
            actions.append("檢查相關服務的健康度和依賴項狀態")

        # 添加趨勢相關的 action
        if status in ['🔴 critical', '🟠 high']:
            actions.append("監控此 alarm 的觸發頻率，評估是否需要進一步處理")

        return actions

    def generate_report(self, start_time: datetime, end_time: datetime) -> str:
        """
        生成每日報告（Confluence 表格格式）
        """
        print(f"正在分析 {start_time.astimezone(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d %H:%M')} "
              f"到 {end_time.astimezone(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d %H:%M')} (TW) 的 alarms...")

        # 1. 獲取 alarm history
        alarm_history = self.get_alarm_history(start_time, end_time)

        if not alarm_history:
            return f"✅ 在 {start_time.astimezone(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d')} 工作時段內沒有觸發任何 alarm"

        # 2. 按 alarm name 分組
        alarms_grouped = defaultdict(list)
        for item in alarm_history:
            alarms_grouped[item['alarm_name']].append(item)

        # 3. 收集所有 alarm 資料（用於表格生成）
        table_rows = []

        print(f"\n開始處理 {len(alarms_grouped)} 個 alarms...")

        for alarm_name, occurrences in sorted(alarms_grouped.items(), key=lambda x: x[1][0]['timestamp']):
            print(f"\n處理: {alarm_name}")

            # 獲取 region (從第一個 occurrence)
            region = occurrences[0].get('region', 'us-east-1')

            # 獲取 alarm 詳細資訊
            alarm_details = self.get_alarm_details(alarm_name, region)
            if not alarm_details:
                continue

            # 生成 CloudWatch alarm 連結
            alarm_url = self.get_cloudwatch_alarm_url(alarm_name, region)

            # 提取服務名稱
            service_name = self.extract_service_name(alarm_details)

            # 嘗試獲取 log group (Lambda 或 custom metrics)
            log_group_name = None
            function_name = self.extract_lambda_function(alarm_details)

            if function_name:
                log_group_name = f'/aws/lambda/{function_name}'
            else:
                # 嘗試從 custom metric 提取 log group（包含 API Gateway）
                log_group_name = self.extract_log_group_from_custom_metric(alarm_details, region)

            # 獲取第一次和最後一次觸發時間
            first_occurrence = min(occurrences, key=lambda x: x['timestamp'])
            last_occurrence = max(occurrences, key=lambda x: x['timestamp'])

            # 生成觸發時間列表
            alarm_times = []
            for occurrence in sorted(occurrences, key=lambda x: x['timestamp']):
                tw_time = occurrence['timestamp'].astimezone(ZoneInfo('Asia/Taipei'))
                alarm_times.append(tw_time.strftime('%H:%M'))

            # 初始化變數
            description = ""
            note = ""
            error_logs = []
            complete_execution_logs = []
            recovery_info = None
            log_start = None
            log_end = None

            # 特殊處理: Synthetics alarm 檢查恢復狀態
            is_synthetics_alarm = 'Synthetics' in alarm_name
            if is_synthetics_alarm:
                print(f"  檢查 Synthetics alarm 恢復狀態...", end=' ', flush=True)
                recovery_info = self.check_alarm_recovery(
                    alarm_name,
                    region,
                    first_occurrence['timestamp'],
                    check_window_hours=2
                )

                if recovery_info and recovery_info.get('recovered'):
                    recovery_time = recovery_info['recovery_time'].astimezone(ZoneInfo('Asia/Taipei'))
                    print(f"已恢復於 {recovery_time.strftime('%H:%M')}")
                    description = f"已於 {recovery_time.strftime('%H:%M')} 恢復"
                else:
                    print("尚未恢復")

            # 處理日誌分析（如果未恢復或不是 Synthetics）
            if log_group_name and not (recovery_info and recovery_info.get('recovered')):
                # 查詢錯誤日誌（前後 3 分鐘）
                log_start = first_occurrence['timestamp'] - timedelta(minutes=3)
                log_end = last_occurrence['timestamp'] + timedelta(minutes=3)
                error_logs = self.get_error_logs(log_group_name, region, log_start, log_end, max_logs=100)

                # 檢查是否為 timeout 錯誤
                is_timeout = any('timed out' in log['message'].lower() for log in error_logs)

                # 收集完整的執行日誌
                logs_to_collect = error_logs if error_logs else []

                if not logs_to_collect:
                    sample_start = first_occurrence['timestamp'] - timedelta(minutes=3)
                    sample_end = first_occurrence['timestamp'] + timedelta(minutes=3)
                    logs_to_collect = self.get_error_logs(log_group_name, region, sample_start, sample_end, max_logs=100, include_all=True)

                if logs_to_collect:
                    print(f"  正在收集完整執行日誌...", end=' ', flush=True)
                    complete_execution_logs = self.get_complete_execution_logs(
                        log_group_name, region, logs_to_collect, max_logs=500, is_timeout=is_timeout
                    )
                    print(f"收集到 {len(complete_execution_logs)} 條")

                # AI 分析
                if self.ai_enabled and complete_execution_logs:
                    try:
                        print(f"  正在進行 AI 分析...", end=' ', flush=True)
                        ai_analysis = self.ai_analyzer.analyze_alarm(
                            alarm_details,
                            complete_execution_logs,
                            region,
                            is_timeout=is_timeout if error_logs else False
                        )

                        if ai_analysis:
                            print("完成")
                            description = ai_analysis['root_cause']
                            note = ai_analysis['recommendation']
                        else:
                            print("失敗")
                            description = "AI 分析失敗"
                    except Exception as e:
                        print(f"錯誤: {e}")
                        description = f"AI 分析異常: {str(e)}"
                else:
                    # 沒有 AI 分析，使用基本描述
                    if is_timeout:
                        description = "Lambda timeout"
                    elif error_logs:
                        description = "執行錯誤"
            elif not log_group_name:
                description = "無法識別 log group"

            # 智能狀態判斷
            status_emoji, status_reason = self.classify_alarm_status(
                alarm_details,
                complete_execution_logs if complete_execution_logs else error_logs,
                recovery_info
            )

            # 智能提取錯誤上下文 - 為 description 添加更多細節
            if not description or description in ["Lambda timeout", "執行錯誤", "AI 分析失敗"]:
                # 使用智能提取來改進描述
                context_description = self.extract_error_context(
                    complete_execution_logs if complete_execution_logs else error_logs,
                    status_reason,
                    alarm_details
                )
                # 如果有 AI 分析結果，保留它；否則使用智能提取的結果
                if not description or "AI 分析失敗" not in description:
                    description = context_description

            # 提取關鍵錯誤
            key_errors = self.extract_key_errors(
                complete_execution_logs if complete_execution_logs else error_logs,
                max_errors=3
            )

            # 提取客戶影響分析
            customer_impact = self.extract_customer_impact(
                complete_execution_logs if complete_execution_logs else error_logs
            )

            # 生成 CloudWatch Logs 連結
            logs_url = ""
            if log_group_name and log_start and log_end:
                logs_url = self.get_cloudwatch_logs_url(
                    log_group_name=log_group_name,
                    region=region,
                    start_time=log_start,
                    end_time=log_end,
                    filter_pattern="ERROR"
                )

            # 生成 Grafana Dashboard 連結
            grafana_url = None
            if log_start and log_end:
                grafana_url = self.get_grafana_dashboard_url(
                    service_name=service_name,
                    start_time=log_start,
                    end_time=log_end
                )

            # 獲取趨勢分析
            print(f"  查詢趨勢...", end=' ', flush=True)
            trend_info = self.get_alarm_trend(alarm_name, region, days=7)
            print(f"{trend_info['trend_text']}")

            # 生成 Action Items
            action_items = self.generate_action_items(
                alarm_details,
                status_emoji,
                description,
                note,
                complete_execution_logs if complete_execution_logs else error_logs
            )

            # 構建表格行資料
            table_row = {
                'alarm_name': alarm_name,
                'alarm_times': alarm_times,
                'alarm_url': alarm_url,
                'service': service_name,
                'status': status_emoji,
                'status_reason': status_reason,
                'description': description,
                'note': note,
                'key_errors': key_errors,
                'customer_impact': customer_impact,
                'logs_url': logs_url,
                'grafana_url': grafana_url,
                'region': region,
                'log_count': len(complete_execution_logs) if complete_execution_logs else len(error_logs),
                'trend_info': trend_info,
                'action_items': action_items
            }

            table_rows.append(table_row)

        # 4. 生成 Markdown 表格
        report_date = start_time.astimezone(ZoneInfo('Asia/Taipei')).strftime('%Y%m%d')
        report_lines = []

        # 標題
        report_lines.append(f"# DRI Diary - {report_date}")
        report_lines.append("")

        # 統計摘要（即時計算）
        total_alarms = len(table_rows)
        critical_count = sum(1 for row in table_rows if '🔴 critical' in row['status'])
        recovered_count = sum(1 for row in table_rows if '✅ recovered' in row['status'])
        ignore_count = sum(1 for row in table_rows if '🟡 ignore' in row['status'])

        report_lines.append("## 📊 摘要")
        report_lines.append(f"- **Total Alarms**: {total_alarms}")
        report_lines.append(f"- **Critical**: {critical_count}")
        report_lines.append(f"- **Recovered**: {recovered_count}")
        report_lines.append(f"- **Ignore** (客戶環境): {ignore_count}")
        report_lines.append("")

        # 表格 header (增加趨勢欄位)
        report_lines.append("| Alarm | Service | Trend | Status | Description | Note |")
        report_lines.append("|-------|---------|-------|--------|-------------|------|")

        # 表格內容
        for row in table_rows:
            # Alarm 欄位: 時間 + 連結
            times_str = ' '.join(row['alarm_times'])
            alarm_cell = f"{times_str} [{row['alarm_name']}]({row['alarm_url']})"

            # Service 欄位
            service_cell = row['service']

            # Trend 欄位: emoji + 文字
            trend_info = row.get('trend_info', {})
            trend_cell = f"{trend_info.get('trend_emoji', '❓')}<br>{trend_info.get('trend_text', 'N/A')}"

            # Status 欄位: emoji + 原因
            status_cell = f"{row['status']}<br>{row['status_reason']}"

            # Description 欄位: AI 分析結果 或基本描述
            desc_cell = row['description'] if row['description'] else "-"

            # Note 欄位: AI 建議 + 客戶影響 + 關鍵錯誤 + Action Items + Logs 連結
            note_parts = []

            # AI 建議
            if row['note']:
                note_parts.append(f"**建議**: {row['note']}")

            # 客戶影響 (如果有)
            customer_impact = row.get('customer_impact', {})
            if customer_impact and customer_impact.get('count', 0) > 0:
                note_parts.append(f"<br>**客戶影響**: {customer_impact['summary']}")

            # 關鍵錯誤 (精簡顯示)
            if row['key_errors']:
                note_parts.append(f"<br>**關鍵錯誤**:<br>{'<br>'.join(row['key_errors'])}")

            # Action Items
            if row.get('action_items'):
                action_list = '<br>'.join([f"- {item}" for item in row['action_items'][:3]])  # 只顯示前 3 個
                note_parts.append(f"<br>**Action Items**:<br>{action_list}")

            # 連結區塊
            links = []
            if row['logs_url']:
                links.append(f"[查看日誌 ({row['log_count']} 條)]({row['logs_url']})")
            if row.get('grafana_url'):
                links.append(f"[Grafana Dashboard]({row['grafana_url']})")

            if links:
                note_parts.append(f"<br>{' | '.join(links)}")

            note_cell = ''.join(note_parts) if note_parts else "-"

            # 生成表格行
            report_lines.append(f"| {alarm_cell} | {service_cell} | {trend_cell} | {status_cell} | {desc_cell} | {note_cell} |")

        return "\n".join(report_lines)
    def run_daily_report(self, date: Optional[datetime] = None, save_to_file: bool = True):
        """
        執行每日報告

        Args:
            date: 指定的日期（預設為今天）
            save_to_file: 是否將報告儲存到檔案（預設 True）
        """
        import os

        start_time, end_time = self.get_tw_time_range(date)
        report = self.generate_report(start_time, end_time)
        print(report)

        # 儲存到檔案
        if save_to_file:
            # 建立 report 目錄
            report_dir = 'report'
            os.makedirs(report_dir, exist_ok=True)

            # 使用台灣時間的日期作為檔名
            report_date = start_time.astimezone(ZoneInfo('Asia/Taipei')).strftime('%Y%m%d')
            report_file = os.path.join(report_dir, f'{report_date}.md')

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"\n✅ 報告已儲存至: {report_file}")

        return report


def main():
    """
    主程式入口
    """
    import sys

    # 預設查詢所有 production rings 的 regions
    reporter = AlarmReporter()

    # 檢查是否有命令列參數指定日期
    if len(sys.argv) > 1:
        # 支援格式: python alarm_reporter.py 2025-10-17
        # 或: python alarm_reporter.py 2025-10-16
        date_str = sys.argv[1]
        try:
            # 解析日期字串 (格式: YYYY-MM-DD)
            from datetime import datetime
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            # 設定為台灣時區
            specific_date = parsed_date.replace(tzinfo=ZoneInfo('Asia/Taipei'))
            print(f"查詢日期: {date_str}\n")
            reporter.run_daily_report(specific_date)
        except ValueError:
            print(f"錯誤: 日期格式不正確。請使用 YYYY-MM-DD 格式，例如: 2025-10-17")
            print(f"用法: python alarm_reporter.py [YYYY-MM-DD]")
            print(f"範例: python alarm_reporter.py 2025-10-16")
            sys.exit(1)
    else:
        # 沒有參數，執行今天的報告
        print("查詢日期: 今天\n")
        reporter.run_daily_report()


if __name__ == '__main__':
    main()
