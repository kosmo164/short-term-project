from flask import Flask, render_template, request
from model import run_prediction

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ticker = request.form.get("ticker")
        if ticker:
            plot_url = run_prediction(ticker)  # base64 이미지 반환
            return render_template("index.html", ticker=ticker, result=True, plot_url=plot_url)
    return render_template("index.html", result=False)

if __name__ == "__main__":
    app.run(debug=True)

