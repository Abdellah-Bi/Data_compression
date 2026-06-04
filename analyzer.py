import os
import json
from collections import Counter

def mine_python_patterns(directory_path, top_n=768, max_pattern_len=12):
    patterns = Counter()
    
    if not os.path.exists(directory_path):
        print(f"Error: Path {directory_path} does not exist.")
        return []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for length in range(2, max_pattern_len + 1):
                        for i in range(len(content) - length + 1):
                            pattern = content[i:i+length]
                            if pattern.strip():
                                patterns[pattern] += 1
    
    most_valuable = sorted(patterns.items(), key=lambda x: len(x[0]) * x[1], reverse=True)
    
    return [p[0] for p in most_valuable[:top_n]]

if __name__ == "__main__":
    source_path = "./requests/src/requests" 
    
    print(f"Phase 1: Mining patterns from {source_path}...")
    common_patterns = mine_python_patterns(source_path)
    
    if common_patterns:
        with open("seed_dictionary.json", "w", encoding="utf-8") as f:
            json.dump(common_patterns, f)
            
        print(f"Success! {len(common_patterns)} patterns saved to seed_dictionary.json")
    else:
        print("No patterns were found. Please check your source_path.")