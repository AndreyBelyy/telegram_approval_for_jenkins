import subprocess
import sys

# Function to check and install the required package
def install_package(package):
    try:
        __import__(package)
    except ImportError as e:
        print(f"Package {package} not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check and install Telethon if needed
install_package("telethon")

from telethon import TelegramClient, events, sync

# Define the necessary credentials
api_id = 
api_hash = ''
group_chat_id = 
bot_token = ''

# Initialize the client
client = TelegramClient('anon', api_id, api_hash)

# Function to send a message
async def send_message(text):
    async with client:
        await client.send_message(group_chat_id, text)

# The text message to send, passed as a command line argument
message_text = ' '.join(sys.argv[1:])  # Joins all arguments into a single string

# Run the client and send the message
client.loop.run_until_complete(send_message(message_text))
