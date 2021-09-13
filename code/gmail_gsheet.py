# import the required libraries
import base64
import email
import logging
from datetime import datetime

import gspread
import pandas as pd
# import df2gspread as d2g
from df2gspread import df2gspread as d2g
from googleapiclient.discovery import build
from oauth2client import file, client, tools


# import matplotlib.pyplot as plt


# Define the SCOPES. If modifying it, delete the token.pickle file.
#
# FORMAT = '%(asctime)-15s | %(levelname)s | %(clientip)s | %(user)-8s == %(message)s'
# logging.basicConfig(filename='gmail_html_table_read_LOG_' + str(time.strftime('%Y-%m')) + '.log', format=FORMAT)
# rootLogger = logging.getLogger('')
# rootLogger.setLevel(logging.ERROR)
# rootLogger.setLevel(logging.DEBUG)
# rootLogger.setLevel(logging.WARNING)
# rootLogger.setLevel(logging.INFO)
#
# logFormatter = logging.Formatter(FORMAT)
#
# consoleHandler = logging.StreamHandler()
# consoleHandler.setFormatter(logFormatter)
# rootLogger.addHandler(consoleHandler)

def concat_email_text(mime_msg):
    text = ""
    for part in mime_msg.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            text += " "
            text += payload.decode('UTF-8')
    return text

def convertCurrency( input):
	convertionFactor = 86.91

	input = float(input.split(' ')[0])
	input = round(input * convertionFactor,2)

	input = f"{input} INR"

	return  input



def process_raw_msg(raw_msg, msg_id, append=True):
	try:
		data = raw_msg.decode()
		mime_msg = email.message_from_bytes(raw_msg)
	except AttributeError:
		mime_msg = email.message_from_string(raw_msg)

	text = concat_email_text(mime_msg)
	date = text.partition("We confirm the following transactions for: ")[2][0:10]
	date = datetime.strptime(date,"%Y-%m-%d").strftime("%m-%d-%Y")
	df = pd.read_html(text)

	final_df = df[3]
	final_df.dropna(inplace=True)
	print (final_df)
	colName = final_df.columns
	new_df = final_df.filter([colName[0],colName[2],colName[3],'Quantity', 'Price', 'Exchange rate','Charges and fees'], axis=1)

	new_df[colName[2]] = new_df[colName[2]].apply(lambda x: x.split('/')[0])

	# Currecny Conversion
	# new_df["Total cost"] = new_df["Total cost"].apply(convertCurrency)
	new_df["New Exchange"] = new_df["Exchange rate"].apply(lambda  x: x if x > 0.1 else (x * 100) )
	new_df["Total Cost"] = pd.to_numeric(new_df["Price"].apply(lambda x: x.split(' ')[0])) * new_df["New Exchange"]

	new_df['Date']=date

	new_df["Charges and fees"] = pd.to_numeric(new_df["Charges and fees"].apply(lambda x: x.split(' ')[0]))  * new_df["New Exchange"]

	new_df[" "]= " "

	new_df = new_df.filter(['Date','Direction','Instrument/ISIN' , 'Quantity', 'Total Cost'," ", 'Charges and fees', 'Trading Fees'], axis=1)

	new_df['Trading Account'] = "Trading 212"


	# new_df.drop('Price',axis=1,inplace=True)
	print(new_df)
	return new_df


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
		  'https://spreadsheets.google.com/feeds',
		  'https://www.googleapis.com/auth/drive'
		  ]



def htmlString(html):
    result = str(html).replace("\\r", "").replace("\\n", "").strip()
    return result



def getEmails():

	store = file.Storage('../token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('../credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)

	# Connect to the Gmail API
	service = build('gmail', 'v1', credentials=creds)

	gc = gspread.authorize(credentials=creds)


	# request a list of all the messages
	result = service.users().messages().list(
		userId='me', q="from:merinsin78@gmail.com").execute()

	result = service.users().messages().list(
		userId='me').execute()



	# We can also pass maxResults to get any number of emails. Like this:
	# result = service.users().messages().list(maxResults=200, userId='me').execute()
	# messages = result.get('messages')

	messages = []
	if 'messages' in result:
		messages.extend(result['messages'])
	while 'nextPageToken' in result:
		page_token = result['nextPageToken']
		result = service.users().messages().list(userId='me', q="from:merinsin78@gmail.com"
												   , pageToken=page_token).execute()
		messages.extend(result['messages'])
	# messages is a list of dictionaries where each dictionary contains a message id.
	datas = []

	# iterate through all the messages
	count= 0
	for msg in messages:
		# Get the message from its id
		# txt = service.users().messages().get(userId='me', id=msg['id']).execute()

		txt = service.users().messages().get(userId='me', id=msg['id'],
												 format='raw').execute()

		# Use try-except to avoid any Errors
		try:
			msg_str = base64.urlsafe_b64decode(txt['raw'].encode('ascii'))

			if msg_str is not None:
				df = process_raw_msg(msg_str, msg['id'])
				# print Processed message count
				spreadsheet_key = 'red_url_code_goes_here'
				wks_name = 'Master'
				d2g.upload(df, spreadsheet_key, wks_name, credentials=creds, row_names=False)

				print("Processed", count, "of")
				count += 1

		except Exception as e:
			print(f"foo {e}")
			logging.exception("Failed")

if __name__ == '__main__':
	print( "IN main" )
	getEmails()
