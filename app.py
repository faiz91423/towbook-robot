import os
from flask import Flask, request, jsonify
from nova_act import NovaAct
import threading
import time

app = Flask(__name__)

os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"
NOVA_API_KEY = os.environ.get("NOVA_ACT_API_KEY", "63629994-8637-48db-bdd8-f6f1ef60a696")

def execute_dispatch(data):
    """
    Executes the browser automation in the background.
    """
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
            
            print("[System] Executing dispatch flow...")
            dispatch_instruction = f"""
            You are now on the Towbook dashboard.
            1. Find and click 'New Call'.
            2. Set Account to 'Agero'.
            3. Name: {customer}
            4. Phone: {phone}
            5. Vehicle: {vehicle}
            6. Service Type: {service}
            7. Pickup Location: {pickup}
            8. Destination: {dest}
            9. Notes: {notes}
            10. Finally, click 'Create Call' and confirm it was saved.
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
    
    # KEY FIX: Run the robot in the background so we don't hit Railway's 60-second connection timeout!
    thread = threading.Thread(target=execute_dispatch, args=(data,))
    thread.start()
    
    # Respond to n8n instantly so the webhook successfully completes!
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
