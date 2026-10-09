# Debug Log: การแก้ไขข้อผิดพลาดแบบมีหลักฐาน - Lab 04

เอกสารบันทึกกระบวนการสืบหาต้นตอของข้อผิดพลาด (Root Cause Analysis) และการแก้ไขไฟล์ `discount.py` อย่างมีหลักฐานตามกระบวนการ 5 ขั้นตอน โดยอ้างอิงผลการรันคำสั่ง `python -m pytest tests/test_discount.py -v`

---

## สรุปภาพรวมผลการทดสอบเริ่มต้น (Initial Test Run)

เมื่อรันคำสั่ง `python -m pytest tests/test_discount.py -v` พบข้อผิดพลาดดังนี้:
```text
tests/test_discount.py::test_apply_discount_basic FAILED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total FAILED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty FAILED                  [ 83%]
tests/test_discount.py::test_cheapest_n FAILED                           [100%]

========================= 4 failed, 2 passed in 0.05s =========================
```

> ⚠️ **ข้อสังเกตเรื่องกับดักที่ผู้สอนวางไว้ (Edge Case Trap):**
> ฟังก์ชัน `apply_discount` มีบั๊กในการคำนวณสูตร แต่ `test_apply_discount_zero` กลับผ่าน (`PASSED`) เพราะกรณีลด 0% คำนวณ `250.0 - 0/100 = 250.0` ซึ่งได้ผลลัพธ์บังเอิญตรงกับราคาเดิม นี่เป็นตัวอย่างชัดเจนว่า **การที่ Test ผ่านบางข้อ ไม่ได้แปลว่าฟังก์ชันทำงานถูกต้องเสมอไป**

---

## การไล่หา Root Cause ทีละข้อตามกระบวนการ 5 ขั้นตอน

### จุดที่ 1: `test_apply_discount_basic`

#### 1. Reproduce
- **คำสั่งที่ใช้รัน:** `python -m pytest tests/test_discount.py::test_apply_discount_basic -v`
- **Assertion ที่ Fail:** `assert apply_discount(100.0, 10) == 90.0`
  - ผลลัพธ์ที่ได้จริง: `99.9`
  - ผลลัพธ์ที่คาดหวัง: `90.0`

#### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 5 ในฟังก์ชัน `apply_discount`
  ```python
  return price - percent / 100
  ```

#### 3. สมมติฐาน (Hypothesis)
ฟังก์ชันคำนวณส่วนลดผิดพลาดเนื่องจากสูตรไม่ได้นำเปอร์เซ็นต์ส่วนลดไปคูณกับราคาต้นทุน (`price`) ส่งผลให้กลายเป็นการนำราคาเต็มไปลบด้วยเศษส่วนลดโดยตรง เช่น ซื้อ 100 บาท ลด 10% แทนที่จะลด 10 บาท กลับลดไปเพียง `10 / 100 = 0.1` บาท ทำให้ยอดคงเหลือกลายเป็น `99.9` บาท

#### 4. การยืนยัน (Verification)
ทดสอบคำนวณผ่าน Python Interactive Shell:
```python
>>> price = 100.0
>>> percent = 10
>>> price - percent / 100
99.9  # พิสูจน์ได้ว่าลำดับเครื่องหมายและการคำนวณผิด
>>> price * (1 - percent / 100)
90.0  # สูตรที่ถูกต้อง
```

#### 5. Root Cause และการแก้
- **สาเหตุจริง (Root Cause):** การเขียนสูตรทางคณิตศาสตร์ผิดพลาด (Operator logic error) ขาดการคูณราคาตั้งต้นก่อนคำนวณส่วนลด
- **การแก้ไข:** แก้ไขบรรทัดที่ 5 ของ `discount.py` เป็น:
  ```python
  return price * (1 - percent / 100)
  ```

---

### จุดที่ 2: `test_bulk_total`

#### 1. Reproduce
- **คำสั่งที่ใช้รัน:** `python -m pytest tests/test_discount.py::test_bulk_total -v`
- **Assertion ที่ Fail:** `assert bulk_total([100.0, 100.0, 100.0], 10) == 270.0`
  - ผลลัพธ์ที่ได้จริง: `299.9`
  - ผลลัพธ์ที่คาดหวัง: `270.0`

#### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 13 ในฟังก์ชัน `bulk_total` ซึ่งเรียกใช้งาน `apply_discount(total, discount_percent)`

#### 3. สมมติฐาน (Hypothesis)
ลอจิกการรวมราคาสินค้าใน `bulk_total` ทำงานถูกต้อง (`total = 300.0`) แต่ผลลัพธ์ล้มเหลวเพราะฟังก์ชันเรียกส่งต่อยอดรวมไปให้ `apply_discount` ซึ่งมีสูตรคำนวณเปอร์เซ็นต์ผิดพลาดจากจุดที่ 1 ทำให้ยอด 300 บาท ลด 10% กลายเป็น `300 - 0.1 = 299.9` แทนที่จะเป็น `270.0`

#### 4. การยืนยัน (Verification)
ตรวจสอบค่าตัวแปร `total` ก่อนส่งเข้าฟังก์ชัน:
```python
print(f"DEBUG total: {total}") # แสดงผลเป็น 300.0 ถูกต้อง
```
เมื่อจำลองการเรียก `apply_discount(300.0, 10)` ด้วยสูตรที่แก้แล้วในจุดที่ 1 ได้ผลลัพธ์เป็น `270.0` ทันที

#### 5. Root Cause และการแก้
- **สาเหตุจริง (Root Cause):** เกิด Ripple Effect จากฟังก์ชัน `apply_discount()` ที่มีบั๊ก เมื่อฟังก์ชันต้นทางได้รับการแก้ไข ตัวฟังก์ชัน `bulk_total()` ก็จะทำงานได้อย่างถูกต้องโดยไม่ต้องแก้ไขโค้ดเพิ่มเติม

---

### จุดที่ 3: `test_average_price_empty`

#### 1. Reproduce
- **คำสั่งที่ใช้รัน:** `python -m pytest tests/test_discount.py::test_average_price_empty -v`
- **Assertion / Exception ที่ Fail:**
  ```text
  ZeroDivisionError: division by zero
  ```

#### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 18 ในฟังก์ชัน `average_price`
  ```python
  return sum(prices) / len(prices)
  ```

#### 3. สมมติฐาน (Hypothesis)
ฟังก์ชันไม่ได้ตรวจสอบกรณีที่ลิสต์ `prices` ว่างเปล่า (`[]`) ส่งผลให้ `len(prices)` มีค่าเท่ากับ 0 เมื่อนำไปเป็นตัวหารในภาษา Python จึงเกิดข้อยกเว้น `ZeroDivisionError` แทนที่จะคืนค่า `0.0` ตามข้อกำหนดของการจัดการคลังสินค้า

#### 4. การยืนยัน (Verification)
ทดสอบส่งลิสต์ว่างเข้าฟังก์ชัน:
```python
>>> prices = []
>>> len(prices)
0
>>> sum(prices) / len(prices)
Traceback (most recent call last):
  ...
ZeroDivisionError: division by zero
```

#### 5. Root Cause และการแก้
- **สาเหตุจริง (Root Cause):** ขาด Guard Clause / Defensive Check ในการรับมือกับ Edge Case ข้อมูลลิสต์ว่าง
- **การแก้ไข:** เพิ่มการตรวจสอบเงื่อนไขที่บรรทัดเริ่มต้นของฟังก์ชัน `average_price`:
  ```python
  def average_price(prices: list) -> float:
      """คืนราคาเฉลี่ยของรายการสินค้า"""
      if not prices:
          return 0.0
      return sum(prices) / len(prices)
  ```

---

### จุดที่ 4: `test_cheapest_n`

#### 1. Reproduce
- **คำสั่งที่ใช้รัน:** `python -m pytest tests/test_discount.py::test_cheapest_n -v`
- **Assertion ที่ Fail:** `assert cheapest_n([50.0, 10.0, 30.0, 20.0], 2) == [10.0, 20.0]`
  - ผลลัพธ์ที่ได้จริง: `[20.0]`
  - ผลลัพธ์ที่คาดหวัง: `[10.0, 20.0]`

#### 2. Traceback
- **ไฟล์และบรรทัดที่เกิดปัญหา:** `discount.py` บรรทัดที่ 24 ในฟังก์ชัน `cheapest_n`
  ```python
  ordered = sorted(prices)
  return ordered[1:n]
  ```

