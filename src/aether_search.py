import os
import json
import re
import sys
from pypdf import PdfReader

VAULT_DIR = os.path.expanduser("~/.aether_vault")
INDEX_FILE = os.path.join(VAULT_DIR, "search_index.json")
TARGET_DIRS = [
    os.path.join(VAULT_DIR, "10_GATE_Prep"),
    os.path.join(VAULT_DIR, "20_College_Academics")
]

def extract_pdf_text(path):
    try:
        reader = PdfReader(path)
        text = ""
        max_pages = min(len(reader.pages), 20)
        for i in range(max_pages):
            text += reader.pages[i].extract_text() or ""
        return text
    except Exception as e:
        return ""

def extract_text(path):
    _, ext = os.path.splitext(path.lower())
    if ext == ".pdf":
        return extract_pdf_text(path)
    elif ext in [".txt", ".md", ".py", ".json", ".js", ".ts", ".html"]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""
    return ""

def build_index():
    print("Indexing academic documents & study notes...")
    index = {}
    total_indexed = 0
    
    for base_dir in TARGET_DIRS:
        if not os.path.exists(base_dir):
            continue
            
        print(f"Scanning: {os.path.basename(base_dir)}...")
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in ["node_modules", "venv", ".venv", ".git"] and not d.startswith('.')]
            
            for f in files:
                if f.startswith('.'):
                    continue
                file_path = os.path.join(root, f)
                rel_path = os.path.relpath(file_path, VAULT_DIR)
                
                try:
                    if os.path.getsize(file_path) > 15 * 1024 * 1024:
                        continue
                except:
                    continue
                    
                text = extract_text(file_path)
                if text:
                    clean_text = re.sub(r'\s+', ' ', text.lower())
                    index[rel_path] = {
                        "name": f,
                        "text": clean_text
                    }
                    total_indexed += 1
                    
    try:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        print(f"SUCCESS: Search index updated. {total_indexed} documents indexed.")
    except Exception as e:
        print(f"Error saving search index: {str(e)}", file=sys.stderr)

def search_index(query):
    if not os.path.exists(INDEX_FILE):
        print("Search index not found. Building index first...")
        build_index()
        if not os.path.exists(INDEX_FILE):
            return
            
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index = json.load(f)
    except Exception as e:
        print(f"Error reading index file: {str(e)}", file=sys.stderr)
        return
        
    query_terms = query.lower().split()
    results = []
    
    for rel_path, data in index.items():
        text = data["text"]
        name = data["name"]
        
        score = 0
        snippet = ""
        matches = 0
        for term in query_terms:
            count = text.count(term)
            if count > 0:
                score += count
                matches += 1
                
        if score > 0:
            first_term = query_terms[0]
            pos = text.find(first_term)
            if pos != -1:
                start = max(0, pos - 80)
                end = min(len(text), pos + 120)
                snippet = "..." + text[start:end].replace('\n', ' ').strip() + "..."
                
            results.append({
                "rel_path": rel_path,
                "name": name,
                "score": score,
                "matches": matches,
                "snippet": snippet
            })
            
    results.sort(key=lambda x: (x["matches"], x["score"]), reverse=True)
    
    print(f"\n--- Search Results for '{query}' (Found {len(results)} matches) ---\n")
    if not results:
        print("No matches found.")
        return
        
    for r in results[:5]:
        print(f"\033[1;34m{r['name']}\033[0m  (Score: {r['score']}, Terms Matched: {r['matches']}/{len(query_terms)})")
        print(f"Path: file://{VAULT_DIR}/{r['rel_path']}")
        if r['snippet']:
            highlighted = r['snippet']
            for term in query_terms:
                highlighted = re.sub(
                    re.escape(term), 
                    f"\033[1;33m{term}\033[0m", 
                    highlighted, 
                    flags=re.IGNORECASE
                )
            print(f"Snippet: {highlighted}")
        print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "index":
            build_index()
        elif cmd == "ask":
            if len(sys.argv) > 2:
                search_index(" ".join(sys.argv[2:]))
            else:
                print("Error: Please provide a search query.")
        else:
            print(f"Error: Unknown command '{cmd}'")
    else:
        print("Usage: python3 aether_search.py [index|ask] [query]")
