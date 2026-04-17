import os
from flask import Flask, request, jsonify
from nova_act import NovaAct
import threading
import time

app = Flask(__name__)

os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"
NOVA_API_KEY = os.environ.get("NOVA_ACT_API_KEY", "63629994-8637-48db-bdd8-f6f1ef60a696")

def execute_dispatch(data):
    customer = data.get("customer_name", "Unknown")
    phone = data.get("phone", "No phone")
    vehicle = data.get("vehicle_type", "Vehicle")
    service = data.get("service_type", "Tow")
    pickup = data.get("pickup_location", "Unknown Location")
    dest = data.get("destination", "Unknown Location")
    notes = data.get("notes", "No notes")

    try:
        with NovaAct(
            starting_page="https://example.com",
            headless=True, 
            tty=False,
            nova_act_api_key=NOVA_API_KEY
        ) as nova:
            nova.start()
            
            print("[System] Bypassing native navigation limits...")
            nova.page.goto("https://app.towbook.com/Security/Login.aspx", wait_until="commit")
            
            print("[System] Executing login flow...")
            nova.act("Type Faizan463 into the username and 3N@@cD6LEZaaxFA into the password. Click Log In. Stop immediately after submitting.")
            
            time.sleep(12)
            
            print("[System] Executing heavy dispatch flow...")
            
            dispatch_instruction = f"""
            You are now on the Towbook dashboard. Follow these strict rules to avoid crashing:
            
            - RULE 1: If you type into a dropdown (like Vehicle) and the exact match isn't there, select the closest match like "Other" or "Light". Do not loop.
            - RULE 2 (Location Fields are STRICT): You must type the EXACT literal address given to you into the Pickup and Destination fields. 
              DO NOT wait for suggestions. DO NOT click dropdowns. DO NOT change the address. 
              Once you type it in, IMMEDIATELY move on to the next field. Even if you think the field says 'address' or looks empty, assume your typing was successful and DO NOT click it again. Do not loop.
              
            Task details:
            1. Find and click 'New Call'.
            2. Set Account to 'Agero'.
            3. Name: {customer}
            4. Phone: {phone}
            5. Vehicle: {vehicle}
            6. Service Type: {service}
            7. Pickup Location: Type EXACTLY '{pickup}' and do not re-check it.
            8. Destination: Type EXACTLY '{dest}' and do not re-check it.
            9. Notes: {notes}
            
            Once all fields are populated, click 'Create Call' and confirm it was saved.
            """
            
            result = nova.act(dispatch_instruction)
            print("[System] Background dispatch completed successfully.")
            return True, str(result)
            
    except Exception as e:
        print(f"[System] AI Error: {e}")
        return False, str(e)

@app.route('/dispatch', methods=['POST'])
def handle_dispatch():
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No JSON payload provided."}), 400
        
    print(f"Received new dispatch request for: {data.get('customer_name')}")
    
    thread = threading.Thread(target=execute_dispatch, args=(data,))
    thread.start()
    
    return jsonify({
        "success": True, 
        "message": "Dispatch received! Robot has started processing in the background."
    }), 202

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "NovaAct Towbook Node"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
