"""Phase 4 Integration Test: Finance, Payments & Reporting."""
import requests
import json

BASE = "http://localhost:8000/api/v1"


def register_and_login(username, email, password, role_id):
    r = requests.post(f"{BASE}/auth/register", json={
        "username": username, "email": email, "password": password, "role_id": role_id
    })
    r = requests.post(f"{BASE}/auth/login", data={
        "username": username, "password": password
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==================== Setup ====================
print("=== Setting up users ===")
admin_h = register_and_login("fin_admin", "finadmin@ums.edu", "pass123", 3)
faculty_h = register_and_login("dr_jones", "jones@ums.edu", "pass123", 2)
student_h = register_and_login("alice", "alice@ums.edu", "pass123", 1)
student2_h = register_and_login("bob_fin", "bobfin@ums.edu", "pass123", 1)

# Create a course
course = requests.post(f"{BASE}/courses/", json={
    "code": "FIN101", "name": "Accounting Basics",
    "latitude": 33.68, "longitude": 73.04
}, headers=faculty_h).json()
print(f"  Course: {course['name']} (id={course['id']})")

# Enroll students
requests.post(f"{BASE}/courses/{course['id']}/enroll", headers=student_h)
requests.post(f"{BASE}/courses/{course['id']}/enroll", headers=student2_h)

# ==================== Fee Structures ====================
print("\n=== Test 1: Create fee structures ===")
fee1 = requests.post(f"{BASE}/finance/fees", json={
    "course_id": course['id'], "semester": "Fall-2026",
    "fee_type": "Tuition", "amount": 50000.0,
    "description": "Semester tuition fee"
}, headers=admin_h).json()
print(f"  Fee 1: {fee1['fee_type']} = Rs.{fee1['amount']}")

fee2 = requests.post(f"{BASE}/finance/fees", json={
    "course_id": course['id'], "semester": "Fall-2026",
    "fee_type": "Lab", "amount": 5000.0,
    "description": "Lab usage charges"
}, headers=admin_h).json()
print(f"  Fee 2: {fee2['fee_type']} = Rs.{fee2['amount']}")

fee3 = requests.post(f"{BASE}/finance/fees", json={
    "semester": "Fall-2026",
    "fee_type": "Library", "amount": 2000.0,
    "description": "University library fee"
}, headers=admin_h).json()
print(f"  Fee 3: {fee3['fee_type']} = Rs.{fee3['amount']} (university-wide)")

# List fees
fees = requests.get(f"{BASE}/finance/fees", headers=admin_h).json()
print(f"  Total fee structures: {len(fees)}")

# ==================== Invoice Generation ====================
print("\n=== Test 2: Generate 1Bill invoice for Alice ===")
# Get alice's user id
alice_me = requests.get(f"{BASE}/auth/me", headers=student_h).json()
alice_id = alice_me['id']

invoice = requests.post(f"{BASE}/payments/invoices", json={
    "student_id": alice_id,
    "semester": "Fall-2026",
    "fee_structure_ids": [fee1['id'], fee2['id'], fee3['id']]
}, headers=admin_h).json()
print(f"  Consumer Number: {invoice['consumer_number']}")
print(f"  Bill Reference:  {invoice['bill_reference']}")
print(f"  Total Amount:    Rs.{invoice['total_amount']}")
print(f"  Status:          {invoice['status']}")
print(f"  Payment Link:    {invoice['payment_link']}")
print(f"  Items:           {len(invoice['items'])}")

# ==================== Public Payment Link ====================
print("\n=== Test 3: View invoice via payment link (no auth) ===")
token = invoice['payment_link'].split('/')[-1]
public = requests.get(f"{BASE}/payments/invoices/pay/{token}").json()
print(f"  Consumer Number: {public['consumer_number']}")
print(f"  Total:           Rs.{public['total_amount']}")
print(f"  Status:          {public['status']}")

# ==================== Student Views Own Invoices ====================
print("\n=== Test 4: Alice views her invoices ===")
my_inv = requests.get(f"{BASE}/payments/invoices/me", headers=student_h).json()
print(f"  Alice's invoices: {len(my_inv)}")
print(f"  Outstanding:      Rs.{my_inv[0]['total_amount'] - my_inv[0]['amount_paid']}")

# ==================== Manual Payment ====================
print("\n=== Test 5: Admin records partial cash payment (Rs.30,000) ===")
payment1 = requests.post(f"{BASE}/payments/record", json={
    "invoice_id": invoice['id'],
    "amount": 30000.0,
    "payment_method": "Cash",
    "remarks": "Partial payment at cashier"
}, headers=admin_h).json()
print(f"  Payment id={payment1['id']}, method={payment1['payment_method']}, status={payment1['status']}")

# Check invoice status
my_inv2 = requests.get(f"{BASE}/payments/invoices/me", headers=student_h).json()
print(f"  Invoice status:   {my_inv2[0]['status']}")
print(f"  Amount paid:      Rs.{my_inv2[0]['amount_paid']}")

# ==================== 1Bill Webhook ====================
print("\n=== Test 6: 1Bill webhook callback for remaining Rs.27,000 ===")
webhook_resp = requests.post(f"{BASE}/payments/webhook/1bill", json={
    "consumer_number": invoice['consumer_number'],
    "transaction_ref": "1BILL-TXN-ABC123456",
    "amount": 27000.0,
    "payment_method": "1Bill"
}).json()
print(f"  Webhook payment id={webhook_resp['id']}, ref={webhook_resp['transaction_ref']}")

# Check final status
my_inv3 = requests.get(f"{BASE}/payments/invoices/me", headers=student_h).json()
print(f"  Invoice status:   {my_inv3[0]['status']}")
print(f"  Amount paid:      Rs.{my_inv3[0]['amount_paid']}")

# ==================== Payroll ====================
print("\n=== Test 7: Create payroll for faculty ===")
faculty_me = requests.get(f"{BASE}/auth/me", headers=faculty_h).json()

payroll = requests.post(f"{BASE}/finance/payroll", json={
    "staff_id": faculty_me['id'],
    "month": "2026-05",
    "base_salary": 80000.0,
    "allowances": 15000.0,
    "deductions": 5000.0,
    "remarks": "May 2026 salary"
}, headers=admin_h).json()
print(f"  Payroll id={payroll['id']}, net_salary=Rs.{payroll['net_salary']}, status={payroll['status']}")

# Transition: Pending → Processed
pr_update = requests.put(f"{BASE}/finance/payroll/{payroll['id']}/status", json={
    "status": "Processed"
}, headers=admin_h).json()
print(f"  After processing: status={pr_update['status']}")

# Transition: Processed → Paid
pr_paid = requests.put(f"{BASE}/finance/payroll/{payroll['id']}/status", json={
    "status": "Paid"
}, headers=admin_h).json()
print(f"  After payment:    status={pr_paid['status']}")

# ==================== Analytics ====================
print("\n=== Test 8: Analytics dashboards ===")
revenue = requests.get(f"{BASE}/analytics/revenue", headers=admin_h).json()
print(f"  Revenue Summary:")
for r in revenue:
    print(f"    {r['semester']}: Invoiced=Rs.{r['total_invoiced']}, Collected=Rs.{r['total_collected']}, Outstanding=Rs.{r['total_outstanding']}")

enrollment = requests.get(f"{BASE}/analytics/enrollments", headers=admin_h).json()
print(f"  Enrollment Stats:")
for e in enrollment:
    print(f"    {e['course_name']}: {e['student_count']} students")

payroll_sum = requests.get(f"{BASE}/analytics/payroll", headers=admin_h).json()
print(f"  Payroll Summary:")
for p in payroll_sum:
    print(f"    {p['month']}: Net=Rs.{p['total_net']}, Staff={p['staff_count']}")

print("\n✅ All Phase 4 tests completed!")
