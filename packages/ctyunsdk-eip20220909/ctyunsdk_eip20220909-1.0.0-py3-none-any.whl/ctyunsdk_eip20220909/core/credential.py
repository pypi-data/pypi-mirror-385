import os
from typing import Optional

class Credential:
    """认证信息"""
    
    def __init__(self, ak: Optional[str] = None, sk: Optional[str] = None):
        self.ak = ak
        self.sk = sk
        
        if not (self.ak and self.sk):
            self._load_from_env()
    
    def _load_from_env(self) -> None:
        """从测试类获取认证信息"""
        if hasattr(self, 'ak') and hasattr(self, 'sk'):
            return
            
        raise ValueError("Please provide credentials when initializing Credential class")
        
        if not (self.ak and self.sk):
            raise ValueError("Credentials not found in environment variables")
    
    @classmethod
    def from_env(cls) -> 'Credential':
        """从环境变量创建认证信息"""
        return cls()