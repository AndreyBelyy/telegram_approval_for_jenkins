from telethon import TelegramClient, events, Button



import asyncio
from telethon import TelegramClient, events, Button

api_id = ''
api_hash = ''
group_chat_id = ''

client = TelegramClient('anon', api_id, api_hash)

votes = {}

async def send_voting_message():
    await client.send_message(group_chat_id, "Please vote:",
                              buttons=[
                                  [Button.inline('Approve', b'approve'),
                                   Button.inline('Decline', b'decline')]
                              ])

@client.on(events.CallbackQuery)
async def callback_handler(event):
    user = await event.get_sender()
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "no username"
    vote = event.data.decode('utf-8')

    # Send a message to the chat showing the user's choice with full name and username
    choice = 'approved' if vote == 'approve' else 'declined'
    await client.send_message(group_chat_id, f"{full_name} ({username}) has {choice}.")

    # Record the vote
    votes[user.id] = vote

    # Respond to the callback query (optional)
    await event.answer(f"You voted {choice}")

async def announce_results():
    # Wait for one minute
    await asyncio.sleep(60)

    # Tally the votes
    approve_count = sum(v == 'approve' for v in votes.values())
    decline_count = sum(v == 'decline' for v in votes.values())

    # Announce the results
    results_message = f"Voting results:\nApprove: {approve_count}\nDecline: {decline_count}"
    await client.send_message(group_chat_id, results_message)

async def main():
    await client.start()
    await send_voting_message()

    # Run the results announcement in parallel
    asyncio.create_task(announce_results())

    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())

