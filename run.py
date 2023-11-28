from app import app
import webbrowser

# Checks if th run.py file has executed directly and not imported
if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug = True)