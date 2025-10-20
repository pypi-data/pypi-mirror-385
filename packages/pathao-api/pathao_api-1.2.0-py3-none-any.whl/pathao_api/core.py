from . import constants, routes, controllers

class PathaoAPI:
    REQUIRED_CONSTANTS = [
        "PATHAO_BASE_URL",
        "PATHAO_STORE_ID",
        "PATHAO_CLIENT_ID",
        "PATHAO_CLIENT_SECRET",
        "PATHAO_USERNAME",
        "PATHAO_PASSWORD",
    ]

    def __init__(self, 
                 base_url=None,
                 store_id=None,
                 client_id=None,
                 client_secret=None,
                 username=None,
                 password=None):
        # Override constants if provided
        if base_url: constants.PATHAO_BASE_URL = base_url
        if store_id: constants.PATHAO_STORE_ID = store_id
        if client_id: constants.PATHAO_CLIENT_ID = client_id
        if client_secret: constants.PATHAO_CLIENT_SECRET = client_secret
        if username: constants.PATHAO_USERNAME = username
        if password: constants.PATHAO_PASSWORD = password

        # Validate required constants
        for var_name in self.REQUIRED_CONSTANTS:
            if getattr(constants, var_name) in (None, ""):
                raise ValueError(f"{var_name} is not set. Provide it via .env or constructor.")

        self.base_url = constants.PATHAO_BASE_URL
        self.store_id = constants.PATHAO_STORE_ID
        self.client_id = constants.PATHAO_CLIENT_ID
        self.client_secret = constants.PATHAO_CLIENT_SECRET
        self.username = constants.PATHAO_USERNAME
        self.password = constants.PATHAO_PASSWORD

        self.routes : routes.PathaoRoutes = routes.PathaoRoutes(self.base_url)
        self.access_token = None
        self.refresh_token = None

        # Initial token fetch
        data = controllers.issue_access_token(self.routes.ISSUE_TOKEN, args={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": self.username,
            "password": self.password
        })
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

    # -----------------------------
    # Internal helper
    # -----------------------------
    def _call_with_token_refresh(self, func, *args, **kwargs):
        """
        Call a controller function with the current access_token.
        If UnauthorizedError (401) occurs, refresh token and retry once.
        """
        try:
            return func(*args, **kwargs, token=self.access_token)
        except controllers.UnauthorizedError:
            # Refresh token
            print("Unauthorized. Getting new token")
            data = controllers.issue_access_token(self.routes.ISSUE_TOKEN, args={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "password",
                "username": self.username,
                "password": self.password
            })
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            # Retry once
            return func(*args, **kwargs, token=self.access_token)

    # -----------------------------
    # API Methods
    # -----------------------------
    def get_city_list(self):
        return self._call_with_token_refresh(controllers.get_city_list, self.routes.CITY_LIST)
    
    def get_zone_list(self, city_id=None):
        if not city_id:
            raise Exception("Must provide a city id")
        return self._call_with_token_refresh(controllers.get_zone_list, self.routes.ZONE_LIST(city_id))
    
    def get_area_list(self, zone_id=None):
        if not zone_id:
            raise Exception("Must provide a zone id")
        return self._call_with_token_refresh(controllers.get_area_list, self.routes.AREA_LIST(zone_id))

    def get_delivery_charge(self, city_id, zone_id, item_type:int=2, delivery_type:int=48, item_weight:float=0.5):
        if not zone_id or not city_id:
            raise Exception("Both zone id and city id are required")
        payload = {
            "store_id": self.store_id,
            "item_type": item_type,
            "delivery_type": delivery_type,
            "item_weight": f"{item_weight}",
            "recipient_city": city_id,
            "recipient_zone": zone_id
        }
        return self._call_with_token_refresh(controllers.get_price_plan, self.routes.PRICE_PLAN, payload=payload)

    def get_stores(self):
        return self._call_with_token_refresh(controllers.get_stores_info, self.routes.STORES_INFO)
    
    def create_order(self, order_id:str, recipient_name:str, recipient_phone:str, recipient_address:str,
                     item_quantity:int, amount_to_collect:int, delivery_type:int=48, item_type:int=2,
                     special_instruction:str="", item_weight:float=0.5, item_description:str=''):
        payload = {
            "store_id": self.store_id,
            "merchant_order_id": order_id,
            "recipient_name": recipient_name,
            "recipient_phone": recipient_phone,
            "recipient_address": recipient_address,
            "delivery_type": delivery_type,
            "item_type": item_type,
            "special_instruction": special_instruction,
            "item_quantity": item_quantity,
            "item_weight": f"{item_weight}",
            "item_description": item_description,
            "amount_to_collect": amount_to_collect
        }
        return self._call_with_token_refresh(controllers.create_order, self.routes.CREATE_ORDER, payload=payload)