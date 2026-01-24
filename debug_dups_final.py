import os

filename = "Fabrika_Yönetimi.py"
search_patterns = ["st.text_area", "Kararınızı yazın", "decision_input ="]

print(f"Analyzing {filename}...")

if os.path.exists(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            for pattern in search_patterns:
                if pattern in line:
                    print(f"Line {i+1}: {line.strip()}")
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("File not found.")
