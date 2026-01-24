try:
    with open("Fabrika_Yönetimi.py", encoding='utf-8') as f:
        code = f.read()
    exec(code)
except FileNotFoundError:
    print("Error: Fabrika_Yönetimi.py not found.")
