'''
설명 요약
Flask를 이용해 웹 서버를 실행합니다.
/ 경로에서 GET 요청 시 기본 페이지를 보여주고, POST 요청 시 사용자가 입력한 ticker 값을 받아 run_prediction() 함수로 처리합니다.
결과로 생성된 그래프 이미지를 base64 형태로 HTML에 전달하여 표시합니다.
debug=True 옵션을 통해 개발 중 오류 발생 시 디버그 정보를 확인할 수 있습니다.

'''

from flask import Flask, render_template, request
from model import run_prediction
# Flask 애플리케이션 객체 생성
app = Flask(__name__)

# comment; 라우트 설정: "/" 경로로 GET, POST 요청을 처리
@app.route("/", methods=["GET", "POST"])
def index():
   # 요청 방식이 POST일 경우 (즉, 사용자가 폼을 제출했을 때)
    if request.method == "POST":
      # 폼에서 'ticker' 값 가져오기 (예: 주식 티커 심볼)
        ticker = request.form.get("ticker")
        if ticker:
        # ticker 값을 기반으로 예측 실행 → 결과는 base64 인코딩된 이미지 URL
            plot_url = run_prediction(ticker)  # base64 이미지 반환
            # index.html 템플릿 렌더링, ticker와 결과 이미지 전달
            return render_template("index.html", ticker=ticker, result=True, plot_url=plot_url)
    # GET 요청이거나 ticker 값이 없을 경우 → 결과 없음 상태로 템플릿 렌더링
    return render_template("index.html", result=False)

# 애플리케이션 실행 (디버그 모드 활성화)
if __name__ == "__main__":
    app.run(debug=True)

