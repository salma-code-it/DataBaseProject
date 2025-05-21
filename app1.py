from flask import Flask, render_template
import webbrowser
import threading

app = Flask(__name__)

@app.route('/')
def accueil():
    return render_template('index.html')

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("Le script Flask démarre...")
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
