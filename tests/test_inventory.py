# tests/test_inventory.py
import pytest
from inventory import Inventory


# ==============================================================================
# ขั้นที่ 2: TDD สำหรับเมธอด low_stock_items(threshold) (6 กรณี)
# ==============================================================================

def test_low_stock_all_items_above_threshold():
    """กรณีที่ 1: สินค้าทุกรายการมีจำนวนมากกว่า threshold -> คืน list ว่าง"""
    inv = Inventory()
    inv.add_item("Apple", 10, 20.0)
    inv.add_item("Banana", 15, 10.0)
    
    result = inv.low_stock_items(threshold=5)
    assert result == []


def test_low_stock_item_exactly_equal_threshold():
    """กรณีที่ 2: มีสินค้าที่จำนวนเท่ากับ threshold พอดี -> ต้องถูกนับรวมด้วย"""
    inv = Inventory()
    inv.add_item("Apple", 5, 20.0)
    inv.add_item("Banana", 10, 10.0)
    
    result = inv.low_stock_items(threshold=5)
    assert result == ["Apple"]


def test_low_stock_multiple_items_sorted_by_name():
    """กรณีที่ 3: มีสินค้าเข้าเกณฑ์หลายรายการ -> ผลลัพธ์เรียงตามชื่อ ไม่ใช่ตามลำดับที่เพิ่ม"""
    inv = Inventory()
    # เพิ่มตามลำดับ: Orange -> Banana -> Apple
    inv.add_item("Orange", 3, 15.0)
    inv.add_item("Banana", 2, 10.0)
    inv.add_item("Apple", 4, 25.0)
    
    result = inv.low_stock_items(threshold=4)
    # ต้องเรียงตามตัวอักษร: Apple -> Banana -> Orange
    assert result == ["Apple", "Banana", "Orange"]


def test_low_stock_empty_inventory():
    """กรณีที่ 4: คลังว่าง -> คืน list ว่าง ไม่ใช่ error"""
    inv = Inventory()
    result = inv.low_stock_items(threshold=10)
    assert result == []


def test_low_stock_threshold_zero():
    """กรณีที่ 5: threshold เป็น 0 -> คืนเฉพาะสินค้าที่เหลือ 0"""
    inv = Inventory()
    inv.add_item("InStock", 5, 10.0)
    inv.add_item("ZeroStock", 0, 15.0)
    
    result = inv.low_stock_items(threshold=0)
    assert result == ["ZeroStock"]


def test_low_stock_negative_threshold():
    """กรณีที่ 6: threshold ติดลบ -> ตัดสินใจคืน list ว่าง เนื่องจากสินค้าไม่สามารถติดลบได้"""
    inv = Inventory()
    inv.add_item("Apple", 0, 10.0)
    inv.add_item("Banana", 5, 15.0)
    
    result = inv.low_stock_items(threshold=-1)
    assert result == []
