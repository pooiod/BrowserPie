import os
import json
import re
import io
import sys
import traceback
import threading
from flask import Flask, request, render_template_string
import tkinter as tk
import webbrowser

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'BrowserPieConfig.json')

global defaultport
defaultport = 5938
DEFAULT_CONFIG = {
    "port": defaultport,
    "allowed_websites": ["https://filenest.pages.dev"]
}

def execute_query(query_code):
    local_scope = {}
    output_stream = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output_stream

    try:
        exec(f"_result = ({query_code})", {}, local_scope)
        response = local_scope.get('_result', None)
    except SyntaxError:
        try:
            exec(query_code, {}, local_scope)
            response = None
        except Exception as e:
            return "Error executing code: " + str(e)
    except Exception as e:
        return "Error executing code: " + str(e)
    finally:
        sys.stdout = old_stdout

    if response is None:
        printed_output = output_stream.getvalue().strip().splitlines()
        return printed_output[-1] if printed_output else ""

    return response

if not os.path.exists(CONFIG_FILE):
    webbrowser.open("https://localhost:" + str(defaultport) + "/#setup")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

app = Flask(__name__)

prompt_lock = threading.Lock()
prompt_count = 0
max_prompts = 1

execution_history = []

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BrowserPie - Settings</title>
    <link href="data:image/x-icon;base64,AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAARNP/AP///wCfcDoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEREQAAAAAAEREREAAAAAAREiEQAAAAABESIRAAADMzEREREREDMzMRERERERMzMxEREREREzMzERERERETMzMzMzMRERMzMzMzMxEREzMzMzMzEREQMzMzMzMREQAAAzIjMwAAAAADMiMzAAAAAAMzMzMAAAAAADMzMAAAD8HwAA+A8AAPgPAAD4DwAAgAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIABAADwHwAA8B8AAPAfAAD4PwAA" rel="icon" type="image/x-icon">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .spinner {
            display: none;
            position: fixed;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
        }
    </style>
</head>
<body class="bg-light">
<div class="container mt-5">
    <h1 class="mb-4">BrowserPie Settings</h1>
    <form id="configForm" method="post" action="/" onsubmit="return confirmPortChange()">
        <div class="mb-3">
            <label for="port" class="form-label">Port</label>
            <input type="number" class="form-control" id="port" name="port" value="{{ config['port'] }}" required>
            <div class="form-text text-danger" id="portWarning" style="display: none;">
                Please restart your device to apply this port number
            </div>
            <div class="form-text">You will need to restart the server if you change this.</div>
        </div>
        <div class="mb-3">
            <label for="allowed_websites" class="form-label">Allowed Websites</label>
            <textarea class="form-control" id="allowed_websites" name="allowed_websites" rows="3" required>{{ allowed_websites }}</textarea>
            <div class="form-text">Websites that can always run code (one per line).</div>
        </div>
        <button type="submit" class="btn btn-primary">Update Configuration</button>
    </form>
    <a href="/history" class="btn btn-info mt-4">View Execution History</a>
    {% if message %}
    <div class="alert alert-success mt-4" role="alert">
        {{ message }}
    </div>
    {% endif %}
    {% if restart_message %}
    <div class="alert alert-warning mt-4" role="alert">
        {{ restart_message }}
    </div>
    {% endif %}
</div>

<div class="spinner">
    <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
</div>

