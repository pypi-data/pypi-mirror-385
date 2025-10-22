from pixelarraythirdparty.client import Client


class CronManager(Client):
    def get_cron_status(self):
        """
        获取Cron服务状态
        
        功能说明：
            获取Cron服务的运行状态，包括已注册的任务、工作节点状态等。
        
        输入参数：
            无
        
        返回字段：
            data (dict): Cron服务状态信息
                - registered_tasks (dict): 已注册的任务列表，按工作节点分组
                - worker_stats (dict): 工作节点统计信息
                - scheduled_task_count (int): 定时任务数量
                - timestamp (str): 状态获取时间
            success (bool): 操作是否成功
        
        异常情况：
            - 获取Cron状态失败：返回错误信息"获取Cron状态失败"
        """
        data, success = self._request("GET", "/api/cron/status")
        if not success:
            return {}, False
        return data, True

    def get_cron_tasks(self):
        """
        获取已注册任务列表
        
        功能说明：
            获取所有已注册的Cron任务列表。
        
        输入参数：
            无
        
        返回字段：
            data (dict): 任务列表信息
                - tasks (list): 已注册的任务名称列表
                - count (int): 任务数量
                - timestamp (str): 获取时间
            success (bool): 操作是否成功
        
        异常情况：
            - 获取任务列表失败：返回错误信息"获取任务列表失败"
        """
        data, success = self._request("GET", "/api/cron/tasks")
        if not success:
            return {}, False
        return data, True

    def get_cron_tasks_scheduled(self):
        """
        获取定时任务列表
        
        功能说明：
            获取所有配置的定时任务列表，包括任务详情、执行时间、状态等。
        
        输入参数：
            无
        
        返回字段：
            data (dict): 定时任务列表信息
                - tasks (list): 定时任务列表
                    - id (str): 任务ID
                    - name (str): 任务名称
                    - description (str): 任务描述
                    - schedule (str): 执行时间
                    - enabled (bool): 是否启用
                    - task_name (str): 任务函数名
                    - module_name (str): 模块名
                    - function_name (str): 函数名
                    - file_path (str): 文件路径
                    - parameters (list): 参数列表
                    - task_config (dict): 任务配置
                    - registration_info (dict): 注册信息
                - count (int): 任务数量
                - timestamp (str): 获取时间
            success (bool): 操作是否成功
        
        异常情况：
            - 获取定时任务列表失败：返回错误信息"获取定时任务列表失败"
        """
        data, success = self._request("GET", "/api/cron/tasks/scheduled")
        if not success:
            return {}, False
        return data, True

    def get_cron_tasks_detail(self, task_name: str):
        """
        获取任务详情
        
        功能说明：
            根据任务名称获取指定任务的详细信息。
        
        输入参数：
            task_name (str): 任务名称，必填，需要URL编码
        
        返回字段：
            data (dict): 任务详细信息
                - task_name (str): 任务名称
                - module_name (str): 模块名
                - function_name (str): 函数名
                - file_path (str): 文件路径
                - description (str): 任务描述
                - parameters (list): 参数列表
                - task_config (dict): 任务配置
                - registration_info (dict): 注册信息
                - timestamp (str): 获取时间
            success (bool): 操作是否成功
        
        异常情况：
            - 任务不存在：返回错误信息"任务不存在"
            - 获取任务详情失败：返回错误信息"获取任务详情失败"
        """
        data, success = self._request("GET", f"/api/cron/tasks/{task_name}")
        if not success:
            return {}, False
        return data, True

    def trigger_cron_task(self, task_name: str, args: list, kwargs: dict):
        """
        触发任务执行
        
        功能说明：
            手动触发指定任务的执行，支持传递参数。
        
        输入参数：
            task_name (str): 任务名称，必填，需要URL编码
            args (list): 任务参数列表，可选
            kwargs (dict): 任务关键字参数，可选
        
        返回字段：
            data (dict): 任务触发信息
                - task_id (str): 任务ID
                - task_name (str): 任务名称
                - status (str): 任务状态，初始为"PENDING"
                - message (str): 触发消息
            success (bool): 操作是否成功
        
        异常情况：
            - 任务不存在：返回错误信息"任务不存在"
            - 任务触发失败：返回错误信息"任务触发失败"
        """
        data, success = self._request(
            "POST",
            f"/api/cron/tasks/{task_name}/trigger",
            json={"args": args, "kwargs": kwargs},
        )
        if not success:
            return {}, False
        return data, True
