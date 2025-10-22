import aiohttp
from typing import Optional
from pixelarraythirdparty.client import Client


class UserManager(Client):
    def list_user(
        self,
        page: int = 1,
        page_size: int = 10,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ):
        """
        获取用户列表
        
        功能说明：
            分页查询用户列表，支持按角色和状态进行筛选。仅管理员可访问。
        
        输入参数：
            page (int, 可选): 页码，默认为1，最小值为1
            page_size (int, 可选): 每页数量，默认为10，范围为1-1000
            role (str, 可选): 用户角色筛选，可选值：
                - "admin": 管理员
                - "user": 普通用户
            is_active (bool, 可选): 用户状态筛选，True为激活，False为禁用
        
        返回字段：
            data (dict): 用户列表信息
                - users (list): 用户列表
                    - id (int): 用户ID
                    - username (str): 用户名
                    - email (str): 邮箱地址
                    - role (str): 用户角色
                    - is_active (bool): 是否激活
                    - created_at (str): 用户创建时间
                    - last_login_at (str): 最后登录时间
                - total (int): 总用户数量
                - page (int): 当前页码
                - page_size (int): 每页数量
            success (bool): 操作是否成功
        
        异常情况：
            - 权限不足：返回错误信息"权限不足"
            - 获取用户列表失败：返回错误信息"获取用户列表失败"
        """
        params = {"page": page, "page_size": page_size}
        if role is not None:
            params["role"] = role
        if is_active is not None:
            params["is_active"] = is_active
        data, success = self._request("GET", "/api/users/list", params=params)
        if not success:
            return {}, False
        return data, True

    def create_user(self, username: str, password: str, email: str, role: str):
        """
        创建用户
        
        功能说明：
            创建新的用户账户，仅管理员可访问。
        
        输入参数：
            username (str): 用户名，必填
            password (str): 密码，必填
            email (str): 邮箱地址，必填
            role (str): 用户角色，必填，可选值：
                - "admin": 管理员
                - "user": 普通用户
        
        返回字段：
            data (dict): 用户信息
                - id (int): 用户ID
                - username (str): 用户名
                - email (str): 邮箱地址
                - role (str): 用户角色
                - is_active (bool): 是否激活，默认为True
                - created_at (str): 用户创建时间
            success (bool): 操作是否成功
        
        异常情况：
            - 权限不足：返回错误信息"权限不足"
            - 用户名已存在：返回错误信息"用户名已存在"
            - 邮箱已存在：返回错误信息"邮箱已存在"
            - 用户创建失败：返回错误信息"用户创建失败"
        """
        data = {
            "username": username,
            "password": password,
            "email": email,
            "role": role,
        }
        data, success = self._request("POST", "/api/users/create", json=data)
        if not success:
            return {}, False
        return data, True

    def update_user(
        self, user_id: int, username: str, email: str, role: str, is_active: bool
    ):
        """
        更新用户信息
        
        功能说明：
            更新指定用户的信息，包括用户名、邮箱、角色和状态。仅管理员可访问。
        
        输入参数：
            user_id (int): 用户ID，必填
            username (str): 用户名，必填
            email (str): 邮箱地址，必填
            role (str): 用户角色，必填，可选值：
                - "admin": 管理员
                - "user": 普通用户
            is_active (bool): 是否激活，必填
        
        返回字段：
            data (dict): 更新后的用户信息
                - id (int): 用户ID
                - username (str): 用户名
                - email (str): 邮箱地址
                - role (str): 用户角色
                - is_active (bool): 是否激活
                - created_at (str): 用户创建时间
                - updated_at (str): 用户信息更新时间
            success (bool): 操作是否成功
        
        异常情况：
            - 权限不足：返回错误信息"权限不足"
            - 用户不存在：返回错误信息"用户不存在"
            - 用户名已存在：返回错误信息"用户名已存在"
            - 邮箱已存在：返回错误信息"邮箱已存在"
            - 用户信息更新失败：返回错误信息"用户信息更新失败"
        """
        data = {
            "username": username,
            "email": email,
            "role": role,
            "is_active": is_active,
        }
        data, success = self._request("PUT", f"/api/users/{user_id}", json=data)
        if not success:
            return {}, False
        return data, True

    def delete_user(self, user_id: int):
        """
        删除用户
        
        功能说明：
            根据用户ID删除指定的用户记录。仅管理员可访问。
        
        输入参数：
            user_id (int): 用户ID，必填
        
        返回字段：
            data (None): 删除成功时返回None
            success (bool): 操作是否成功
        
        异常情况：
            - 权限不足：返回错误信息"权限不足"
            - 用户不存在：返回错误信息"用户不存在"
            - 删除用户失败：返回错误信息"删除用户失败"
        """
        data, success = self._request("DELETE", f"/api/users/{user_id}")
        if not success:
            return {}, False
        return data, True

    def get_user_detail(self, user_id: int):
        """
        获取用户详情
        
        功能说明：
            根据用户ID获取用户的详细信息。仅管理员可访问。
        
        输入参数：
            user_id (int): 用户ID，必填
        
        返回字段：
            data (dict): 用户详细信息
                - id (int): 用户ID
                - username (str): 用户名
                - email (str): 邮箱地址
                - role (str): 用户角色
                - is_active (bool): 是否激活
                - created_at (str): 用户创建时间
                - last_login_at (str): 最后登录时间
            success (bool): 操作是否成功
        
        异常情况：
            - 权限不足：返回错误信息"权限不足"
            - 用户不存在：返回错误信息"用户不存在"
            - 获取用户详情失败：返回错误信息"获取用户详情失败"
        """
        data, success = self._request("GET", f"/api/users/{user_id}")
        if not success:
            return {}, False
        return data, True

    def reset_user_password(self, user_id: int, new_password: str):
        """
        重置用户密码
        
        功能说明：
            重置指定用户的密码。仅管理员可访问。
        
        输入参数：
            user_id (int): 用户ID，必填
            new_password (str): 新密码，必填
        
        返回字段：
            data (None): 重置成功时返回None
            success (bool): 操作是否成功
        
        异常情况：
            - 权限不足：返回错误信息"权限不足"
            - 用户不存在：返回错误信息"用户不存在"
            - 密码重置失败：返回错误信息"密码重置失败"
        """
        data = {"new_password": new_password}
        data, success = self._request(
            "POST", f"/api/users/{user_id}/reset-password", json=data
        )
        if not success:
            return {}, False
        return data, True
