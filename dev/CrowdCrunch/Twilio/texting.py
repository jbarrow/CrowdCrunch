from twilio.rest import TwilioRestClient

account = "AC61b168a14cd3c4c2d480006903327506"
token = "3dc14327f5d7a9e883702bdbbe2648aa"
client = TwilioRestClient(account, token)

message = client.messages.create(to="5712257068", from_="+17039978527", body="Fuck yeah!")