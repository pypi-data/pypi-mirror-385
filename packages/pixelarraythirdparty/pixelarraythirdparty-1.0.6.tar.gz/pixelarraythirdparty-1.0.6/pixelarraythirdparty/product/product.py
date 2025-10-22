from pixelarraythirdparty.client import Client


class ProductManager(Client):
    def create_product(
        self,
        name: str,
        description: str,
        price: float,
        category: str,
        status: str,
        is_subscription: bool,
        subscription_period: str,
        features: str,
        sort_order: int,
    ):
        """
        创建产品
        
        功能说明：
            创建新的产品，支持订阅产品和一次性产品，产品信息包括名称、描述、价格、分类等。
        
        输入参数：
            name (str): 产品名称，必填
            description (str): 产品描述，必填
            price (float): 产品价格（元），必填
            category (str): 产品分类，必填
            status (str): 产品状态，必填，可选值：
                - "ACTIVE": 激活
                - "INACTIVE": 停用
            is_subscription (bool): 是否为订阅产品，必填
            subscription_period (str): 订阅周期，必填，可选值：
                - "MONTHLY": 月付
                - "YEARLY": 年付
            features (str): 产品特性，JSON格式字符串，必填
            sort_order (int): 排序权重，必填
        
        返回字段：
            data (dict): 产品信息
                - id (int): 产品ID
                - name (str): 产品名称
                - description (str): 产品描述
                - price (float): 产品价格（元）
                - category (str): 产品分类
                - status (str): 产品状态
                - is_subscription (bool): 是否为订阅产品
                - subscription_period (str): 订阅周期
                - features (str): 产品特性（JSON格式）
                - sort_order (int): 排序权重
                - created_at (str): 产品创建时间
                - updated_at (str): 产品更新时间
            success (bool): 操作是否成功
        
        异常情况：
            - 产品创建失败：返回错误信息"产品创建失败"
        """
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "status": status,
            "is_subscription": is_subscription,
            "subscription_period": subscription_period,
            "features": features,
            "sort_order": sort_order,
        }
        data, success = self._request("POST", "/api/products/create", json=data)
        if not success:
            return {}, False
        return data, True

    def list_product(
        self,
        page: int = 1,
        page_size: int = 10,
        status: str = None,
        category: str = None,
        name: str = None,
    ):
        """
        获取产品列表
        
        功能说明：
            分页查询产品列表，支持按状态、分类和名称进行筛选。
        
        输入参数：
            page (int, 可选): 页码，默认为1，最小值为1
            page_size (int, 可选): 每页数量，默认为10，范围为1-1000
            status (str, 可选): 产品状态筛选，可选值：
                - "ACTIVE": 激活
                - "INACTIVE": 停用
            category (str, 可选): 产品分类筛选
            name (str, 可选): 产品名称搜索，支持模糊匹配
        
        返回字段：
            data (dict): 产品列表信息
                - products (list): 产品列表
                    - id (int): 产品ID
                    - name (str): 产品名称
                    - description (str): 产品描述
                    - price (float): 产品价格（元）
                    - category (str): 产品分类
                    - status (str): 产品状态
                    - is_subscription (bool): 是否为订阅产品
                    - subscription_period (str): 订阅周期
                    - features (str): 产品特性（JSON格式）
                    - sort_order (int): 排序权重
                    - created_at (str): 产品创建时间
                    - updated_at (str): 产品更新时间
                - total (int): 总产品数量
                - page (int): 当前页码
                - page_size (int): 每页数量
            success (bool): 操作是否成功
        
        异常情况：
            - 获取产品列表失败：返回错误信息"获取产品列表失败"
        """
        params = {
            "page": page,
            "page_size": page_size,
            "status": status,
            "category": category,
            "name": name,
        }
        if status is not None:
            params["status"] = status
        if category is not None:
            params["category"] = category
        if name is not None:
            params["name"] = name
        data, success = self._request("GET", "/api/products/list", params=params)
        if not success:
            return {}, False
        return data, True

    def get_product_detail(self, product_id: str):
        """
        获取产品详情
        
        功能说明：
            根据产品ID获取产品的详细信息。
        
        输入参数：
            product_id (str): 产品ID，必填
        
        返回字段：
            data (dict): 产品详细信息
                - id (int): 产品ID
                - name (str): 产品名称
                - description (str): 产品描述
                - price (float): 产品价格（元）
                - category (str): 产品分类
                - status (str): 产品状态
                - is_subscription (bool): 是否为订阅产品
                - subscription_period (str): 订阅周期
                - features (str): 产品特性（JSON格式）
                - sort_order (int): 排序权重
                - created_at (str): 产品创建时间
                - updated_at (str): 产品更新时间
            success (bool): 操作是否成功
        
        异常情况：
            - 产品不存在：返回错误信息"产品不存在"
            - 获取产品详情失败：返回错误信息"获取产品详情失败"
        """
        data, success = self._request("GET", f"/api/products/{product_id}")
        if not success:
            return {}, False
        return data, True

    def update_product(
        self,
        product_id: str,
        name: str,
        description: str,
        price: float,
        category: str,
        status: str,
        is_subscription: bool,
        subscription_period: str,
        features: str,
        sort_order: int,
    ):
        """
        更新产品信息
        
        功能说明：
            更新指定产品的信息，包括名称、描述、价格、状态等。
        
        输入参数：
            product_id (str): 产品ID，必填
            name (str): 产品名称，必填
            description (str): 产品描述，必填
            price (float): 产品价格（元），必填
            category (str): 产品分类，必填
            status (str): 产品状态，必填，可选值：
                - "ACTIVE": 激活
                - "INACTIVE": 停用
            is_subscription (bool): 是否为订阅产品，必填
            subscription_period (str): 订阅周期，必填，可选值：
                - "MONTHLY": 月付
                - "YEARLY": 年付
            features (str): 产品特性，JSON格式字符串，必填
            sort_order (int): 排序权重，必填
        
        返回字段：
            data (dict): 更新后的产品信息
                - id (int): 产品ID
                - name (str): 产品名称
                - description (str): 产品描述
                - price (float): 产品价格（元）
                - category (str): 产品分类
                - status (str): 产品状态
                - is_subscription (bool): 是否为订阅产品
                - subscription_period (str): 订阅周期
                - features (str): 产品特性（JSON格式）
                - sort_order (int): 排序权重
                - created_at (str): 产品创建时间
                - updated_at (str): 产品更新时间
            success (bool): 操作是否成功
        
        异常情况：
            - 产品不存在：返回错误信息"产品不存在"
            - 产品更新失败：返回错误信息"产品更新失败"
        """
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "status": status,
            "is_subscription": is_subscription,
            "subscription_period": subscription_period,
            "features": features,
            "sort_order": sort_order,
        }
        data, success = self._request("PUT", f"/api/products/{product_id}", json=data)
        if not success:
            return {}, False
        return data, True

    def delete_product(self, product_id: str):
        """
        删除产品
        
        功能说明：
            根据产品ID删除指定的产品记录。
        
        输入参数：
            product_id (str): 产品ID，必填
        
        返回字段：
            data (None): 删除成功时返回None
            success (bool): 操作是否成功
        
        异常情况：
            - 产品不存在：返回错误信息"产品不存在"
            - 删除产品失败：返回错误信息"删除产品失败"
        """
        data, success = self._request("DELETE", f"/api/products/{product_id}")
        if not success:
            return {}, False
        return data, True

    def get_product_categories(self):
        """
        获取产品分类列表
        
        功能说明：
            获取所有可用的产品分类列表。
        
        输入参数：
            无
        
        返回字段：
            data (dict): 产品分类信息
                - categories (list): 产品分类列表，如["subscription", "service", "addon"]
            success (bool): 操作是否成功
        
        异常情况：
            - 获取产品分类失败：返回错误信息"获取产品分类失败"
        """
        data, success = self._request("GET", "/api/products/categories/list")
        if not success:
            return {}, False
        return data, True
