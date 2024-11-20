from flask import Flask, request, jsonify, render_template
import requests
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

# API 요청에 필요한 정보
BASE_URL = "http://apis.data.go.kr/1613000/ExpBusInfoService"
SERVICE_KEY = "WKp1VvR7awnciw/bWZyS/ucpv8Tiihgn8LgHK7a7Hw0u+ewXMZNo7buPDOywQc2k7pjJssVL39S0Oe6RWzCa3w=="

def get_bus_terminal_list(terminal_name=None, page_no=1, num_of_rows=100, response_type="json"):
    """고속버스터미널 목록 조회"""
    params = {
        "serviceKey": SERVICE_KEY,
        "_type": response_type,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
    }
    if terminal_name:
        params["terminalNm"] = terminal_name

    response = requests.get(f"{BASE_URL}/getExpBusTrminlList", params=params)
    if response.status_code == 200:
        if response_type == "json":
            return response.json()
        elif response_type == "xml":
            root = ET.fromstring(response.content)
            return ET.tostring(root, encoding="utf-8").decode("utf-8")
    else:
        return {"error": f"API Error: {response.status_code}"}

def get_bus_schedule(dep_terminal_id, arr_terminal_id, dep_date="20240101", response_type="json"):
    """출/도착지 기반 고속버스 정보 조회"""
    params = {
        "serviceKey": SERVICE_KEY,
        "_type": response_type,
        "depTerminalId": dep_terminal_id,
        "arrTerminalId": arr_terminal_id,
        "depPlandTime": dep_date,
        "numOfRows": 100,
    }

    response = requests.get(f"{BASE_URL}/getStrtpntAlocFndExpbusInfo", params=params)
    if response.status_code == 200:
        if response_type == "json":
            return response.json()
        elif response_type == "xml":
            root = ET.fromstring(response.content)
            return ET.tostring(root, encoding="utf-8").decode("utf-8")
    else:
        return {"error": f"API Error: {response.status_code}"}

@app.route('/')
def home():
    """메인 페이지 렌더링"""
    return render_template('index.html')

@app.route('/api/terminals', methods=['GET'])
def terminals():
    """고속버스 터미널 조회 API"""
    terminal_name = request.args.get('terminal_name', None)
    page_no = request.args.get('page_no', 1, type=int)
    num_of_rows = request.args.get('num_of_rows', 100, type=int)
    response_type = request.args.get('response_type', 'json')

    data = get_bus_terminal_list(terminal_name, page_no, num_of_rows, response_type)
    return jsonify(data)

@app.route('/api/bus_schedule', methods=['GET'])
def bus_schedule():
    """고속버스 스케줄 조회 API"""
    dep_terminal_id = request.args.get('dep_terminal_id')
    arr_terminal_id = request.args.get('arr_terminal_id')
    dep_date = request.args.get('dep_date', '20240101')
    response_type = request.args.get('response_type', 'json')

    if not dep_terminal_id or not arr_terminal_id:
        return jsonify({"error": "Missing required parameters: dep_terminal_id, arr_terminal_id"}), 400

    data = get_bus_schedule(dep_terminal_id, arr_terminal_id, dep_date, response_type)
    return jsonify(data)

@app.route('/result')
def result_page():
    return render_template('result.html')

# Google Cloud Functions 진입점
def main(request):
    """Cloud Functions 엔트리포인트"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

# Cloud Run 진입점
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Cloud Run에서 제공하는 PORT 환경 변수 사용
    app.run(host="0.0.0.0", port=port)
