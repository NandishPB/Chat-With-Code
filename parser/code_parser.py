from tree_sitter_language_pack import get_language, get_parser
from tree_sitter import Parser

C_LANGUAGE = get_language("c")
CPP_LANGUAGE = get_language("cpp")

def extract_functions_from_file(filepath, language="c"):
    lang = C_LANGUAGE if language == "c" else CPP_LANGUAGE

    parser = Parser()
    parser.set_language(lang)

    with open(filepath,'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()

    tree = parser.parse(bytes(code,"utf8"))
    functions = []
    
    for node in tree.root_node.walk():
        if node.type == "function_definition":
            start, _ = node.start_point
            end, _ = node.end_point
            lines = code.splitlines()
            functions.append("\n".join(lines[start:end+1]))
    return functions

if __name__ == "__main__":
    test_file = "../data/lprint/lprint-brother.c"
    funcs = extract_functions_from_file(test_file, language="c")
    print(f"Extracted {len(funcs)} functions.")