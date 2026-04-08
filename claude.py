import os

# 1. Put the prompt you want to ask Claude right here
CLAUDE_PROMPT = """
Please review the codebase above.
[Add your specific question or instructions for Claude here]
"""

OUTPUT_FILE = 'temp.txt'

# Directories and file types to ignore
EXCLUDE_DIRS = {'__pycache__', 'venv', 'data', '.git'} 
INCLUDE_EXTS = {'.py', '.md', '.yaml', '.yml', '.sh'}
INCLUDE_FILES = {'Dockerfile', 'requirements.txt'}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk('.'):
        # Skip directories we don't care about
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            # Skip this script and the output file itself
            if file == OUTPUT_FILE or file == 'compile_context.py':
                continue
                
            _, ext = os.path.splitext(file)
            
            # Check if it's a file we want to include
            if ext in INCLUDE_EXTS or file in INCLUDE_FILES:
                filepath = os.path.join(root, file)
                
                # Write a nice header so Claude knows which file it's looking at
                outfile.write(f"\n{'='*80}\n")
                outfile.write(f"FILE: {filepath}\n")
                outfile.write(f"{'='*80}\n\n")
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                        outfile.write("\n")
                except Exception as e:
                    outfile.write(f"[Error reading file: {e}]\n")

    # Append your prompt at the very end
    outfile.write(f"\n{'='*80}\n")
    outfile.write("USER PROMPT:\n")
    outfile.write(f"{'='*80}\n")
    outfile.write(CLAUDE_PROMPT + "\n")

print(f"✅ Codebase successfully compiled into {OUTPUT_FILE}!")
