root=$(pwd)
data_dir="$root/data"
doc_dir="$root/documentation/build/html"

raw_documentation="$data_dir/TransformationDocumentation.docx"
html_documentation="$doc_dir/TransformationDocumentation.html"

pandoc -o "$html_documentation" "$raw_documentation"

content=$(cat "$html_documentation")

cat << EOF > "$html_documentation"
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>OFA TANF Longitudinal Dataset Documentation — OFA TANF Longitudinal Dataset 0.0.1 documentation</title>
    <link rel="stylesheet" type="text/css" href="_static/pygments.css?v=d1102ebc">
    <link rel="stylesheet" type="text/css" href="_static/basic.css?v=686e5160">
    <link rel="stylesheet" type="text/css" href="_static/alabaster.css?v=27fed22d">
    <script src="_static/documentation_options.js?v=d45e8c67"></script>
    <script src="_static/doctools.js?v=9bcbadda"></script>
    <script src="_static/sphinx_highlight.js?v=dc90522c"></script>
    <link rel="index" title="Index" href="genindex.html">
    <link rel="search" title="Search" href="search.html">
    <link rel="next" title="otld" href="_autosummary/otld.html">
    <link rel="stylesheet" href="_static/custom.css" type="text/css">
</head>
EOF

cat << EOF >> "$html_documentation"
<body>
    <div class="document">
        <div class="documentwrapper">
            <div class="bodywrapper">
                <div class="body" role="main">
EOF

echo $content >> "$html_documentation"

cat << EOF >> "$html_documentation"
                </div>
            </div>
        </div>
    </div>
</body>
EOF