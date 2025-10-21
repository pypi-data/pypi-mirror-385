GRAPHVIZ_NODE_DATA = (
    '<table cellpadding="3" cellborder="1" cellspacing="0" border="0" style="rounded">{}</table>'
)
GRAPHVIZ_NODE_DATA_ROW = '<tr><td bgcolor="{}"><font face="arial" color="white">{}</font></td></tr>'
GRAPHVIZ_LINK_DATA = (
    '<table cellpadding="0" cellborder="0" cellspacing="0" border="0" style="rounded">{}</table>'
)
GRAPHVIZ_LINK_DATA_ROW = '<tr><td bgcolor="snow"><font face="arial" color="{}">{}</font></td></tr>'
GRAPHVIZ_START_END_LINK_DATA = '<table cellpadding="0" cellborder="0" cellspacing="0" border="0"><tr><td bgcolor="white"><font face="arial" color="{}">{}</font></td></tr></table>'
MERMAID_UPPER_HTML = """<html>
<body>
    <pre class='mermaid'>
"""
MERMAID_LOWER_HTML = """
    </pre>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true });
    </script>
</body>
</html>"""
