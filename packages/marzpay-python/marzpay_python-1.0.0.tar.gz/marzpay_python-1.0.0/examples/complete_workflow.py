#!/usr/bin/env python3
"""
Complete MarzPay Python SDK Workflow Example

This example demonstrates all the major features of the MarzPay Python SDK:
- Collections (collecting money from customers)
- Disbursements (sending money to customers)
- Phone Verification (verifying customer phone numbers)
- Webhook handling
- Error handling
- Utility functions

For more information, visit: https://wallet.wearemarz.com/documentation
"""

import os
import json
from marzpay import MarzPay
from marzpay.errors import MarzPayError


def main():
    """Main workflow example"""
    print("MarzPay Python SDK - Complete Workflow Example")
    print("=" * 50)
    
    # Initialize the client
    # In production, use environment variables for credentials
    api_key = os.getenv('MARZPAY_API_KEY', 'your_api_key_here')
    api_secret = os.getenv('MARZPAY_API_SECRET', 'your_api_secret_here')
    
    try:
        client = MarzPay(api_key=api_key, api_secret=api_secret)
        print("✓ MarzPay client initialized successfully")
    except MarzPayError as e:
        print(f"✗ Failed to initialize client: {e.message}")
        return
    
    # Test connection
    print("\n1. Testing API Connection...")
    connection_result = client.test_connection()
    if connection_result["status"] == "success":
        print("✓ API connection successful")
        print(f"  Business: {connection_result['data']['business_name']}")
    else:
        print(f"✗ API connection failed: {connection_result['message']}")
        return
    
    # Phone Verification
    print("\n2. Phone Number Verification...")
    try:
        # Get service info first
        service_info = client.phone_verification.get_service_info()
        print(f"✓ Service info: {service_info['data']['service_name']}")
        
        # Check subscription status
        subscription = client.phone_verification.get_subscription_status()
        if subscription['data']['is_subscribed']:
            print("✓ Phone verification service is subscribed")
            
            # Verify phone number
            verification_result = client.phone_verification.verify_phone_number("256759983853")
            if verification_result["success"]:
                print(f"✓ Phone verified: {verification_result['data']['full_name']}")
            else:
                print(f"✗ Phone verification failed: {verification_result['message']}")
        else:
            print("✗ Phone verification service not subscribed")
    except MarzPayError as e:
        print(f"✗ Phone verification error: {e.message}")
    
    # Collections (Collect Money)
    print("\n3. Collecting Money from Customer...")
    try:
        collection_params = {
            "phone_number": "256759983853",
            "amount": 1000,  # 1000 UGX
            "description": "Test payment for services",
            "callback_url": "https://your-app.com/webhook"
        }
        
        collection_result = client.collections.collect_money(collection_params)
        if collection_result["status"] == "success":
            print("✓ Money collection initiated successfully")
            transaction_uuid = collection_result["data"]["transaction"]["uuid"]
            print(f"  Transaction UUID: {transaction_uuid}")
            print(f"  Reference: {collection_result['data']['transaction']['reference']}")
            print(f"  Status: {collection_result['data']['transaction']['status']}")
            
            # Get collection details
            print("\n4. Getting Collection Details...")
            details = client.collections.get_collection_details(transaction_uuid)
            print(f"✓ Collection details retrieved")
            print(f"  Status: {details['data']['transaction']['status']}")
            
        else:
            print(f"✗ Collection failed: {collection_result['message']}")
    except MarzPayError as e:
        print(f"✗ Collection error: {e.message}")
    
    # Disbursements (Send Money)
    print("\n5. Sending Money to Customer...")
    try:
        disbursement_params = {
            "phone_number": "256759983853",
            "amount": 500,  # 500 UGX
            "description": "Refund payment",
            "callback_url": "https://your-app.com/webhook"
        }
        
        disbursement_result = client.disbursements.send_money(disbursement_params)
        if disbursement_result["status"] == "success":
            print("✓ Money disbursement initiated successfully")
            transaction_uuid = disbursement_result["data"]["transaction"]["uuid"]
            print(f"  Transaction UUID: {transaction_uuid}")
            print(f"  Reference: {disbursement_result['data']['transaction']['reference']}")
            print(f"  Status: {disbursement_result['data']['transaction']['status']}")
            
            # Get disbursement details
            print("\n6. Getting Disbursement Details...")
            details = client.disbursements.get_send_money_details(transaction_uuid)
            print(f"✓ Disbursement details retrieved")
            print(f"  Status: {details['data']['transaction']['status']}")
            
        else:
            print(f"✗ Disbursement failed: {disbursement_result['message']}")
    except MarzPayError as e:
        print(f"✗ Disbursement error: {e.message}")
    
    # Utility Functions
    print("\n7. Testing Utility Functions...")
    
    # Phone number formatting
    formatted_phone = client.format_phone_number("0759983853")
    print(f"✓ Phone formatting: 0759983853 -> {formatted_phone}")
    
    # Phone number validation
    is_valid = client.is_valid_phone_number("256759983853")
    print(f"✓ Phone validation: 256759983853 is {'valid' if is_valid else 'invalid'}")
    
    # Reference generation
    ref1 = client.generate_reference()
    ref2 = client.generate_reference_with_prefix("PAY")
    print(f"✓ Generated references: {ref1[:8]}..., {ref2}")
    
    # Webhook Handling Example
    print("\n8. Webhook Handling Example...")
    
    # Simulate a webhook payload
    webhook_payload = {
        "type": "collection",
        "data": {
            "transaction_id": "test-tx-123",
            "status": "completed",
            "amount": 1000
        },
        "timestamp": "2024-01-20T10:30:00Z"
    }
    
    try:
        # Process webhook
        webhook_result = client.callback_handler.handle_callback(webhook_payload)
        print("✓ Webhook processed successfully")
        print(f"  Type: {webhook_result['type']}")
        print(f"  Transaction ID: {webhook_result['transaction_id']}")
        print(f"  Status: {webhook_result['status']}")
        print(f"  Success: {webhook_result['success']}")
    except MarzPayError as e:
        print(f"✗ Webhook processing error: {e.message}")
    
    # Get Available Services
    print("\n9. Getting Available Services...")
    try:
        # Collection services
        collection_services = client.collections.get_services()
        print(f"✓ Collection services: {len(collection_services.get('data', {}).get('services', []))} available")
        
        # Disbursement services
        disbursement_services = client.disbursements.get_services()
        print(f"✓ Disbursement services: {len(disbursement_services.get('data', {}).get('services', []))} available")
        
    except MarzPayError as e:
        print(f"✗ Services error: {e.message}")
    
    # SDK Information
    print("\n10. SDK Information...")
    info = client.get_info()
    print(f"✓ SDK: {info['name']} v{info['version']}")
    print(f"  Features: {len(info['features'])} available")
    print(f"  Base URL: {info['base_url']}")
    
    print("\n" + "=" * 50)
    print("MarzPay Python SDK workflow completed successfully!")
    print("For more information, visit: https://wallet.wearemarz.com/documentation")


if __name__ == "__main__":
    main()
