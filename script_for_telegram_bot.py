import json
import requests
from shapely.geometry import shape, Point
import pandas as pd
import telebot
import io

# Step 1: Load the JSON file containing the district polygons
json_url = "https://raw.githubusercontent.com/akilbekov/almaty.geo.json/master/almaty-districts.geo.json"
response = requests.get(json_url)
json_data = json.loads(response.text)

# Step 2: Extract the district polygons from the JSON data
districts = []
for feature in json_data['features']:
    polygon = shape(feature['geometry'])
    district_name = feature['properties']['name']
    districts.append((district_name, polygon))


def process_xlsx(message):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_bytes = bot.download_file(file_info.file_path)
        excel_data = io.BytesIO(file_bytes)
        df = pd.read_excel(excel_data)

        # Check if the required columns exist in the DataFrame
        if 'x' not in df.columns or 'y' not in df.columns:
            bot.reply_to(message, "Error: Required columns 'x' or 'y' not found in the XLSX file.")
            return

        # Step 4: Assign district names based on the coordinates
        district_names = []
        for index, row in df.iterrows():
            try:
                point = Point(row['x'], row['y'])
            except KeyError:
                bot.reply_to(message, f"Error: Missing coordinate data for row {index + 2}.")
                return
            district_name = None
            for name, district in districts:
                if district.contains(point):
                    district_name = name
                    break
            if district_name is None:
                district_name = "Unknown"  # Assign a default value for unknown districts
            district_names.append(district_name)

        # Step 5: Add the district names as a new column in the DataFrame
        df['district'] = district_names

        # Convert DataFrame to XLSX
        output_file = 'Output.xlsx'
        df.to_excel(output_file, index=False)

        # Send the output file to the user
        with open(output_file, 'rb') as file:
            bot.send_document(message.chat.id, file)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")


# Set up the Telegram bot
token = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=['document'])
def handle_xlsx(message):
    process_xlsx(message)


bot.polling()

