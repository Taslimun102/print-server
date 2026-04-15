from flask import Flask, request, render_template_string, send_from_directory
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = "/home/kali/Documents"
OUTPUT_FOLDER = "/home/kali/PDF"
PRINTER = "Os_Virtual_PDF_Printer"

last_uploaded_file = ""

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Smart Print Server</title>

<!-- Auto Refresh -->
<meta http-equiv="refresh" content="10">

<style>
body { font-family: Arial; margin: 40px; }
button { padding: 8px 15px; margin: 5px; }
table { border-collapse: collapse; width: 60%; }
th, td { border: 1px solid black; padding: 8px; text-align: center; }
th { background-color: #ddd; }
</style>

</head>

<body>

<h2>🖨️ Smart Print Server Dashboard</h2>

<!-- Upload -->
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button name="action" value="upload">📤 Upload</button>
</form>

<!-- Print -->
<form method="post">
    <select name="filename">
        {% for file in uploaded_files %}
        <option value="{{file}}">{{file}}</option>
        {% endfor %}
    </select>
    <button name="action" value="print">🖨️ Print Selected File</button>
</form>

<hr>

<!-- Buttons -->
<form method="post">
    <button name="action" value="status">📊 Printer Status</button>
    <button name="action" value="jobs">🧾 Print Jobs</button>
</form>

<hr>

<h3>📄 Generated PDFs:</h3>

<table>
<tr><th>File Name</th><th>Download</th></tr>
{% for file in pdfs %}
<tr>
<td>{{file}}</td>
<td><a href="/download/{{file}}">⬇ Download</a></td>
</tr>
{% endfor %}
</table>

<hr>

<h3>📊 Status / Jobs:</h3>
<pre>{{output}}</pre>

<hr>

<h3>⏳ Progress:</h3>
<pre>{{progress}}</pre>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_uploaded_file
    output = ""
    progress = ""

    # Uploaded files list
    uploaded_files = os.listdir(UPLOAD_FOLDER)

    # Generated PDFs
    try:
        pdfs = os.listdir(OUTPUT_FOLDER)
    except:
        pdfs = []

    if request.method == 'POST':
        action = request.form.get("action")

        # Upload
        if action == "upload":
            f = request.files['file']
            if f.filename != "":
                path = os.path.join(UPLOAD_FOLDER, f.filename)
                f.save(path)
                last_uploaded_file = f.filename
                output = f"✅ Uploaded: {f.filename}"

        # Print selected
        elif action == "print":
            filename = request.form.get("filename")
            if filename:
                full_path = os.path.join(UPLOAD_FOLDER, filename)
                os.system(f"lp -d {PRINTER} {full_path}")
                output = f"🖨️ Printing: {filename}"

        # Status
        elif action == "status":
            output = subprocess.getoutput("lpstat -p")

        # Jobs
        elif action == "jobs":
            output = subprocess.getoutput("lpstat -o")

    # Progress check (auto)
    job_check = subprocess.getoutput("lpstat -o")
    if job_check.strip() == "":
        progress = "✅ No active jobs (Idle)"
    else:
        progress = "⏳ Printing in progress..."

    return render_template_string(
        HTML,
        output=output,
        progress=progress,
        pdfs=pdfs,
        uploaded_files=uploaded_files
    )


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
