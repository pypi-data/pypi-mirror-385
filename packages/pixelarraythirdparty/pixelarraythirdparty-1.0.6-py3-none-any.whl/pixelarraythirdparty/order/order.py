from pixelarraythirdparty.client import Client, AsyncClient


class OrderManager(Client):
    def create_order(
        self,
        product_id: str,
        body: str = None,
        remark: str = None,
        payment_channel: str = "WECHAT",
    ):
        """
        创建订单
        
        功能说明：
            根据产品ID创建新的订单，系统会自动生成订单号，获取产品价格信息，并创建对应的支付订单。
        
        输入参数：
            product_id (str): 产品ID，必填，用于获取产品信息和价格
            body (str, 可选): 商品描述，如果不提供则使用产品名称
            remark (str, 可选): 订单备注信息
            payment_channel (str, 可选): 支付渠道，默认为"WECHAT"（微信支付）
        
        返回字段：
            data (dict): 订单信息
                - id (int): 订单ID
                - out_trade_no (str): 商户订单号，格式为"ORD_时间戳_随机字符串"
                - payment_status (str): 支付状态，初始为"PENDING"（待支付）
                - payment_channel (str): 支付渠道
                - product_id (str): 产品ID
                - amount (str): 订单金额（元），格式为"99.00"
                - total_fee (int): 订单金额（分），用于支付接口
                - body (str): 商品描述
                - remark (str): 订单备注
                - created_at (str): 订单创建时间
                - updated_at (str): 订单更新时间
            success (bool): 操作是否成功
        
        异常情况：
            - 产品ID为空：返回错误信息"产品ID不能为空"
            - 产品不存在：返回错误信息"产品不存在"
            - 产品价格无效：返回错误信息"产品价格无效"
            - 创建订单失败：返回错误信息"创建订单失败"
        """
        data = {
            "product_id": product_id,
            "body": body,
            "remark": remark,
            "payment_channel": payment_channel,
        }
        data, success = self._request("POST", "/api/orders/create", json=data)
        if not success:
            return {}, False
        return data, True

    def list_order(
        self,
        page: int = 1,
        page_size: int = 10,
        payment_status: str = None,
        out_trade_no: str = None,
    ):
        """
        获取订单列表
        
        功能说明：
            分页查询订单列表，支持按支付状态和订单号进行筛选。
        
        输入参数：
            page (int, 可选): 页码，默认为1，最小值为1
            page_size (int, 可选): 每页数量，默认为10，范围为1-1000
            payment_status (str, 可选): 支付状态筛选，可选值：
                - "PENDING": 待支付
                - "PAID": 已支付
                - "REFUNDED": 已退款
                - "CANCELLED": 已取消
            out_trade_no (str, 可选): 订单号搜索，支持模糊匹配
        
        返回字段：
            data (dict): 订单列表信息
                - orders (list): 订单列表
                    - id (int): 订单ID
                    - out_trade_no (str): 商户订单号
                    - payment_status (str): 支付状态
                    - payment_channel (str): 支付渠道
                    - amount (str): 订单金额（元）
                    - total_fee (int): 订单金额（分）
                    - created_at (str): 订单创建时间
                    - updated_at (str): 订单更新时间
                - total (int): 总订单数量
                - page (int): 当前页码
                - page_size (int): 每页数量
            success (bool): 操作是否成功
        
        异常情况：
            - 获取订单列表失败：返回错误信息"获取订单列表失败"
        """
        params = {
            "page": page,
            "page_size": page_size,
            "payment_status": payment_status,
            "out_trade_no": out_trade_no,
        }
        data, success = self._request("GET", "/api/orders/list", params=params)
        if not success:
            return {}, False
        return data, True

    def get_order_detail(self, out_trade_no: str):
        """
        获取订单详情
        
        功能说明：
            根据订单号获取订单的详细信息，包括支付状态、交易信息等。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
        
        返回字段：
            data (dict): 订单详细信息
                - id (int): 订单ID
                - out_trade_no (str): 商户订单号
                - payment_status (str): 支付状态
                - product_id (str): 产品ID
                - amount (str): 订单金额（元）
                - total_fee (int): 订单金额（分）
                - body (str): 商品描述
                - transaction_id (str): 微信交易号（支付成功后才有）
                - openid (str): 用户openid（支付成功后才有）
                - trade_type (str): 交易类型（支付成功后才有）
                - bank_type (str): 银行类型（支付成功后才有）
                - fee_type (str): 货币类型，默认为"CNY"
                - is_subscribe (str): 是否关注公众号（支付成功后才有）
                - time_end (str): 支付完成时间（支付成功后才有）
                - created_at (str): 订单创建时间
                - updated_at (str): 订单更新时间
                - paid_at (str): 支付时间（支付成功后才有）
                - remark (str): 订单备注
            success (bool): 操作是否成功
        
        异常情况：
            - 订单不存在：返回错误信息"订单不存在"
            - 获取订单详情失败：返回错误信息"获取订单详情失败"
        """
        data, success = self._request("GET", f"/api/orders/{out_trade_no}")
        if not success:
            return {}, False
        return data, True

    def update_order_status(
        self,
        out_trade_no: str,
        payment_status: str,
    ):
        """
        更新订单状态
        
        功能说明：
            更新指定订单的支付状态，仅支持状态修改，其他字段不可修改。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
            payment_status (str): 支付状态，必填，可选值：
                - "PENDING": 待支付
                - "PAID": 已支付
                - "REFUNDED": 已退款
                - "CANCELLED": 已取消
        
        返回字段：
            data (dict): 更新后的订单信息
                - id (int): 订单ID
                - out_trade_no (str): 商户订单号
                - payment_status (str): 更新后的支付状态
                - transaction_id (str): 微信交易号（如果已支付）
                - openid (str): 用户openid（如果已支付）
                - trade_type (str): 交易类型（如果已支付）
                - bank_type (str): 银行类型（如果已支付）
                - fee_type (str): 货币类型
                - is_subscribe (str): 是否关注公众号（如果已支付）
                - time_end (str): 支付完成时间（如果已支付）
                - paid_at (str): 支付时间（如果已支付）
                - updated_at (str): 订单更新时间
                - remark (str): 订单备注
            success (bool): 操作是否成功
        
        异常情况：
            - 支付状态为空：返回错误信息"支付状态不能为空"
            - 订单不存在：返回错误信息"订单不存在"
            - 更新订单状态失败：返回错误信息"更新订单状态失败"
        """
        data = {
            "payment_status": payment_status,
        }
        data, success = self._request(
            "PUT", f"/api/orders/{out_trade_no}/status", json=data
        )
        if not success:
            return {}, False
        return data, True

    def delete_order(self, out_trade_no: str):
        """
        删除订单
        
        功能说明：
            根据订单号删除指定的订单记录。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
        
        返回字段：
            data (None): 删除成功时返回None
            success (bool): 操作是否成功
        
        异常情况：
            - 订单不存在：返回错误信息"订单不存在"
            - 删除订单失败：返回错误信息"删除订单失败"
        """
        data, success = self._request("DELETE", f"/api/orders/{out_trade_no}")
        if not success:
            return {}, False
        return data, True

    def get_order_stats(self):
        """
        获取订单统计信息
        
        功能说明：
            获取订单的统计汇总信息，包括总订单数、各状态订单数量、总金额等。
        
        输入参数：
            无
        
        返回字段：
            data (dict): 订单统计信息
                - total_orders (int): 总订单数量
                - pending_orders (int): 待支付订单数量
                - paid_orders (int): 已支付订单数量
                - refunded_orders (int): 已退款订单数量
                - total_amount (float): 总订单金额（元）
                - total_fee (int): 总订单金额（分）
            success (bool): 操作是否成功
        
        异常情况：
            - 获取订单统计信息失败：返回错误信息"获取订单统计信息失败"
        """
        data, success = self._request("GET", "/api/orders/stats/summary")
        if not success:
            return {}, False
        return data, True

    def generate_qr_code(
        self,
        out_trade_no: str,
        payment_channel: str = "WECHAT",
    ):
        """
        生成支付二维码
        
        功能说明：
            为指定订单生成支付二维码，支持微信支付和支付宝。二维码会自动上传到OSS并返回访问URL。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
            payment_channel (str, 可选): 支付渠道，默认为"WECHAT"，可选值：
                - "WECHAT": 微信支付
                - "ALIPAY": 支付宝（暂未实现）
        
        返回字段：
            data (dict): 二维码信息
                - qr_code_url (str): 二维码图片URL，可直接用于显示
                - out_trade_no (str): 商户订单号
            success (bool): 操作是否成功
        
        异常情况：
            - 订单号为空：返回错误信息"订单号不能为空"
            - 订单不存在：返回错误信息"订单不存在"
            - 不支持的支付渠道：抛出ValueError异常
            - 生成支付二维码失败：返回错误信息"生成支付二维码失败"
        """
        if payment_channel == "WECHAT":
            url = "/api/orders/wx_pay/generate_qr_code"
        elif payment_channel == "ALIPAY":
            url = "/api/orders/ali_pay/generate_qr_code"
        else:
            raise ValueError("Invalid payment channel")
        data, success = self._request(
            "POST",
            url,
            json={
                "out_trade_no": out_trade_no,
            },
        )
        if not success:
            return {}, False
        return data, True

    def refund_order(self, out_trade_no: str, payment_channel: str = "WECHAT"):
        """
        申请订单退款
        
        功能说明：
            为指定订单申请退款，支持微信支付和支付宝。退款申请提交后，系统会处理退款并更新订单状态。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
            payment_channel (str, 可选): 支付渠道，默认为"WECHAT"，可选值：
                - "WECHAT": 微信支付
                - "ALIPAY": 支付宝（暂未实现）
        
        返回字段：
            data (dict): 退款信息
                - out_refund_no (str): 退款单号，格式为"REFUND_订单号_时间戳"
                - out_trade_no (str): 商户订单号
                - total_fee (int): 退款金额（分）
            success (bool): 操作是否成功
        
        异常情况：
            - 订单号为空：返回错误信息"订单号不能为空"
            - 订单不存在：返回错误信息"订单不存在"
            - 订单状态不允许退款：返回错误信息"订单状态不允许退款"
            - 不支持的支付渠道：抛出ValueError异常
            - 退款申请失败：返回错误信息"退款申请失败"
        """
        if payment_channel == "WECHAT":
            url = "/api/orders/wx_pay/refund"
        elif payment_channel == "ALIPAY":
            url = "/api/orders/ali_pay/refund"
        else:
            raise ValueError("Invalid payment channel")
        data, success = self._request(
            "POST",
            url,
            json={"out_trade_no": out_trade_no},
        )
        if not success:
            return {}, False
        return data, True


