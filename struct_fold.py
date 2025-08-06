# import os
# from pathlib import Path

# def generate_project_tree(start_path='.', max_depth=5, indent='    '):
#     """
#     Generate a tree structure of your project files
#     :param start_path: Root directory to scan
#     :param max_depth: Maximum folder depth to display
#     :param indent: Indentation string
#     """
#     start_path = Path(start_path)
#     print(f"Project Structure: {start_path.resolve()}")
    
#     for root, dirs, files in os.walk(start_path):
#         level = root.replace(str(start_path), '').count(os.sep)
#         if level > max_depth:
#             continue
            
#         # Skip virtual environments and cache folders
#         if 'venv' in dirs or '.venv' in dirs:
#             dirs.remove('venv') if 'venv' in dirs else dirs.remove('.venv')
#         if '__pycache__' in dirs:
#             dirs.remove('__pycache__')
            
#         # Print current directory
#         indent_str = indent * level
#         print(f"{indent_str}{os.path.basename(root)}/")
        
#         # Print files
#         sub_indent = indent * (level + 1)
#         for f in files:
#             if not f.endswith(('.pyc', '.pyo')):
#                 print(f"{sub_indent}{f}")

# if __name__ == "__main__":
#     print("\n" + "="*50)
#     print("JARVIS Project Structure")
#     print("="*50 + "\n")
#     generate_project_tree()
#     print("\n" + "="*50)