import os
from keep_alive import keep_alive  
keep_alive()
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Bot Token and Allowed Users
BOT_TOKEN = "7932946161:AAETXfSjYQNwcECWYzYAKeTn9fnV_fYAGgQ"
ALLOWED_USERS = {7848399218,7770152439,5974999747}  # Replace with actual user IDs

# Dictionary to store user file queues
user_file_queues = {}

# Function to customize the text file
def remove_unwanted_lines(content):
    unwanted_keywords = ["mKeyword:", "mauthgop", "mDate:"]  # Define keywords to search for
    filtered_content = "\n".join(
        [line for line in content.split("\n") if not any(keyword in line for keyword in unwanted_keywords)]
    )
    return filtered_content
    
def customize_text(content, query_type):
    # Remove the lines containing "📝 Query:Garena" or "📝 Query:Moonton"
    content = "\n".join([line for line in content.split("\n") if "📝 Query:Garena" not in line and "📝 Query:Moonton" not in line])
def customize_text(content, query_type):
    # Remove lines containing the "[" character
    content = "\n".join([line for line in content.split("\n") if "[" not in line])

    # Remove lines containing "Query" (if any)
    content = "\n".join([line for line in content.split("\n") if "Query" not in line])

    # Only keep lines containing ":"
    filtered_content = "\n".join([line for line in content.split("\n") if ":" in line])

    # Add header and query type with new layout
    styled_content = "════════════════════════════════════\n"
    styled_content += "       ᴘᴏᴡᴇʀᴇᴅ ʙʏ: ℕØ𝕌ℂℍ\n"
    styled_content += "════════════════════════════════════\n\n"

    if query_type == "ML":
        styled_content += "📝 Query: Moonton\n\n"
    elif query_type == "CODM":
        styled_content += "📝 Query: Garena\n\n"
    elif query_type == "Roblox":
        styled_content += "📝 Query: Roblox\n\n"
    elif query_type == "Codashop":
        styled_content += "📝 Query: Codashop\n\n"

    styled_content += "════════════════════════════════════\n"

    # Format usernames and passwords
    for line in filtered_content.split("\n"):
        if ":" in line:
            username, password = line.split(":", 1)
            styled_content += f"➤ {username.strip()}:{password.strip()}\n"
        else:
            styled_content += line + "\n"

    return styled_content

# Function to check if user is authorized
def is_allowed_user(update):
    return update.message.from_user.id in ALLOWED_USERS

# Handler for processing received or forwarded .txt files
async def handle_document(update: Update, context):
    message = update.message or update.edited_message

    if not is_allowed_user(update):
        await message.reply_text("❌ You are not authorized to use this bot.")
        return

    document = message.document

    if document.mime_type != "text/plain":
        await message.reply_text("❌ Please send a valid .txt file.")
        return

    user_id = message.from_user.id

    # Download the file
    file_path = f"{document.file_id}.txt"
    new_file = await context.bot.get_file(document.file_id)
    await new_file.download_to_drive(file_path)

    # Store the file in queue for processing
    if user_id not in user_file_queues:
        user_file_queues[user_id] = []
    user_file_queues[user_id].append(file_path)

    # If this is the first file in the queue, start processing
    if len(user_file_queues[user_id]) == 1:
        await ask_game_selection(update, context, user_id)

# Function to ask for game selection
async def ask_game_selection(update: Update, context, user_id):
    keyboard = [
    [InlineKeyboardButton("ML", callback_data=f"ML_{user_id}")],
    [InlineKeyboardButton("CODM", callback_data=f"CODM_{user_id}")],
    [InlineKeyboardButton("Roblox", callback_data=f"Roblox_{user_id}")],
    [InlineKeyboardButton("Codashop", callback_data=f"Codashop_{user_id}")]
]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=user_id, text="📌 Select the game for this file:", reply_markup=reply_markup)

# Callback handler for ML/CODM selection
async def handle_game_selection(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Extract selection and user ID
    selection, user_id = query.data.split("_")
    user_id = int(user_id)

    if user_id not in user_file_queues or not user_file_queues[user_id]:
        await query.message.reply_text("⚠️ No file found. Please send a .txt file first.")
        return

    # Get the next file from the queue
    file_path = user_file_queues[user_id].pop(0)

    # Hide the buttons after selection
    await query.edit_message_text(text=f"📌 You selected: {selection}. Customizing the file...")

    # Read and process the text file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    styled_content = customize_text(content, selection)

    # Rename the output file based on game selection
    if selection == "ML":
        new_filename = "ɴØᴜᴄʜ_ᴍʟ.txt"
    elif selection == "CODM":
        new_filename = "ɴØᴜᴄʜ_ᴄᴏᴅᴍ.txt"
    elif selection == "Roblox":
        new_filename = "ɴØᴜᴄʜ_roblox.txt"
    elif selection == "Codashop":
        new_filename = "ɴØᴜᴄʜ_codashop.txt"
    
    with open(new_filename, "w", encoding="utf-8") as file:
        file.write(styled_content)

    # Send the customized file to the user
    await context.bot.send_document(chat_id=user_id, document=open(new_filename, "rb"))

    # Delete the original and customized files after sending
    os.remove(file_path)
    os.remove(new_filename)

    # If more files are in the queue, process the next one
    if user_file_queues[user_id]:
        await ask_game_selection(update, context, user_id)
    else:
        # Clear queue after processing all files
        del user_file_queues[user_id]

# Start command handler
async def start(update: Update, context):
    if not is_allowed_user(update):
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    await update.message.reply_text("Send me a .txt file to customize.")

# Main function to run the bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(handle_game_selection))

    # Run the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    