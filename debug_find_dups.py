
filename = "Fabrika_Yönetimi.py"
search_term = "Kararınızı yazın"
search_term2 = "decision_input"

try:
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    print(f"Searching in {filename} ({len(lines)} lines)...")
    
    for i, line in enumerate(lines):
        if search_term in line:
            print(f"Found '{search_term}' at line {i+1}")
        if search_term2 in line:
            print(f"Found '{search_term2}' at line {i+1}")
            
except FileNotFoundError:
    print(f"File {filename} not found.")
except Exception as e:
    print(f"Error: {e}")
