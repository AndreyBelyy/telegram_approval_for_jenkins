import subprocess
import os
import sys
import asyncio
import datetime
from telethon import TelegramClient, events, Button
import logging

# Function to check and install required packages
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# List of required packages
required_packages = ['telethon']

# Install required packages
for package in required_packages:
    install_package(package)

# Ensure that a message argument is provided
if len(sys.argv) < 2:
    print("Usage: python script.py 'Please, make a vote'")
    sys.exit(1)

# Custom message from the command line
voting_message = sys.argv[1]

api_id = 
api_hash = ''
group_chat_id = 
bot_token = ''
client = TelegramClient('anon', api_id, api_hash).start(bot_token=bot_token)
# File to be read and sent
file_path = './2.txt'
# Ensure your file exists
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

# Set up basic logging to stdout
logging.basicConfig(level=logging.INFO)
votes = {}
before_extension_votes = {}  # To store votes before extension
after_extension_votes = {}  # To store votes after extension
extension_time = 0  # To store the extended voting time (in seconds)
results_announced = False  # To track if results are announced
initial_voting_duration = 30

async def send_file():
    # Send the file to the chat
    await client.send_file(group_chat_id, file_path)

with client:
    client.loop.run_until_complete(send_file())


async def ask_voting_duration():
    await client.send_message(group_chat_id, "Choose the duration for voting:",
                              buttons=[
                                  [Button.inline('1 min', b'1min'),
                                   Button.inline('3 min', b'3min'),
                                   Button.inline('5 min', b'5min'),
                                   Button.inline('10 min', b'10min')]
                              ])




async def send_voting_message():
    await client.send_message(group_chat_id, voting_message,
                              buttons=[
                                  [Button.inline('Approve', b'approve'),
                                   Button.inline('Decline', b'decline')]
                              ])


@client.on(events.CallbackQuery)
async def callback_handler(event):
    global votes, before_extension_votes, after_extension_votes, extension_time

    user = await event.get_sender()
    user_id = user.id
    data = event.data.decode('utf-8')

    # Check if the callback data is for voting duration setting
    if data.endswith('min'):
        # Handle voting duration setting
        await duration_handler(event, user_id, data)
    elif data in ['approve', 'decline', 'yes', 'no']:
        # Handle voting or voting end confirmation
        await handle_vote(event, user_id, data, user)
    else:
        # Handle other callback data if necessary
        pass

async def duration_handler(event, user_id, duration_choice):
    global initial_voting_duration, extension_time
    message = await event.get_message()

    if user_id in [483998347, 1535811250]:  # Admin user IDs
        duration_minutes = int(duration_choice[:-3])  # Extracting minutes part
        initial_voting_duration = duration_minutes * 60
        extension_time = int(datetime.datetime.now().timestamp()) + initial_voting_duration
        await message.edit(f"Voting duration set to {duration_minutes} minutes. Starting voting...", buttons=None)
        await send_voting_message()
    else:
        await event.answer("You're not authorized to set the duration.", alert=True)

async def handle_vote(event, user_id, vote, user):
    current_timestamp = int(datetime.datetime.now().timestamp())
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "no username"
    choice_text = 'approved' if vote == 'approve' else 'declined'

    if vote in ['approve', 'decline']:
        if user_id not in votes or user_id in [483998347, 1535811250]:
            # It's a new vote or a vote from a special user, process it
            votes[user_id] = vote  # Record the vote

            # Determine if it's before or after the extension
            if current_timestamp < extension_time:
                before_extension_votes[user_id] = vote
            else:
                after_extension_votes[user_id] = vote

            # Send a public message if it's a new vote or if a special user changes their vote
            public_message = f"{full_name} ({username}) has {choice_text} the proposal."
            await client.send_message(group_chat_id, public_message)

            # Send a confirmation to the user
            await event.answer(f"You have {choice_text} the proposal.")
        else:
            # The user has already voted and is not allowed to vote multiple times
            await event.answer("You have already voted.", alert=True)

