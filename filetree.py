# create your filetree with `python ./filetree.py input_dir output_file`. The output html page lets you copy the filetree to a clipboard. 
import os
import sys

def load_gitignore(directory):
    gitignore_path = os.path.join(directory, '.gitignore')
    if not os.path.exists(gitignore_path):
        return []
    with open(gitignore_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if pattern in path:
            return True
    return False

def generate_file_tree_html(directory_path, output_file_path):
    ignore_patterns = load_gitignore(directory_path)
    ignore_patterns.append('.git')

    def generate_html(directory, level=0):
        html = ""
        indent = " " * (level * 4)
        items = sorted(os.listdir(directory), key=lambda x: (not os.path.isdir(os.path.join(directory, x)), x.lower()))
        for item in items:
            item_path = os.path.join(directory, item)
            if is_ignored(item_path, ignore_patterns):
                continue
            if os.path.isdir(item_path):
                html += f'{indent}<li><span class="caret closed-folder">{item}</span>\n{indent}<ul class="nested">\n'
                html += generate_html(item_path, level + 1)
                html += f'{indent}</ul>\n{indent}</li>\n'
            else:
                html += f'{indent}<li>{item}</li>\n'
        return html

    def generate_ascii_tree(directory, prefix="", include_contents=True):
        ascii_tree = ""
        items = sorted(os.listdir(directory), key=lambda x: (not os.path.isdir(os.path.join(directory, x)), x.lower()))
        for index, item in enumerate(items):
            item_path = os.path.join(directory, item)
            if is_ignored(item_path, ignore_patterns):
                continue
            connector = "├── " if index < len(items) - 1 else "└── "
            if os.path.isdir(item_path):
                ascii_tree += f'{prefix}{connector}{item}\n'
                if include_contents:
                    ascii_tree += generate_ascii_tree(item_path, prefix + ("│   " if index < len(items) - 1 else "    "), include_contents)
            else:
                ascii_tree += f'{prefix}{connector}{item}\n'
        return ascii_tree

    html_content = f"""
    <!DOCTYPE html>
        <meta charset="UTF-8">

    <html>
    <head>
        <title>File Tree</title>
        <style>
            ul {{
                list-style-type: none;
            }}
            .caret {{
                cursor: pointer;
                user-select: none;
            }}
            .caret::before {{
                content: "\\1F4C1"; /* Closed folder symbol */
                color: black;
                display: inline-block;
                margin-right: 6px;
            }}
            .caret-down::before {{
                content: "\\1F4C2"; /* Open folder symbol */
            }}
            .nested {{
                display: none;
            }}
            .active {{
                display: block;
            }}
        </style>
    </head>
    <body>
        <h1>File Tree</h1>
        <button onclick="copyToClipboard()">Copy to Clipboard</button>
        <ul id="fileTree">
            {generate_html(directory_path)}
        </ul>
        <script>
            var toggler = document.getElementsByClassName("caret");
            for (var i = 0; i < toggler.length; i++) {{
                toggler[i].addEventListener("click", function() {{
                    this.parentElement.querySelector(".nested").classList.toggle("active");
                    this.classList.toggle("caret-down");
                }});
            }}

            function generateAsciiTree(element, prefix="") {{
                var asciiTree = "";
                var children = element.children;
                for (var i = 0; i < children.length; i++) {{
                    var item = children[i];
                    var connector = (i < children.length - 1) ? "├── " : "└── ";
                    var text = item.querySelector(".caret") ? item.querySelector(".caret").textContent : item.textContent;
                    asciiTree += prefix + connector + text + "\\n";
                    var nested = item.querySelector(".nested");
                    if (nested && nested.classList.contains("active")) {{
                        asciiTree += generateAsciiTree(nested, prefix + ((i < children.length - 1) ? "│   " : "    "));
                    }}
                }}
                return asciiTree;
            }}

            function copyToClipboard() {{
                var fileTree = document.getElementById("fileTree");
                var asciiTree = generateAsciiTree(fileTree);
                navigator.clipboard.writeText(asciiTree).then(function() {{
                    alert('File tree copied to clipboard!');
                }}, function(err) {{
                    console.error('Could not copy text: ', err);
                }});
            }}
        </script>
    </body>
    </html>
    """

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(html_content)

if __name__ == "__main__":
    indirectory_path = sys.argv[1] if len(sys.argv) > 1 else './'
    output_file_path = sys.argv[2] if len(sys.argv) > 2 else 'filetree.html'

    generate_file_tree_html(indirectory_path, output_file_path)
