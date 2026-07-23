import os

print("Current directory:", os.getcwd())
print("\nFiles in current directory:")
for item in os.listdir('.'):
    print(f"  {item}")

print("\nChecking templates folder:")
if os.path.exists('templates'):
    print("  ✅ templates folder exists")
    print("  Files:", os.listdir('templates'))
else:
    print("  ❌ templates folder NOT found")

print("\nChecking app/templates folder:")
if os.path.exists('app/templates'):
    print("  ✅ app/templates exists")
    print("  Files:", os.listdir('app/templates'))
else:
    print("  ❌ app/templates NOT found")

print("\nChecking app/static folder:")
if os.path.exists('app/static'):
    print("  ✅ app/static exists")
else:
    print("  ❌ app/static NOT found")
