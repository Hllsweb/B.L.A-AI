from flask import Flask, jsonify, request
import httpx
import pandas as pd
import io
import asyncio

app = Flask(__name__)

GITHUB_URL = 'https://raw.githubusercontent.com/Hllsweb/B.L.A-AI/main/Resultados_Anteriores.xlsx'
BLAZE_API_URL = 'https://blaze.com/api/roulette_games/recent'

# Configuração do proxy
PROXY = {
    "http://": "http://brd-customer-hl_a7cc6768-zone-isp_proxy1:bq6xo1n9zi8b@brd.superproxy.io:22225",
    "https://": "http://brd-customer-hl_a7cc6768-zone-isp_proxy1:bq6xo1n9zi8b@brd.superproxy.io:22225"
}

def fetch_data():
    response = httpx.get(GITHUB_URL)
    response.raise_for_status()  # Verifica se houve algum erro na requisição
    data = pd.read_excel(io.BytesIO(response.content))
    return data

async def fetch_blaze_data():
    async with httpx.AsyncClient(proxies=PROXY) as client:
        response = await client.get(BLAZE_API_URL)
        response.raise_for_status()  # Verifica se houve algum erro na requisição
        return response.json()

@app.route('/dados', methods=['GET'])
def get_dados():
    data = fetch_data()
    return jsonify(data.to_dict(orient='records'))

@app.route('/dados_filtrados', methods=['GET'])
def get_dados_filtrados():
    data = fetch_data()
    cor = request.args.get('cor')
    if cor:
        data = data[data['Cor'] == cor]
    return jsonify(data.to_dict(orient='records'))

@app.route('/dados_blaze', methods=['GET'])
async def get_dados_blaze():
    try:
        data = await fetch_blaze_data()
        results = [{'color': item['color'], 'number': item['roll'], 'created_at': item['created_at'], 'id': item['id']} for item in data]
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