#### 3. สมมติฐาน (Hypothesis)
การตัดช่วงข้อมูล (List slicing) เขียนผิดขอบเขตเป็น `ordered[1:n]` โดยผู้เขียนสับสนการนับดัชนีแบบ 1-based index (คิดว่าตัวแรกคือ index 1) ซึ่งใน Python ลิสต์เริ่มต้นที่ดัชนี 0 ส่งผลให้ตัวเลขที่น้อยที่สุดตัวแรกสุด (`ordered[0]`) ถูกตัดทิ้งไป และการตัดช่วง `[1:2]` ส่งคืนสมาชิกเพียง 1 ตัวแทนที่จะเป็น 2 ตัว

#### 4. การยืนยัน (Verification)
ทดลองใน Python Shell:
```python
>>> prices = [50.0, 10.0, 30.0, 20.0]
>>> ordered = sorted(prices)
>>> ordered
[10.0, 20.0, 30.0, 50.0]
>>> ordered[1:2]
[20.0]        # ผิด ขาด 10.0
>>> ordered[:2]
[10.0, 20.0]  # ถูกต้อง
```

#### 5. Root Cause และการแก้
- **สาเหตุจริง (Root Cause):** Off-by-one / Wrong slicing index error
- **การแก้ไข:** แก้ไขการ Slice ให้เริ่มจาก index 0:
  ```python
  return ordered[:n]
  ```

---

## สรุปตารางการ Debugging ทั้งหมด

| test ที่ไม่ผ่าน | traceback หรือ assertion ที่เห็น | สมมติฐาน root cause | วิธีการยืนยัน | การแก้ |
|---|---|---|---|---|
| `test_apply_discount_basic` | `assert 99.9 == 90.0` (tests/test_discount.py:8) | คำนวณสูตรผิด `price - percent/100` ไม่ได้คูณกับราคาเดิม | ทดสอบพิมพ์สูตรใน shell พบได้ 99.9 แทน 90.0 | แก้เป็น `return price * (1 - percent / 100)` |
| `test_bulk_total` | `assert 299.9 == 270.0` (tests/test_discount.py:18) | รับผลกระทบจากบั๊กของฟังก์ชัน `apply_discount` | ตรวจสอบยอดรวมพบ 300 ถูกต้อง แต่ฟังก์ชันย่อยส่งค่าผิด | ผ่านอัตโนมัติเมื่อแก้ `apply_discount` |
| `test_average_price_empty` | `ZeroDivisionError: division by zero` (discount.py:18) | ไม่ดักจับกรณีลิสต์ราคาว่าง ทำให้ตัวหารเป็น 0 | ส่ง `[]` เข้าทดสอบ พบ exception เกิดขึ้นจริง | เพิ่มเงื่อนไข `if not prices: return 0.0` |
| `test_cheapest_n` | `assert [20.0] == [10.0, 20.0]` (tests/test_discount.py:33) | Slicing ผิดช่วง `[1:n]` ทำให้สมาชิกตัวแรกที่ถูกที่สุดหลุดหายไป | ทดสอบ Slice พบดัชนี 0 ตกหล่น | แก้เป็น `return ordered[:n]` |

---

## ผลการรันหลังการแก้ไขโค้ด (Final Test Verification)

คำสั่ง: `python -m pytest tests/test_discount.py -v`
```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\uuuu\Desktop\lab 4\swe-inventory-67332110083-8\lab04-ai-coding-ux
collected 6 items

tests/test_discount.py::test_apply_discount_basic PASSED                 [ 16%]
tests/test_discount.py::test_apply_discount_zero PASSED                  [ 33%]
tests/test_discount.py::test_bulk_total PASSED                           [ 50%]
tests/test_discount.py::test_average_price PASSED                        [ 66%]
tests/test_discount.py::test_average_price_empty PASSED                  [ 83%]
tests/test_discount.py::test_cheapest_n PASSED                           [100%]

============================== 6 passed in 0.04s ==============================
```
**ผลลัพธ์:** การทดสอบผ่านครบ 100% ทุกกรณีทดสอบ (6 passed)
