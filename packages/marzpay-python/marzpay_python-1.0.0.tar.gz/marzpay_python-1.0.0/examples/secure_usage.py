#!/usr/bin/env python3
"""
Secure MarzPay Python SDK Usage Example

This example shows how to use the MarzPay Python SDK securely
without exposing API credentials in your code.

IMPORTANT: Never commit API credentials to version control!
"""

import os
from marzpay import MarzPay
from marzpay.errors import MarzPayError


def main():
    """Example of secure MarzPay SDK usage"""
    print("MarzPay Python SDK - Secure Usage Example")
    print("=" * 50)
    
    # SECURE WAY: Get credentials from environment variables
    api_key = os.getenv('MARZPAY_API_KEY')
    api_secret = os.getenv('MARZPAY_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ Missing API credentials!")
        print("   Please set the following environment variables:")
        print("   export MARZPAY_API_KEY='your_api_key_here'")
        print("   export MARZPAY_API_SECRET='your_api_secret_here'")
        print("\n   Or create a .env file with your credentials")
        return
    
    try:
        # Initialize the client
        print("🔧 Initializing MarzPay client...")
        client = MarzPay(api_key=api_key, api_secret=api_secret)
        print("✅ Client initialized successfully")
        
        # Test connection
        print("\n🔗 Testing API connection...")
        connection_result = client.test_connection()
        if connection_result["status"] == "success":
            print("✅ API connection successful")
            print(f"   Business: {connection_result['data']['business_name']}")
        else:
            print(f"❌ API connection failed: {connection_result['message']}")
            return
        
        # Example: Phone Verification
        print("\n📱 Phone Verification Example...")
        phone_number = "256759983853"  # Replace with actual phone number
        
        try:
            verification_result = client.phone_verification.verify_phone_number(phone_number)
            if verification_result["success"]:
                print("✅ Phone verification successful")
                print(f"   User: {verification_result['data']['full_name']}")
                print(f"   Phone: {verification_result['data']['phone_number']}")
            else:
                print(f"❌ Phone verification failed: {verification_result['message']}")
        except MarzPayError as e:
            print(f"❌ Phone verification error: {e.message}")
        
        # Example: Money Collection
        print("\n💰 Money Collection Example...")
        collection_params = {
            "phone_number": phone_number,
            "amount": 1000,  # Amount in UGX
            "description": "Payment for services",
            "callback_url": "https://your-app.com/webhook"  # Optional
        }
        
        try:
            collection_result = client.collections.collect_money(collection_params)
            if collection_result["status"] == "success":
                print("✅ Collection request sent successfully!")
                print(f"   Transaction UUID: {collection_result['data']['transaction']['uuid']}")
                print(f"   Reference: {collection_result['data']['transaction']['reference']}")
                print(f"   Status: {collection_result['data']['transaction']['status']}")
            else:
                print(f"❌ Collection failed: {collection_result['message']}")
        except MarzPayError as e:
            print(f"❌ Collection error: {e.message}")
        
        # Example: Money Disbursement
        print("\n💸 Money Disbursement Example...")
        disbursement_params = {
            "phone_number": phone_number,
            "amount": 1000,  # Amount in UGX (minimum)
            "description": "Payment to customer",
            "callback_url": "https://your-app.com/webhook"  # Optional
        }
        
        try:
            disbursement_result = client.disbursements.send_money(disbursement_params)
            if disbursement_result["status"] == "success":
                print("✅ Disbursement request sent successfully!")
                print(f"   Transaction UUID: {disbursement_result['data']['transaction']['uuid']}")
                print(f"   Reference: {disbursement_result['data']['transaction']['reference']}")
                print(f"   Status: {disbursement_result['data']['transaction']['status']}")
            else:
                print(f"❌ Disbursement failed: {disbursement_result['message']}")
        except MarzPayError as e:
            print(f"❌ Disbursement error: {e.message}")
        
        print("\n" + "=" * 50)
        print("🎉 MarzPay Python SDK example completed!")
        print("📚 For more info: https://wallet.wearemarz.com/documentation")
        
    except MarzPayError as e:
        print(f"❌ SDK Error: {e.message}")
        print(f"   Code: {e.code}")
        print(f"   Status: {e.status}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
