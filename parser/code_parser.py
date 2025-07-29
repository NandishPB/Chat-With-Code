import re
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class CodeChunk:
    function_name : str
    function_body : str
    comments : str
    file_path : str
    line_start : int
    line_end : int
    chunk_type : str = "function"

class SimpleCppParser:

    def __init__(self):
        self.function_pattern = re.compile(
            r'((?:/\*.*?\*/|//.*?\n)*)\s*'  # Comments before function (group 1)
            r'(?:(?:inline|static|extern|virtual|friend)\s+)*'  # Optional modifiers
            r'([a-zA-Z_]\w*(?:\s*\*)*\s+)'  # Return type (group 2)
            r'([a-zA-Z_]\w*)\s*'  # Function name (group 3)
            r'\([^{]*?\)\s*'  # Parameters
            r'(\{)',
            re.MULTILINE | re.DOTALL
        )

    def find_matching_brace(self, code: str, start_pos : int) -> int:
        brace_count = 1
        pos = start_pos + 1

        while pos < len(code) and brace_count > 0:
            char = code[pos]
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            pos += 1
        
        return pos -1 if brace_count == 0 else -1
    
    def extract_functions(self, code: str, file_path : str)-> List[CodeChunk]:
        chunks = []
        lines = code.split('\n')

        for match in self.function_pattern.finditer(code):
            comments = match.group(1).strip() if match.group(1) else ""
            return_type = match.group(2).strip()
            function_name = match.group(3).strip()

            brace_start = match.end()-1 
            brace_end = self.find_matching_brace(code, brace_start)

            if brace_end == -1:
                continue

            function_start = match.start()
            full_function = code[function_start:brace_end + 1]

            line_start = code[:function_start].count('\n') + 1
            line_end = code[:brace_end + 1].count('\n') + 1

            clean_comments = re.sub(r'/\*|\*/|//','', comments).strip()

            chunk = CodeChunk(
                function_name = function_name,
                function_body = full_function,
                comments = clean_comments,
                file_path = file_path,
                line_start = line_start,
                line_end = line_end
            )

            chunks.append(chunk)
        return chunks
    
    def parse_file(self, file_path: str) -> List[CodeChunk]:

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

            return self.extract_function(code, file_path)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
        
    def parse_directory(self, directory: str)-> List[CodeChunk]:

        all_chunks = []
        c_extensions = ['.c','.cpp', '.cc', '.cxx', '.h', '.hpp']

        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in c_extensions):
                    file_path = os.path.join(root, file)
                    chunks = self.parse_file(file_path)
                    all_chunks.extend(chunks)
                    print(f"Parsed {len(chunks)} functions from {file_path}")

        return all_chunks

if __name__ == "__main__":
    test_code = '''
    #include<iostream>

    int add(int a , int b){
        return a + b;
    }

    int factorial(int n) {
        if(n <= 1) {
            return 1;
        }
        return n * factorial(n-1);
    }

    void printHello() {
        std::cout << "Hello, World!" << std::endl;
    }
    '''

    with open('test.cpp', 'w') as f:
        f.write(test_code)

    parser = SimpleCppParser()
    chunks = parser.parse_file('test.cpp')

    print(f"Found {len(chunks)} funcitons:")
    for chunk in chunks:
        print(f"- {chunk.function_name} (lines {chunk.line_start}-{chunk.line_end})")
        if chunk.comments:
            print(f" Comments: {chunk.comments}")

    os.remove('test.cpp')      