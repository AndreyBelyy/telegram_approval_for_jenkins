import asyncio
from telethon import TelegramClient, events, Button
from telethon import events

# Your Telegram API ID, API Hash, and group chat ID
api_id = '29880805'
api_hash = '7499a71417d05232299609c8e9ad0bd0'
group_chat_id = -1001572494479  # Replace with your group's chat ID

# Initialize the Telegram Client
client = TelegramClient('anon', api_id, api_hash)

async def send_message_with_inline_buttons():
    await client.send_message(group_chat_id, 'Please approve or decline',
                              buttons=[
                                  [Button.inline('Approve', b'approve'),
                                   Button.inline('Decline', b'decline')]
                              ])


@client.on(events.CallbackQuery)
async def callback_handler(event):
    # Decode the payload to get the button text
    button_data = event.data.decode('utf-8')

    # Get the sender of the callback query
    sender = await event.get_sender()
    sender_full_name = getattr(sender, 'full_name', 'Someone')
    sender_username = getattr(sender, 'username', None)

    # Construct the name display string
    name_display = sender_full_name
    if sender_username:
        name_display += f" (@{sender_username})"

    # Respond to the callback query to give user feedback
    await event.answer(f'You selected {button_data}')

    # Send a message to the chat indicating the action
    await client.send_message(group_chat_id, f"{name_display} has chosen to {button_data}.")



async def main():
    await client.start()
    await send_message_with_inline_buttons()
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
