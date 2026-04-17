import os
from flask import Flask, request, jsonify
from nova_act import NovaAct
import threading
import time

app = Flask(__name__)

# Nova Act requires debug port
os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"
NOVA_API_KEY = os.environ.get("NOVA_ACT_API_KEY", "63629994-8637-48db-bdd8-f6f1ef60a696")

def execute_dispatch(data):
    """
    Executes the highly stable browser automation using the API payload.
    """
    customer = data.get("customer_name", "Unknown")
    phone = data.get("phone", "No phone")
    vehicle = data.get("vehicle_type", "Vehicle")
    service = data.get("service_type", "Tow")
    pickup = data.get("pickup_location", "Unknown Location")
    dest = data.get("destination", "Unknown Location")
    notes = data.get("notes", "No notes")

    try:
        # 1. Boot up on lightweight domain to avoid startup crashes
        with NovaAct(
            starting_page="https://example.com",
            headless=True, # Must be True for cloud servers!
            tty=False,
            nova_act_api_key=NOVA_API_KEY
        ) as nova:
            nova.start()
            
            # 2. Programmatic Navigation Bypass
            print("[System] Bypassing native navigation limits...")
            nova.page.goto("https://app.towbook.com/Security/Login.aspx", wait_until="commit")
            
            # 3. Secure Fast Login
            print("[System] Executing login flow...")
            nova.act("Type Faizan463 into the username and 3N@@cD6LEZaaxFA into the password. Click Log In. Stop immediately after submitting.")
            
            # 4. Mandatory Stabilization
            time.sleep(12)
            
            # 5. Dispatch Creation
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
            return True, str(result)
            
    except Exception as e:
        return False, str(e)

@app.route('/dispatch', methods=['POST'])
def handle_dispatch():
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No JSON payload provided."}), 400
        
    print(f"Received new dispatch request for: {data.get('customer_name')}")
    
    # Execute the automation synchronously so n8n knows if it succeeded
    success, message = execute_dispatch(data)
    
    if success:
        return jsonify({"success": True, "message": "Call successfully created in Towbook.", "nova_logs": message})
    else:
        return jsonify({"success": False, "error": message}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "NovaAct Towbook Node"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
