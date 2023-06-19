from abc import abstractmethod

class VerificationCase:
    
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.is_SAT: bool
    
    @abstractmethod    
    def verify(self, **kwargs) -> bool:
        raise NotImplementedError("VerificationCase.verify() is not implemented.") 
    
    def set_result(self, is_SAT: bool) -> None:
        self.is_SAT = is_SAT
        
    def set_name(self, name: str) -> None:
        self.name = name
        
    def __hash__(self) -> int:
        return hash(self.name + str(self.__class__))
    
    def __str__(self) -> str:
        return f'Verification case #{self.name}'