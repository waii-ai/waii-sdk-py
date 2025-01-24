from pydantic import BaseModel
from typing import List

class B(BaseModel, extra='allow'):
    a: int

class A(BaseModel, extra='allow'):
    a: int
    c: List[int]
    d: List[B]

class D(B):
    pass
# class B(A, extra='ignore'):
#     pass
a = A(a=3, c=[4], d=[B(a=2)])

print(a.__fields__)

if isinstance(a, BaseModel):
    print('yes')

c = B(a=2)
if isinstance(c, D):
    print('ahhh')