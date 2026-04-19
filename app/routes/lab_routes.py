from flask import Blueprint, request, render_template_string

lab_bp = Blueprint("lab", __name__)

@lab_bp.route("/vuln", methods=["GET"])
def vulnerable_page():
    q = request.args.get("q", "")
    file = request.args.get("file", "")

    return render_template_string(f"""
    <html>
    <body>
        <h1>Vulnerable Page</h1>

        <p>Search: {q}</p> <!-- XSS surface -->

        <p>File: {file}</p> <!-- traversal surface -->

        <form action="/vuln-submit" method="post">
            <input type="text" name="comment">
            <button type="submit">Submit</button>
        </form>

        <a href="/vuln?q=test">Test XSS</a>
        <a href="/vuln?file=report.txt">Test Traversal</a>
    </body>
    </html>
    """)