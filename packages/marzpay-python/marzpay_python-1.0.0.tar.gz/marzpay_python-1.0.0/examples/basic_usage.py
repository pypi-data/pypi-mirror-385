"""
Basic usage example for MarzPay Python SDK
"""

import os
from marzpay import MarzPay
from marzpay.errors import MarzPayError


def main():
    """Basic usage example"""
    
    # Initialize the client
    client = MarzPay(
        api_key=os.getenv("MARZPAY_API_KEY", "your_api_key"),
        api_secret=os.getenv("MARZPAY_API_SECRET", "your_api_secret"),
    )
    
    print("MarzPay Python SDK - Basic Usage Example")
    print("=" * 50)
    
    # Test connection
    print("\n1. Testing API connection...")
    connection_result = client.test_connection()
    if connection_result["status"] == "success":
        print("✅ API connection successful!")
        print(f"   Business: {connection_result['data']['business_name']}")
    else:
        print(f"❌ API connection failed: {connection_result['message']}")
        return
    
    # Generate a reference
    reference = client.collections.generate_reference()
    print(f"\n2. Generated reference: {reference}")
    
    # Collect money example
    print("\n3. Collecting money from customer...")
    try:
        result = client.collections.collect_money(
            amount=5000,
            phone_number="0759983853",
            reference=reference,
            description="Payment for services - Python SDK Demo"
        )
        
        print("✅ Money collection initiated successfully!")
        print(f"   Collection ID: {result['data']['collection_id']}")
        print(f"   Status: {result['data']['status']}")
        print(f"   Amount: {result['data']['amount']} UGX")
        
        # Get collection details
        collection_id = result['data']['collection_id']
        print(f"\n4. Getting collection details for ID: {collection_id}")
        
        collection_details = client.collections.get_collection(collection_id)
        print("✅ Collection details retrieved!")
        print(f"   Reference: {collection_details['data']['reference']}")
        print(f"   Phone: {collection_details['data']['phone_number']}")
        
    except MarzPayError as e:
        print(f"❌ Error collecting money: {e.message}")
        print(f"   Code: {e.code}")
        print(f"   Status: {e.status}")
    
    # Get available services
    print("\n5. Getting available collection services...")
    try:
        services = client.collections.get_services()
        print("✅ Available services retrieved!")
        print(f"   Services: {len(services.get('data', {}).get('services', []))} available")
        
    except MarzPayError as e:
        print(f"❌ Error getting services: {e.message}")
    
    # Get SDK info
    print("\n6. SDK Information:")
    info = client.get_info()
    print(f"   Name: {info['name']}")
    print(f"   Version: {info['version']}")
    print(f"   Base URL: {info['base_url']}")
    print(f"   Features: {len(info['features'])} available")


if __name__ == "__main__":
    main()


