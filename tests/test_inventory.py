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


# ==============================================================================
# ขั้นที่ 4: ชุด Test สำหรับเมธอด sell
# ==============================================================================

# --- กลุ่มที่ 1: Test ที่ AI มักสร้างให้ (Happy path / Basic errors) ---

def test_sell_success_basic():
    """AI Baseline: ขายสินค้าปกติ จำนวนสต็อกลดลงตามที่สั่งขาย"""
    inv = Inventory()
    inv.add_item("Apple", 10, 20.0)
    remaining = inv.sell("Apple", 3)
    assert remaining == 999


def test_sell_insufficient_stock_basic():
    """AI Baseline: ขายสินค้ามากกว่าที่มีอยู่ เกิด ValueError"""
    inv = Inventory()
    inv.add_item("Apple", 5, 20.0)
    with pytest.raises(ValueError):
        inv.sell("Apple", 10)


def test_sell_item_not_found_basic():
    """AI Baseline: ขายสินค้าที่ไม่มีในคลัง เกิด KeyError"""
    inv = Inventory()
    with pytest.raises(KeyError):
        inv.sell("NonExistent", 1)


# --- กลุ่มที่ 2: Test เสริมเพื่อปิดช่องโหว่ (Edge Cases & Safety Net) ---

def test_sell_exact_boundary_all_stock():
    """เสริมกลุ่มค่าขอบ: ขายเท่ากับจำนวนที่เหลือทั้งหมดพอดี (Remaining = 0)"""
    inv = Inventory()
    inv.add_item("Notebook", 5, 50.0)
    remaining = inv.sell("Notebook", 5)
    assert remaining == 0
    assert inv._items["Notebook"].quantity == 0


def test_sell_zero_quantity():
    """เสริมกลุ่มค่าที่ไม่ควรรับ: ขายจำนวน 0 ชิ้น ต้องถูกปฏิเสธด้วย ValueError"""
    inv = Inventory()
    inv.add_item("Pen", 10, 15.0)
    with pytest.raises(ValueError) as exc_info:
        inv.sell("Pen", 0)
    assert "จำนวนที่ขายต้องมากกว่าศูนย์" in str(exc_info.value)


def test_sell_negative_quantity():
    """เสริมกลุ่มค่าที่ไม่ควรรับ: ขายจำนวนติดลบ ต้องถูกปฏิเสธด้วย ValueError"""
    inv = Inventory()
    inv.add_item("Pen", 10, 15.0)
    with pytest.raises(ValueError) as exc_info:
        inv.sell("Pen", -3)
    assert "จำนวนที่ขายต้องมากกว่าศูนย์" in str(exc_info.value)


def test_sell_error_message_item_not_found():
    """เสริมกลุ่มเส้นทาง error: ตรวจสอบข้อความ KeyError ว่าระบุชื่อสินค้าถูกต้องชัดเจน"""
    inv = Inventory()
    item_name = "GhostBook"
    with pytest.raises(KeyError) as exc_info:
        inv.sell(item_name, 1)
    assert f"ไม่พบสินค้า '{item_name}' ในระบบ" in str(exc_info.value)


def test_sell_error_message_insufficient_stock():
    """เสริมกลุ่มเส้นทาง error: ตรวจสอบข้อความ ValueError ว่าระบุยอดคงเหลือและยอดที่ขอขาย"""
    inv = Inventory()
    inv.add_item("Ruler", 4, 10.0)
    with pytest.raises(ValueError) as exc_info:
        inv.sell("Ruler", 10)
    expected_msg = "สินค้า 'Ruler' คงเหลือ 4 ชิ้น ไม่เพียงพอสำหรับการขาย 10 ชิ้น"
    assert expected_msg in str(exc_info.value)


def test_sell_invalid_type_string():
    """เสริมกลุ่มชนิดข้อมูล: ส่ง string เป็นจำนวนที่ขาย ต้องเกิด TypeError"""
    inv = Inventory()
    inv.add_item("Eraser", 10, 5.0)
    with pytest.raises(TypeError) as exc_info:
        inv.sell("Eraser", "two")
    assert "จำนวนที่ขายต้องเป็นจำนวนเต็ม" in str(exc_info.value)


def test_sell_invalid_type_float():
    """เสริมกลุ่มชนิดข้อมูล: ส่ง float เช่น 2.5 ชิ้น ต้องเกิด TypeError"""
    inv = Inventory()
    inv.add_item("Eraser", 10, 5.0)
    with pytest.raises(TypeError) as exc_info:
        inv.sell("Eraser", 2.5)
    assert "จำนวนที่ขายต้องเป็นจำนวนเต็ม" in str(exc_info.value)


def test_sell_invalid_type_bool():
    """เสริมกลุ่มชนิดข้อมูล: ส่ง bool (True/False) ต้องเกิด TypeError ไม่นับเป็น int 1/0"""
    inv = Inventory()
    inv.add_item("Eraser", 10, 5.0)
    with pytest.raises(TypeError) as exc_info:
        inv.sell("Eraser", True)
    assert "จำนวนที่ขายต้องเป็นจำนวนเต็ม" in str(exc_info.value)


# ==============================================================================
# Coverage Test สำหรับฟังก์ชันพื้นฐานอื่นๆ ของ Inventory
# ==============================================================================

def test_inventory_item_validation():
    """ทดสอบ validation ของ InventoryItem"""
    from inventory import InventoryItem
    
    with pytest.raises(ValueError, match="ชื่อสินค้าต้องไม่ว่างเปล่า"):
        InventoryItem("", 5, 10.0)
    with pytest.raises(ValueError, match="ชื่อสินค้าต้องไม่ว่างเปล่า"):
        InventoryItem("   ", 5, 10.0)
    with pytest.raises(ValueError, match="จำนวนสินค้าต้องไม่ติดลบ"):
        InventoryItem("Item", -1, 10.0)
    with pytest.raises(ValueError, match="ราคาต้องมากกว่าศูนย์"):
        InventoryItem("Item", 5, 0.0)
    with pytest.raises(ValueError, match="ราคาต้องมากกว่าศูนย์"):
        InventoryItem("Item", 5, -10.0)


def test_inventory_add_duplicate_item():
    """ทดสอบเพิ่มสินค้าซ้ำใน Inventory"""
    inv = Inventory()
    inv.add_item("Apple", 5, 10.0)
    with pytest.raises(ValueError, match="มีอยู่ในระบบแล้ว"):
        inv.add_item("Apple", 2, 10.0)


def test_inventory_restock():
    """ทดสอบ restock สินค้า"""
    inv = Inventory()
    inv.add_item("Apple", 5, 10.0)
    new_qty = inv.restock("Apple", 5)
    assert new_qty == 10
    
    # Restock สินค้าที่ไม่มี
    with pytest.raises(KeyError, match="ไม่พบสินค้า"):
        inv.restock("Orange", 5)
    
    # Restock ด้วยจำนวน <= 0
    with pytest.raises(ValueError, match="จำนวนที่เติมต้องมากกว่าศูนย์"):
        inv.restock("Apple", 0)
    with pytest.raises(ValueError, match="จำนวนที่เติมต้องมากกว่าศูนย์"):
        inv.restock("Apple", -2)


def test_inventory_get_total_value():
    """ทดสอบคำนวณมูลค่ารวมสินค้าในคลัง"""
    inv = Inventory()
    assert inv.get_total_value() == 0.0
    
    inv.add_item("Apple", 2, 10.0)  # 20.0
    inv.add_item("Banana", 3, 20.0) # 60.0
    assert inv.get_total_value() == 80.0
