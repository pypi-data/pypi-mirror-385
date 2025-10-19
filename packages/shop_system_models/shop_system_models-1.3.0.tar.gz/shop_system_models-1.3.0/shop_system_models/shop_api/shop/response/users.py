from shop_system_models.deployment_api.users import UserModel
from typing import Optional

class UserResponseModel(UserModel):
    id: str
    is_service: bool = False
    is_blocked: bool = False
    message_thread_id: Optional[int] = None
