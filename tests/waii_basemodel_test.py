import unittest
import pytest
from typing import Optional, List

from waii_sdk_py.my_pydantic import WaiiBaseModel

class ABaseModel(WaiiBaseModel):
    attr_a: int
    attr_b: float
    attr_c: str

class BBaseModel(WaiiBaseModel):
    attr_a: ABaseModel
    attr_b: int

class CBaseModel(BBaseModel):
    attr_c: int
    attr_d: ABaseModel

class DBaseModel(WaiiBaseModel):
    attr_a: int
    attr_b: List[ABaseModel]
    attr_c: Optional[CBaseModel] = None


class TestWaiiBaseModel(unittest.TestCase):
    def test_extra_field(self):    
        # allows to add unknown attributes at init
        model_a = ABaseModel(attr_a=2, attr_b=3.3, attr_c='val', attr_unknown='unknown')
        with pytest.raises(ValueError):
            # should raise exception only when check_extra_fields() is called
            model_a.check_extra_fields()
        
        model_b = ABaseModel(attr_a=2, attr_b=3.3, attr_c='val')
        # should not raise exception
        model_b.check_extra_fields()
    
    def test_extra_field_recursive(self):
        model_a = ABaseModel(attr_a=2, attr_b=3.3, attr_c='val', attr_unknown='unknown')
        model_b = BBaseModel(attr_a=model_a, attr_b=3)

        # both models should raise exceptions
        with pytest.raises(ValueError):
            model_b.check_extra_fields()
        with pytest.raises(ValueError):
            model_a.check_extra_fields()
    
    def test_extra_field_kwargs(self):
        # kwargs
        model_c = ABaseModel(**{'attr_a':2, 'attr_b':3.3, 'attr_c':'val', 'attr_d':'new_val'})
        with pytest.raises(ValueError):
            model_c.check_extra_fields()
    
    def test_extra_field_subclass(self):
        model_a = ABaseModel(attr_a=2, attr_b=3.3, attr_c='val')
        # invalid model
        model_a_inv = ABaseModel(attr_a=2, attr_b=3.3, attr_c='val', unknown='unknown')
        model_c = CBaseModel(attr_a=model_a, attr_b=3, attr_c=4, attr_d=model_a_inv)

        with pytest.raises(ValueError):
            model_c.check_extra_fields()


        model_c = CBaseModel(attr_a=model_a, attr_b=3, attr_c=4, attr_d=model_a)
        # should not raise exception since all attributes are recursively correct
        model_c.check_extra_fields()
    
    def test_extra_field_list(self):
        model_d = DBaseModel(
            attr_a=2,
            attr_b=[
                ABaseModel(attr_a=2, attr_b=3.3, attr_c='a'),
                # invalid
                ABaseModel(attr_a=2, attr_b=3.3, attr_c='val', unknown='unknown')
            ],
        )

        with pytest.raises(ValueError):
            model_d.check_extra_fields()
    
    def test_extra_field_optional(self):
        model_d = DBaseModel(
            attr_a=2,
            attr_b=[
                ABaseModel(attr_a=2, attr_b=3.3, attr_c='a'),
                ABaseModel(attr_a=2, attr_b=3.3, attr_c='val')
            ],
            attr_c=CBaseModel(
                attr_a=ABaseModel(attr_a=2, attr_b=3.3, attr_c='a'),
                attr_b=2, attr_c=3,
                # invalid
                attr_d=ABaseModel(attr_a=2, attr_b=3.3, attr_c='v', unknown='unknown')
            )
        )

        with pytest.raises(ValueError):
            model_d.check_extra_fields()


if __name__ == '__main__':
    unittest.main()