##async def prompt_voting_end():
##    global extension_time
##    message = await client.send_message(group_chat_id, "Voting ends?", buttons=[
##        [Button.inline('Yes', b'yes'), Button.inline('No', b'no')]
##    ])
##    extension_time = int(message.date.timestamp())

##@client.on(events.CallbackQuery)
##async def confirm_handler(event):
##    global results_announced
##    message = await event.get_message()
##    user_id = event.sender_id
##    data = event.data.decode('utf-8')
##
##    if user_id in [483998347, 1535811250] and data == 'yes':
##        await message.edit("Finalizing voting...", buttons=None)
##        await announce_results()
##    elif user_id in [483998347, 1535811250] and data == 'no':
##        await message.edit("Extending voting time...", buttons=None)
##        await client.send_message(group_chat_id, "Extend voting by:",
##                                    buttons=[
##                                        [Button.inline('1 min', b'1min'),
##                                         Button.inline('5 min', b'5min'),
##                                         Button.inline('10 min', b'10min')]
##                                    ])

##@client.on(events.CallbackQuery)
##async def extend_handler(event):
##    global extension_time
##    message = await event.get_message()
##    user_id = event.sender_id
##    vote_extension = event.data.decode('utf-8')
##
##    if user_id in [483998347, 1535811250] and vote_extension in ['1min', '5min', '10min']:
##        extend_time = int(vote_extension[:-3]) * 60
##        await message.edit(f"Voting extended for {extend_time // 60} minutes.", buttons=None)
##        await asyncio.sleep(extend_time)
##
##        # Check if results should be announced after the extension
##        await announce_results()
##        await client.disconnect()
##    else:
##        await event.answer("You're not authorized to extend the voting time.", alert=True)

@client.on(events.NewMessage(pattern='/endvote', chats=group_chat_id))
async def end_voting_handler(event):
    global results_announced
    if event.sender_id in [483998347, 1535811250]:  # Replace with your Telegram user ID
        if not results_announced:
            await announce_results()
            results_announced = True
    else:
        await event.respond("You don't have the permission to end the voting.")

async def announce_results():
    global results_announced
    if results_announced:
        return  # Avoid announcing results multiple times

    results_announced = True  # Mark results as announced

    # Combine votes from both periods
    combined_votes = {**before_extension_votes, **after_extension_votes}

    # Count the votes
    approve_count = sum(1 for v in combined_votes.values() if v == 'approve')
    decline_count = sum(1 for v in combined_votes.values() if v == 'decline')

    # Announce the results
    results_message = f"Voting results:\nApprove: {approve_count}\nDecline: {decline_count}"
    await client.send_message(group_chat_id, results_message)

    photo_path = 'approve.png' if approve_count > decline_count else 'decline.png'
    await client.send_file(group_chat_id, photo_path)

    # If you need to stop the script with an exit code, you can do so here
    # Use a positive number like 1 to indicate failure, or 0 to indicate success
    exit_code = 0 if approve_count > decline_count else 1
    sys.exit(exit_code)

async def main():
    global results_announced, extension_time

    logging.info("Starting the client...")
    await client.start()

    logging.info("Sending the file...")
    #await send_file()
    logging.info("File has been sent.")

    logging.info("Asking for voting duration...")
    await ask_voting_duration()

    # Wait for the voting duration handler to set the voting duration
    while initial_voting_duration == 0:
        await asyncio.sleep(1)

    #logging.info("Waiting for the initial voting duration...")
    #await asyncio.sleep(initial_voting_duration)

    #logging.info("Sending the voting message...")
    #await send_voting_message()

    logging.info("Voting period has started...")
    extension_time = int(datetime.datetime.now().timestamp()) + initial_voting_duration

    # Wait for the voting period to end or for an extension
    while not results_announced:
        current_timestamp = int(datetime.datetime.now().timestamp())
        if current_timestamp >= extension_time:
            await announce_results()
            break

        await asyncio.sleep(1)

    logging.info("Voting concluded. Disconnecting the client.")
    await client.disconnect()

if __name__ == '__main__':
    logging.info("Running the main function...")
    client.loop.run_until_complete(main())
    logging.info("Main function has completed.")

