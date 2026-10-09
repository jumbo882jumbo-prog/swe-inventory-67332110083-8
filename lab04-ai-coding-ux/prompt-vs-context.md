# Prompt Engineering vs. Context Engineering - Lab 04

การทดลองเปรียบเทียบการสั่งงาน AI Coding Assistant ระหว่าง **Prompt สั้น (ขาดบริบท)** กับ **Prompt ที่แนบ Context ครบถ้วน** เพื่อพัฒนาเมธอด `sell_many()` ให้กับคลาส `Inventory`

---

## 1. การทดลองรอบที่ 1: Prompt สั้น (Prompt Engineering เพียงอย่างเดียว ขาด Context)

### Prompt ที่ใช้สั่ง AI:
```text
เขียน function ลด stock แล้วเก็บผลไว้
```

### ผลลัพธ์ที่ AI สร้างให้ (รอบที่ 1):
```python
def reduce_stock(inventory_dict, item_name, quantity):
    if item_name in inventory_dict:
        if inventory_dict[item_name] >= quantity:
            inventory_dict[item_name] -= quantity
            return True
        else:
            print("Stock not enough")
            return False
    return False
```

### การวิเคราะห์ผลลัพธ์รอบที่ 1:
1. **ไม่เข้ากับโครงสร้างระบบเดิม (Interface Mismatch):** AI สร้างเป็นฟังก์ชันเดี่ยว (standalone function) รับพารามิเตอร์เป็น dictionary ธรรมดา แทนที่จะเป็นเมธอดในคลาส `Inventory` และไม่ได้ใช้งานอ็อบเจกต์ `InventoryItem`
2. **ไม่รองรับการทำงานหลายรายการพร้อมกัน (Batch):** ทำงานได้ทีละ 1 รายการ
3. **ไม่มีการจัดการ Exception ตามมาตรฐานเดิม:** ใช้วิธีพิมพ์ `print()` และ return boolean (`True`/`False`) แทนที่จะ raise `ValueError` หรือ `KeyError` ตามที่ระบบของ Lab 3 กำหนด
4. **ไม่มีคุณสมบัติ Atomicity / Rollback:** หากนำไปประยุกต์ใช้กับหลายรายการ แล้วรายการหลังไม่พอ จะไม่มีย้อนคืนข้อมูล

---

## 2. การทดลองรอบที่ 2: Prompt ที่แนบ Context ครบถ้วน (Context Engineering)

### Prompt ที่ใช้สั่ง AI:
```text
ปรับปรุงเมธอด sell() ของคลาส Inventory ด้านล่างให้รองรับการขายหลายรายการพร้อมกัน

[แนบโค้ด inventory.py ฉบับสมบูรณ์]:
class InventoryItem:
    def __init__(self, name: str, quantity: int, price: float): ...

class Inventory:
    def __init__(self):
        self._items: dict[str, InventoryItem] = {}
    def sell(self, name: str, amount: int) -> int: ...

ข้อกำหนด:
- เพิ่มเมธอด `sell_many(orders: dict[str, int]) -> dict[str, int]` คืนค่า `{ชื่อสินค้า: จำนวนคงเหลือ}`
- ถ้ามีรายการใดรายการหนึ่ง stock ไม่พอ หรือไม่พบสินค้า ต้อง raise Exception และต้องไม่หักสต็อกรายการใดเลย (Atomic Transaction / Rollback)
- ใช้ Exception ชนิดเดียวกับเมธอดเดิม (KeyError เมื่อไม่พบสินค้า, ValueError เมื่อจำนวนติดลบหรือสต็อกไม่พอ)
- ห้ามใช้ library ภายนอก

เกณฑ์การทดสอบ (Test cases ที่ต้องผ่าน):
1. ขายหลายรายการสำเร็จ คืนยอดคงเหลือถูกต้องครบถ้วน
2. ถ้ารายการใดรายการหนึ่งใน orders สต็อกไม่พอ ต้องไม่หักรายการแรกที่ตรวจผ่านไปแล้ว (Rollback)
```

### ผลลัพธ์ที่ AI สร้างให้ (รอบที่ 2):
```python
class Inventory:
    # ... โค้ดเดิมคงอยู่ครบถ้วน ...

    def sell_many(self, orders: dict[str, int]) -> dict[str, int]:
        """ขายหลายรายการพร้อมกันแบบ Atomic Transaction คืน {ชื่อสินค้า: จำนวนคงเหลือ}"""
        # ขั้นที่ 1: ตรวจสอบความถูกต้องล่วงหน้าทั้งหมดก่อนตัดสต็อก (Pre-validation)
        for name, amount in orders.items():
            if name not in self._items:
                raise KeyError(f"ไม่พบสินค้า '{name}' ในระบบ")
            if amount <= 0:
                raise ValueError("จำนวนที่ขายต้องมากกว่าศูนย์")
            if self._items[name].quantity < amount:
                raise ValueError(
                    f"สินค้า '{name}' คงเหลือ {self._items[name].quantity} ชิ้น "
                    f"ไม่เพียงพอสำหรับการขาย {amount} ชิ้น"
                )

        # ขั้นที่ 2: ดำเนินการตัดสต็อกจริงหลังจากผ่านการตรวจสอบครบทุกรายการแล้ว
        result: dict[str, int] = {}
        for name, amount in orders.items():
            self._items[name].quantity -= amount
            result[name] = self._items[name].quantity

        return result
```

---

## 3. สรุปเปรียบเทียบ: ผลลัพธ์สองรอบต่างกันตรงไหน และอะไรทำให้ต่างกัน?

| มิติการเปรียบเทียบ | รอบที่ 1 (สั่งสั้น ขาด Context) | รอบที่ 2 (แนบ Context ครบถ้วน) |
|---|---|---|
| **ความเข้ากันได้กับโค้ดเดิม** | ใช้ไม่ได้เลย เพราะสร้าง interface ใหม่ขัดกับระบบเดิม | สามารถนำไปวางลงในคลาส `Inventory` และใช้งานได้ทันที |
| **การจัดการ Exception** | ใช้ `print()` และคืนค่า `False` (ผิดหลัก OOP) | โยน `KeyError` และ `ValueError` ตาม Signature เดิมของระบบ |
| **คุณสมบัติ Atomicity** | ไม่มี หากตัดรายการแรกไปแล้วจะเกิด state ค้าง | มีการทำ Pre-validation ตรวจสอบก่อนตัดจริง ป้องกันข้อมูลเพี้ยน |
| **สิ่งที่ทำให้เกิดความต่าง** | **ขาด Context:** AI ไม่มีข้อมูลว่าในโปรเจกต์มีคลาสอะไรอยู่ มีกฎธุรกิจอะไร และต้องการ Output แบบไหน | **มี Context ที่ดี:** การส่งไฟล์เดิม, Signature, ชนิดของ Error, และ Test Case ทำให้ AI ทำงานอยู่ในกรอบและได้โค้ดคุณภาพสูงระดับ Production |

> **บทเรียนสำคัญ:** Prompt Engineering คือการสั่งงานให้ชัดเจน แต่ **Context Engineering คือการส่งมอบข้อมูลแวดล้อมที่จำเป็นทั้งหมด** เพื่อให้ AI เข้าใจข้อจำกัดและบริบทของโปรเจกต์ โค้ดที่มีคุณภาพไม่ได้เกิดจากการเขียน Prompt ยาวเพียงอย่างเดียว แต่เกิดจากการส่งมอบ Context ที่ถูกต้อง
