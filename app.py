from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
import json
import csv
import io

app = Flask(__name__)
CORS(app)

SHAREPOINT_SITE_URL = "https://erammotors365.sharepoint.com/sites/CLTWEEKLY"
SHAREPOINT_LIST_NAME = "Name"
USERNAME = "Mis@erammotors.com"
PASSWORD = "Rahul@302319"

def get_sharepoint_context():
    ctx_auth = AuthenticationContext(SHAREPOINT_SITE_URL)
    if ctx_auth.acquire_token_for_user(USERNAME, PASSWORD):
        ctx = ClientContext(SHAREPOINT_SITE_URL, ctx_auth)
        return ctx
    else:
        raise Exception("Authentication failed")

def add_to_sharepoint_list(data):
    ctx = get_sharepoint_context()
    list_obj = ctx.web.lists.get_by_title(SHAREPOINT_LIST_NAME)
    
    item_creation_info = {
        "Title": data.get("name"),
        "Age": data.get("age"),
        "Location": data.get("location")
    }

    item = list_obj.add_item(item_creation_info)
    ctx.execute_query()
    return {"status": "success", "item_id": item.properties["Id"]}

@app.route('/submit_form', methods=['POST'])
def submit_form():
    data = request.json
    try:
        result = add_to_sharepoint_list(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    # Implement data retrieval from SharePoint or local storage if needed
    return jsonify({"name": "", "age": "", "location": ""})

@app.route('/download_csv', methods=['GET'])
def download_csv():
    # Sample data for CSV download
    data = [
        {"Name": "John Doe", "Age": "30", "Location": "USA"}
    ]
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Name", "Age", "Location"])
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='data.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
