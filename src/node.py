class Node:
    def __init__(self, ordering_index: int, variable_index: int, left: int, right: int, variable_name: str) -> None:
        self.index = ordering_index
        self.variable_index = variable_index
        self.edges = [left, right]
        self.variable_name = variable_name
    
    def __str__(self) -> str:
        # return f"Node_{self.index:{' '}{'<'}{5}} Left: {self.edges[0]} \
        #   Right: {self.edges[1]} VarIndex: \"{self.variable_index:{' '}{'<'}{2}}\" \
        #     VarName: \"{self.variable_name:{' '}{'<'}{3}}"
        return f"Node_{self.variable_name if self.variable_name else ''}_{self.index}"

    def __repr__(self) -> str:
        return self.__str__()