class OrderManagerAsync(AsyncClient):
    async def create_order(
        self,
        product_id: str,
        body: str = None,
        remark: str = None,
        payment_channel: str = "WECHAT",
    ):
        """
        创建订单（异步版本）
        
        功能说明：
            根据产品ID创建新的订单，系统会自动生成订单号，获取产品价格信息，并创建对应的支付订单。
        
        输入参数：
            product_id (str): 产品ID，必填，用于获取产品信息和价格
            body (str, 可选): 商品描述，如果不提供则使用产品名称
            remark (str, 可选): 订单备注信息
            payment_channel (str, 可选): 支付渠道，默认为"WECHAT"（微信支付）
        
        返回字段：
            data (dict): 订单信息
                - id (int): 订单ID
                - out_trade_no (str): 商户订单号，格式为"ORD_时间戳_随机字符串"
                - payment_status (str): 支付状态，初始为"PENDING"（待支付）
                - payment_channel (str): 支付渠道
                - product_id (str): 产品ID
                - amount (str): 订单金额（元），格式为"99.00"
                - total_fee (int): 订单金额（分），用于支付接口
                - body (str): 商品描述
                - remark (str): 订单备注
                - created_at (str): 订单创建时间
                - updated_at (str): 订单更新时间
            success (bool): 操作是否成功
        
        异常情况：
            - 产品ID为空：返回错误信息"产品ID不能为空"
            - 产品不存在：返回错误信息"产品不存在"
            - 产品价格无效：返回错误信息"产品价格无效"
            - 创建订单失败：返回错误信息"创建订单失败"
        """
        data = {
            "product_id": product_id,
            "body": body,
            "remark": remark,
            "payment_channel": payment_channel,
        }
        data, success = await self._request("POST", "/api/orders/create", json=data)
        if not success:
            return {}, False
        return data, True

    async def list_order(
        self,
        page: int = 1,
        page_size: int = 10,
        payment_status: str = None,
        out_trade_no: str = None,
    ):
        """
        获取订单列表（异步版本）
        
        功能说明：
            分页查询订单列表，支持按支付状态和订单号进行筛选。
        
        输入参数：
            page (int, 可选): 页码，默认为1，最小值为1
            page_size (int, 可选): 每页数量，默认为10，范围为1-1000
            payment_status (str, 可选): 支付状态筛选，可选值：
                - "PENDING": 待支付
                - "PAID": 已支付
                - "REFUNDED": 已退款
                - "CANCELLED": 已取消
            out_trade_no (str, 可选): 订单号搜索，支持模糊匹配
        
        返回字段：
            data (dict): 订单列表信息
                - orders (list): 订单列表
                    - id (int): 订单ID
                    - out_trade_no (str): 商户订单号
                    - payment_status (str): 支付状态
                    - payment_channel (str): 支付渠道
                    - amount (str): 订单金额（元）
                    - total_fee (int): 订单金额（分）
                    - created_at (str): 订单创建时间
                    - updated_at (str): 订单更新时间
                - total (int): 总订单数量
                - page (int): 当前页码
                - page_size (int): 每页数量
            success (bool): 操作是否成功
        
        异常情况：
            - 获取订单列表失败：返回错误信息"获取订单列表失败"
        """
        params = {
            "page": page,
            "page_size": page_size,
            "payment_status": payment_status,
            "out_trade_no": out_trade_no,
        }
        data, success = await self._request("GET", "/api/orders/list", params=params)
        if not success:
            return {}, False
        return data, True

    async def get_order_detail(self, out_trade_no: str):
        """
        获取订单详情（异步版本）
        
        功能说明：
            根据订单号获取订单的详细信息，包括支付状态、交易信息等。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
        
        返回字段：
            data (dict): 订单详细信息
                - id (int): 订单ID
                - out_trade_no (str): 商户订单号
                - payment_status (str): 支付状态
                - product_id (str): 产品ID
                - amount (str): 订单金额（元）
                - total_fee (int): 订单金额（分）
                - body (str): 商品描述
                - transaction_id (str): 微信交易号（支付成功后才有）
                - openid (str): 用户openid（支付成功后才有）
                - trade_type (str): 交易类型（支付成功后才有）
                - bank_type (str): 银行类型（支付成功后才有）
                - fee_type (str): 货币类型，默认为"CNY"
                - is_subscribe (str): 是否关注公众号（支付成功后才有）
                - time_end (str): 支付完成时间（支付成功后才有）
                - created_at (str): 订单创建时间
                - updated_at (str): 订单更新时间
                - paid_at (str): 支付时间（支付成功后才有）
                - remark (str): 订单备注
            success (bool): 操作是否成功
        
        异常情况：
            - 订单不存在：返回错误信息"订单不存在"
            - 获取订单详情失败：返回错误信息"获取订单详情失败"
        """
        data, success = await self._request("GET", f"/api/orders/{out_trade_no}")
        if not success:
            return {}, False
        return data, True

    async def update_order_status(self, out_trade_no: str, payment_status: str):
        """
        更新订单状态（异步版本）
        
        功能说明：
            更新指定订单的支付状态，仅支持状态修改，其他字段不可修改。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
            payment_status (str): 支付状态，必填，可选值：
                - "PENDING": 待支付
                - "PAID": 已支付
                - "REFUNDED": 已退款
                - "CANCELLED": 已取消
        
        返回字段：
            data (dict): 更新后的订单信息
                - id (int): 订单ID
                - out_trade_no (str): 商户订单号
                - payment_status (str): 更新后的支付状态
                - transaction_id (str): 微信交易号（如果已支付）
                - openid (str): 用户openid（如果已支付）
                - trade_type (str): 交易类型（如果已支付）
                - bank_type (str): 银行类型（如果已支付）
                - fee_type (str): 货币类型
                - is_subscribe (str): 是否关注公众号（如果已支付）
                - time_end (str): 支付完成时间（如果已支付）
                - paid_at (str): 支付时间（如果已支付）
                - updated_at (str): 订单更新时间
                - remark (str): 订单备注
            success (bool): 操作是否成功
        
        异常情况：
            - 支付状态为空：返回错误信息"支付状态不能为空"
            - 订单不存在：返回错误信息"订单不存在"
            - 更新订单状态失败：返回错误信息"更新订单状态失败"
        """
        data = {"payment_status": payment_status}
        data, success = await self._request(
            "PUT", f"/api/orders/{out_trade_no}/status", json=data
        )
        if not success:
            return {}, False
        return data, True

    async def delete_order(self, out_trade_no: str):
        """
        删除订单（异步版本）
        
        功能说明：
            根据订单号删除指定的订单记录。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
        
        返回字段：
            data (None): 删除成功时返回None
            success (bool): 操作是否成功
        
        异常情况：
            - 订单不存在：返回错误信息"订单不存在"
            - 删除订单失败：返回错误信息"删除订单失败"
        """
        data, success = await self._request("DELETE", f"/api/orders/{out_trade_no}")
        if not success:
            return {}, False
        return data, True

    async def get_order_stats(self):
        """
        获取订单统计信息（异步版本）
        
        功能说明：
            获取订单的统计汇总信息，包括总订单数、各状态订单数量、总金额等。
        
        输入参数：
            无
        
        返回字段：
            data (dict): 订单统计信息
                - total_orders (int): 总订单数量
                - pending_orders (int): 待支付订单数量
                - paid_orders (int): 已支付订单数量
                - refunded_orders (int): 已退款订单数量
                - total_amount (float): 总订单金额（元）
                - total_fee (int): 总订单金额（分）
            success (bool): 操作是否成功
        
        异常情况：
            - 获取订单统计信息失败：返回错误信息"获取订单统计信息失败"
        """
        data, success = await self._request("GET", "/api/orders/stats/summary")
        if not success:
            return {}, False
        return data, True

    async def generate_qr_code(
        self, out_trade_no: str, payment_channel: str = "WECHAT"
    ):
        """
        生成支付二维码（异步版本）
        
        功能说明：
            为指定订单生成支付二维码，支持微信支付和支付宝。二维码会自动上传到OSS并返回访问URL。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
            payment_channel (str, 可选): 支付渠道，默认为"WECHAT"，可选值：
                - "WECHAT": 微信支付
                - "ALIPAY": 支付宝（暂未实现）
        
        返回字段：
            data (dict): 二维码信息
                - qr_code_url (str): 二维码图片URL，可直接用于显示
                - out_trade_no (str): 商户订单号
            success (bool): 操作是否成功
        
        异常情况：
            - 订单号为空：返回错误信息"订单号不能为空"
            - 订单不存在：返回错误信息"订单不存在"
            - 不支持的支付渠道：抛出ValueError异常
            - 生成支付二维码失败：返回错误信息"生成支付二维码失败"
        """
        if payment_channel == "WECHAT":
            url = "/api/orders/wx_pay/generate_qr_code"
        elif payment_channel == "ALIPAY":
            url = "/api/orders/ali_pay/generate_qr_code"
        else:
            raise ValueError("Invalid payment channel")
        data, success = await self._request(
            "POST", url, json={"out_trade_no": out_trade_no}
        )
        if not success:
            return {}, False
        return data, True

    async def refund_order(self, out_trade_no: str, payment_channel: str = "WECHAT"):
        """
        申请订单退款（异步版本）
        
        功能说明：
            为指定订单申请退款，支持微信支付和支付宝。退款申请提交后，系统会处理退款并更新订单状态。
        
        输入参数：
            out_trade_no (str): 商户订单号，必填
            payment_channel (str, 可选): 支付渠道，默认为"WECHAT"，可选值：
                - "WECHAT": 微信支付
                - "ALIPAY": 支付宝（暂未实现）
        
        返回字段：
            data (dict): 退款信息
                - out_refund_no (str): 退款单号，格式为"REFUND_订单号_时间戳"
                - out_trade_no (str): 商户订单号
                - total_fee (int): 退款金额（分）
            success (bool): 操作是否成功
        
        异常情况：
            - 订单号为空：返回错误信息"订单号不能为空"
            - 订单不存在：返回错误信息"订单不存在"
            - 订单状态不允许退款：返回错误信息"订单状态不允许退款"
            - 不支持的支付渠道：抛出ValueError异常
            - 退款申请失败：返回错误信息"退款申请失败"
        """
        if payment_channel == "WECHAT":
            url = "/api/orders/wx_pay/refund"
        elif payment_channel == "ALIPAY":
            url = "/api/orders/ali_pay/refund"
        else:
            raise ValueError("Invalid payment channel")
        data, success = await self._request(
            "POST", url, json={"out_trade_no": out_trade_no}
        )
        if not success:
            return {}, False
        return data, True
