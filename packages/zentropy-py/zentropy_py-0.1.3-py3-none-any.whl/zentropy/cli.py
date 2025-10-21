import argparse
from .client import Client

def main():
    parser = argparse.ArgumentParser(description='Zentropy Client CLI')
    parser.add_argument('--host', default='127.0.0.1', help='Server host')
    parser.add_argument('--port', type=int, default=6383, help='Server port')
    parser.add_argument('--password', help='Authentication password')
    
    args = parser.parse_args()
    
    client = Client(host=args.host, port=args.port, password=args.password)
    
    try:
        if client.ping():
            print("Connected to Zentropy server successfully!")
        else:
            print("Connection failed!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    main()