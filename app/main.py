"""
Smart City Automation System - Main Flask Application
"""
from flask import Flask, render_template, jsonify, request
from app.controllers.city_controller import CityController
from app.controllers.banking_controller import BankingController
from app.services.notification_service import NotificationService, SecurityObserver, TransactionObserver
from app.commands.infrastructure_commands import LightOnCommand, LightOffCommand, TrafficGreenCommand, TrafficRedCommand
from app.routines.daily_routines import SunriseRoutine, SunsetRoutine
from app.models.resident import Resident
from app.models.device import StreetLight, TrafficSignal, SecurityCamera
from app.security.auth import AuthService

app = Flask(__name__, 
            template_folder='templates',
            static_folder='../static')

# Initialize core services
city_controller = CityController.get_instance()
banking_controller = BankingController()
notification_service = NotificationService()
auth_service = AuthService()

# Register observers
notification_service.attach(SecurityObserver())
notification_service.attach(TransactionObserver())

# Initialize sample devices
street_light_1 = StreetLight("SL001", "Main Street Light 1")
street_light_2 = StreetLight("SL002", "Main Street Light 2")
traffic_signal_1 = TrafficSignal("TS001", "Central Intersection")
security_camera_1 = SecurityCamera("SC001", "City Hall Entrance")

city_controller.register_device(street_light_1)
city_controller.register_device(street_light_2)
city_controller.register_device(traffic_signal_1)
city_controller.register_device(security_camera_1)

# Sample resident
sample_resident = Resident("R001", "John Doe", "john@smartcity.com", "resident")

# ==================== Routes ====================

@app.route('/')
def dashboard():
    """Main resident dashboard"""
    devices = city_controller.get_all_devices()
    notifications = notification_service.get_recent_notifications()
    return render_template('dashboard.html', 
                         devices=devices, 
                         notifications=notifications,
                         resident=sample_resident)

@app.route('/admin')
def admin_panel():
    """City administrator panel"""
    devices = city_controller.get_all_devices()
    stats = city_controller.get_system_stats()
    return render_template('admin.html', devices=devices, stats=stats)

@app.route('/banking')
def banking():
    """Digital banking interface"""
    transactions = banking_controller.get_recent_transactions()
    balance = banking_controller.get_balance("R001")
    return render_template('banking.html', 
                         transactions=transactions,
                         balance=balance)

@app.route('/security')
def security():
    """Security alerts center"""
    alerts = notification_service.get_security_alerts()
    cameras = [d for d in city_controller.get_all_devices() if d['type'] == 'SecurityCamera']
    return render_template('security.html', alerts=alerts, cameras=cameras)

# ==================== API Endpoints ====================

@app.route('/api/device/<device_id>/control', methods=['POST'])
def control_device(device_id):
    """Control a city device"""
    data = request.json
    action = data.get('action')
    
    if action == 'on':
        command = LightOnCommand(city_controller, device_id)
    elif action == 'off':
        command = LightOffCommand(city_controller, device_id)
    elif action == 'green':
        command = TrafficGreenCommand(city_controller, device_id)
    elif action == 'red':
        command = TrafficRedCommand(city_controller, device_id)
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    result = city_controller.execute_command(command)
    notification_service.notify(f"Device {device_id}: {action}", "info")
    
    return jsonify({'success': True, 'result': result})

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """Process a payment (fiat or crypto)"""
    data = request.json
    payment_type = data.get('type', 'fiat')
    amount = data.get('amount', 0)
    currency = data.get('currency', 'USD')
    description = data.get('description', 'City Service Payment')
    
    result = banking_controller.process_payment(
        resident_id="R001",
        amount=amount,
        currency=currency,
        payment_type=payment_type,
        description=description
    )
    
    if result['success']:
        notification_service.notify(
            f"Payment of {amount} {currency} processed", 
            "transaction"
        )
    
    return jsonify(result)

@app.route('/api/routine/<routine_type>', methods=['POST'])
def execute_routine(routine_type):
    """Execute a daily routine"""
    if routine_type == 'sunrise':
        routine = SunriseRoutine(city_controller)
    elif routine_type == 'sunset':
        routine = SunsetRoutine(city_controller)
    else:
        return jsonify({'error': 'Invalid routine type'}), 400
    
    routine.execute()
    return jsonify({'success': True, 'message': f'{routine_type} routine executed'})

@app.route('/api/notifications')
def get_notifications():
    """Get recent notifications"""
    notifications = notification_service.get_recent_notifications()
    return jsonify(notifications)

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    stats = city_controller.get_system_stats()
    return jsonify(stats)

@app.route('/api/devices')
def get_devices():
    """Get all registered devices"""
    devices = city_controller.get_all_devices()
    return jsonify(devices)

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