<script>
    function confirmPortChange() {
        const portInput = document.getElementById('port').value;
        const currentPort = {{ config['port'] }};
        
        if (portInput != {{ defaultport }}) {
            const warningDiv = document.getElementById('portWarning');
            warningDiv.style.display = 'block';
            const confirmChange = confirm("Some sites may expect you to use the default port ({{ defaultport }}).");
            
            if (!confirmChange) {
                return false;
            }
        }
        
        if (portInput != currentPort) {
            // window.location.hash = "restart";
            document.querySelector("#configForm").action = "/#restart";
        }
        return true;
    }

    window.onload = () => {
        if (window.location.hash == "#restart") {
            window.location.hash = ""
            document.getElementById('portWarning').style.display = 'block';
            document.querySelector("#configForm > div:nth-child(1) > div:nth-child(4)").style.display = 'none';
        } else if ({{ config['port'] }} != {{ defaultport }}) {
            document.querySelector("#configForm > div:nth-child(1) > div:nth-child(4)").textContent = "Some sites may expect you to use port {{ defaultport }}.";
        } else if (window.location.hash == "#setup") {
            window.location.hash = ""
javascript:(function(){const message='Please enable this setting to use BrowserPie:',url='chrome://flags/#allow-insecure-localhost',modal=document.createElement('div');modal.style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:9999;font-family:Arial,sans-serif;font-size:20px;text-align:center;";const text=document.createElement('div');text.innerText=message;modal.appendChild(text);const link=document.createElement('a');link.innerText=url;link.href=url;link.style="color:#1E90FF;margin-top:20px;font-size:18px;text-decoration:underline;";link.target='_blank';modal.appendChild(link);const copyMessage=document.createElement('div');copyMessage.style="margin-top:20px;font-size:16px;opacity:0;transition:opacity 0.5s;";modal.appendChild(copyMessage);document.body.appendChild(modal);modal.onclick=function(){if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(url).then(()=>{copyMessage.innerText='URL copied to clipboard!';copyMessage.style.opacity='1';setTimeout(()=>{copyMessage.style.opacity='0';},2000);});}else{const tempInput=document.createElement('input');tempInput.value=url;document.body.appendChild(tempInput);tempInput.select();document.execCommand('copy');document.body.removeChild(tempInput);copyMessage.innerText='URL copied to clipboard!';copyMessage.style.opacity='1';setTimeout(()=>{copyMessage.style.opacity='0';},2000);}}})();
        }
    };
</script>
</body>
</html>
"""

HISTORY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BrowserPie - History</title>
    <link href="data:image/x-icon;base64,AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAARNP/AP///wCfcDoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEREQAAAAAAEREREAAAAAAREiEQAAAAABESIRAAADMzEREREREDMzMRERERERMzMxEREREREzMzERERERETMzMzMzMRERMzMzMzMxEREzMzMzMzEREQMzMzMzMREQAAAzIjMwAAAAADMiMzAAAAAAMzMzMAAAAAADMzMAAAD8HwAA+A8AAPgPAAD4DwAAgAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIABAADwHwAA8B8AAPAfAAD4PwAA" rel="icon" type="image/x-icon">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <h1 class="mb-4">BrowserPie Command History</h1>
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Domain</th>
                <th>Code</th>
                <th>Response</th>
            </tr>
        </thead>
        <tbody>
            {% for entry in history %}
            <tr>
                <td>{{ entry['domain'] }}</td>
                <td><pre>{{ entry['code'] }}</pre></td>
                <td>{{ entry['response'] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <a href="/" class="btn btn-primary">Back to Configuration</a>
</div>
</body>
</html>
"""

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    global config
    if request.method == 'POST':
        try:
            # Get the form data
            new_port = int(request.form.get('port', defaultport))
            allowed_websites_input = request.form.get('allowed_websites', '').strip().split('\n')

            restart_message = None

            if config['port'] != new_port:
                config['port'] = new_port
                restart_message = "You will need to restart the server to apply the new port."

            config['allowed_websites'] = [website.strip() for website in allowed_websites_input if website.strip()]

            save_config(config)

            message = "Configuration updated successfully."
            return render_template_string(INDEX_HTML, defaultport=defaultport, config=config, allowed_websites="\n".join(config.get('allowed_websites', [])), message=message, restart_message=restart_message)

        except Exception as e:
            message = f"An error occurred: {e}"
            return render_template_string(INDEX_HTML, defaultport=defaultport, config=config, allowed_websites="\n".join(config.get('allowed_websites', [])), message=message)

    allowed_websites = "\n".join(config.get('allowed_websites', []))
    return render_template_string(INDEX_HTML, defaultport=defaultport, config=config, allowed_websites=allowed_websites, message=None, restart_message=None)

@app.route('/run', methods=['GET'])
def run_code():
    query_code = request.args.get('py')
    origin = request.headers.get('Origin')

    if not origin:
        return "Error executing code: Execution denied.", 403

    allowed_websites = config.get('allowed_websites', [])
    if not any(re.match(website, origin) for website in allowed_websites):
        return handle_unauthorized_access(origin, query_code)

    if not query_code:
        return "Error executing code: No code provided to execute.", 400

    try:
        response = str(execute_query(query_code))

        store_execution_history(origin, query_code, response)

        return response
    except Exception as e:
        response = f"Error executing code: {str(e)}<br>{traceback.format_exc()}"
        
        store_execution_history(origin, query_code, response)

        return response, 500

def handle_unauthorized_access(origin, query_code):
    """ Show a tkinter prompt to handle unauthorized access """
    global prompt_count
    if prompt_count < max_prompts:
        prompt_count += 1 
        result = show_warning(origin)

        prompt_count = 0

        if result == "Allow Once":
            try:
                # local_scope = {}
                # exec(query_code, {}, local_scope)
                response = str(execute_query(query_code))

                store_execution_history(origin, query_code, response)

                return response
            except Exception as e:
                return f"Error executing code: {str(e)}", 500

        elif result == "Add to Allow List":
            config['allowed_websites'].append(origin)
            save_config(config)

            try:
                response = str(execute_query(query_code))

                store_execution_history(origin, query_code, response)

                return response
            except Exception as e:
                return f"Error executing code: {str(e)}", 500

        else:
            return "Error executing code: Access denied for this origin.", 403
    else:
        return "Error executing code: Too many requests. Please wait before trying again.", 429

def store_execution_history(domain, code, response): 
    """ Store the execution history, keeping the last 30 entries """
    if len(execution_history) >= 30:
        execution_history.pop(0)
    execution_history.append({"domain": domain, "code": code, "response": response})

@app.route('/history', methods=['GET'])
def history():
    """ Display the execution history """
    return render_template_string(HISTORY_HTML, history=execution_history)

def show_warning(origin):
    """ Display a Tkinter warning prompt for unauthorized access """
    root = tk.Tk()
    root.title("BrowserPie Security Warning")

    origin2 = origin.replace("https://", "").replace("http://", "")

    root.geometry("400x300")
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    root.configure(bg="#ffffff")

    shadow_frame = tk.Frame(root, bg="#cccccc", bd=3)
    shadow_frame.pack(expand=True, fill='both', padx=5, pady=5)

    frame = tk.Frame(shadow_frame, bg="#ffffff", bd=0)
    frame.pack(expand=True, fill='both', padx=1, pady=1)

    question_text = (
        f"{origin2} wants to run administrator-level code on your device.\n\n"
        "⚠️ WARNING: Allowing this will give the website access to run "
        "potentially harmful admin-level  code on your device."
    )

    label = tk.Label(frame, text=question_text, fg="#333333", bg="#ffffff", wraplength=350, justify="center", font=("Helvetica", 12))
    label.pack(pady=(20, 10))

    button_frame = tk.Frame(frame, bg="#ffffff")
    button_frame.pack(pady=(10, 0))

    result = None

    def on_response(action):
        nonlocal result
        result = action
        root.quit()

    allow_once_button = tk.Button(button_frame, text="Allow Once", command=lambda: on_response("Allow Once"),
                                   bg="#f29500", fg="white", font=("Helvetica", 10), padx=8, pady=5, relief="flat")
    allow_once_button.pack(side=tk.LEFT, expand=True, padx=(0, 5))

    add_to_allow_list_button = tk.Button(button_frame, text="Always Allow", command=lambda: on_response("Add to Allow List"),
                                          bg="#F44336", fg="white", font=("Helvetica", 10), padx=8, pady=5, relief="flat")
    add_to_allow_list_button.pack(side=tk.LEFT, expand=True, padx=(5, 0))

    deny_access_button = tk.Button(frame, text="Deny Code Access", command=lambda: on_response("Deny"),
                                    bg="#4CAF50", fg="white", font=("Helvetica", 12), padx=10, pady=5, relief="flat")
    deny_access_button.pack(pady=(15, 0))

    center_window(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_response("Deny"))
    root.mainloop()
    root.destroy()
    return result

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def start_server():
    app.run(host='0.0.0.0', port=config['port'], threaded=True, ssl_context='adhoc')

if __name__ == "__main__":
    start_server()
