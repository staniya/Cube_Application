import string
import sys

from datetime import datetime
import traceback
import abc
import logging
import requests

from Cube_Skill.ask import alexa

# just for testing
from Cube_Skill.ask.deployment_test.FAQIntent_dictionary import html_text
from Cube_Skill.lambda_function import get_cube_launch_intent_handler, get_cube_otp_intent_handler


# authentication_helpers
def login_welcome(request):

    headers = {'Authorization': 'Basic Y3ViZWFwcGJhc2ljOmN1YmVhcHBiYXNpY0AyMDkwKQ==',
               'Content-type': 'application/x-www-form-urlencoded', 'Content-Length': '60'}

    payload = {'identifier': 'user', 'grant_type': 'client_credentials', 'passcode': 'admin'}

    session = requests.Session()

    resp = session.post("https://api.bankoncube.com/v1/api/oauth/token", headers=headers, data=payload)

    try:

        if resp.status_code == 200:
            # (status=status.HTTP_201_CREATED):
            speech_output = "Welcome to Cube. To get you started, please tell me the phone number that you " \
                            "used to register with Cube. " \
                            "Say it in the following format: " + "<say-as interpret-as=\"digits\">" + "123 " + \
                            "</say-as>" + "<say-as interpret-as=\"digits\">" + "456" + "</say-as>" + \
                            "<say-as interpret-as=\"digits\">" + "7890" + "</say-as>"

            card = alexa.create_card(title="Cube Welcome Page", subtitle="Test card output",
                                     content="Welcome to Cube. To get you started, please tell me the "
                                             "phone number that you used to register with Cube. Say it in the "
                                             "following format: 123 456 7890")

            response1 = alexa.create_response(message=speech_output,
                                              reprompt_message="I did not hear you",
                                              end_session=False, card_obj=card)

            return response1

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


def login_phone_number(request):
    resp2, response = get_cube_launch_intent_handler(request)

    try:

        if resp2.status_code == 200:
            # (status=status.HTTP_200_OK):

            speech_output = "What is the OTP?"

            card = alexa.create_card(title="Cube Launch", subtitle=None,
                                     content=speech_output)

            response2 = alexa.create_response(message=speech_output,
                                              reprompt_message="I did not hear you",
                                              end_session=False, card_obj=card)
            return response2

        else:
            print(resp2.status_code)

            card = alexa.create_card(title="Cube Launch", subtitle="We couldn't connect to our server",
                                     content=None)

            return alexa.create_response(message=None,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp2.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp2.status_code))

        sys.exit()


def login_otp(request):
    resp3 = get_cube_otp_intent_handler(request)

    try:

        if resp3.status_code == 200:
            # resp3(status=status.HTTP_200_OK):

            resp_dict = resp3.json()

            access_token = resp_dict['access_token']

            # TODO save acess_token credentials here
            speech_output = "Log-in Successful. You can ask me questions. Now, what can I help you with?"

            card = alexa.create_card(title="Welcome", subtitle=None,
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="For instructions on what you can say, please say help me!",
                                         end_session=False, card_obj=card)

        else:

            print(resp3.status_code)

            speech_output = "Connection Error! Http status Code {}".format(resp3.status_code)

            card = alexa.create_card(title="Failed", subtitle=None,
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp3.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp3.status_code))

        sys.exit()


# API connections


# TODO for the APIs below, I have to add the access token to use them from above
# TODO could pass Cube app version and unique device id as a header
def money_details():
    headers = {'Authorization': 'Bearer 5dc8408b-8c7e-4982-b0db-52b9c85bceac'}

    session = requests.Session()

    return session.get("https://apis.bankoncube.com/m3/core/money_details/", headers=headers)


def mutual_funds_api():
    headers = {'Authorization': 'Bearer 5dc8408b-8c7e-4982-b0db-52b9c85bceac'}

    session = requests.Session()

    return session.get("https://api.bankoncube.com/m3/core/v5/funds/?account=true", headers=headers)


def bills_api():
    headers = {'Authorization': 'Bearer 5dc8408b-8c7e-4982-b0db-52b9c85bceac'}

    session = requests.Session()

    return session.get("https://cubeadmin.bankoncube.com/biller/v1/bills", headers=headers)


# If no intent is found and the request type is not found (refer to alexa_io.py)
def on_processing_error(exc):
    '''
    :param exc exception instance
    '''

    speech_output = "Cube is having difficulty fulfilling your request."

    if exc:
        speech_output = "I am having difficulty fulfilling your request. {0}".format(exc.message)

    card = alexa.create_card(title="Cube Error", subtitle=None,
                             content=speech_output)

    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True, card_obj=card)


# removing digits for slot ['numberOne']
def remove_digits(s):
    return s[2:]


# Bill Amount Function
def get_bill_amount_dict():
    bill_amount_dict = {}

    resp = bills_api()

    resp_dict = resp.json()

    for info in range(0, len(resp_dict)):

        bill_amount = resp_dict['amount']

        fee_description = resp_dict['title']

        if fee_description in bill_amount_dict and fee_description is not None:

            bill_amount_dict[fee_description].append(bill_amount)

        else:

            bill_amount_dict[fee_description] = bill_amount

    return bill_amount_dict


# Expenses/BillDue Function
def get_expenses_dict():
    expenses_dict = {}

    resp = bills_api()

    resp_dict = resp.json()

    for items in range(0, len(resp_dict['stats'])):

        dueDate = (resp_dict['stats']['dueDate']) / 1000

        dueAmount = resp_dict['stats']['dueAmount']

        if dueDate in expenses_dict:

            expenses_dict[dueDate].append(dueAmount)

        else:

            expenses_dict[dueDate] = dueAmount

    return expenses_dict


# string concatenation

def string_addition_expenses(dict):
    for k, v in dict.items():
        return "{0} rupees on {1}".format(v, k)


def string_addition_bill(dict):
    for k, v in dict.items():
        k = string.capwords(k)

        return "{0}: {1}".format(k, v)


# Introductory Statements
introduction = {
    'get_cube_savings': 'This is how much money you have with Cube: ',
    'get_cube_mutual_funds': 'This is the total amount you have in Mutual Funds: ',
    'get_cube_mutual_funds_individual': 'This is how much money you have ',
    'get_cube_bill_amount': 'This is the bill amount ',
    'get_cube_bill_due': 'Your next bills are',
    'get_cube_expenses': 'Your next big expense ',
    'get_cube_helping_number': 'The number of people you helped is: ',
    'get_cube_profit': 'Your profit is: ',
    'get_cube_helping': 'This is the amount you donated towards charity: '
}


# get dictionary values
def find_the_value(key):
    if key in introduction:
        return introduction[key]


def find_the_value_html(key):
    if key in html_text:
        return html_text[key]


class AlexaBaseHandler(object):
    def __init__(self, app_id=None, log_level=logging.INFO):
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)
        self.app_id = app_id

    def _get_intent(self, intent_request):
        if 'intent' in intent_request:
            return intent_request['intent']
        else:
            return None

    def _get_intent_name(self, intent_request):
        intent = self._get_intent(intent_request)
        intent_name = None
        if intent is not None and 'name' in intent:
            intent_name = intent['name']

        return intent_name

    # handle Amazon built-in intents
    def _handle_amazon_intent(self, event, context):
        """
        Method dynamically calls AMAZON built in intents.
        For example, for the AMAZON.YesIntent, this method will dynamically call
        a method of the form:
        on_yes_intent(intent_request, session)

        This allows for this base class to be extensible to handle the new
        Amazon Alexa Streaming Playback support without having to specially
        look for the streaming intent names.
        :param event:
        :param context:
        """
        response = None

        intent_name = self._get_intent_name(event['request'])
        if intent_name is not None and intent_name.startswith("AMAZON."):
            intent_method_name = "on_{0}_intent".format(intent_name.split(".")[1].replace("Intent", "").lower())
            self.logger.debug("_handle_amazon_intent: {0}".format(intent_method_name))

            if hasattr(self, intent_method_name):
                try:
                    response = getattr(self, intent_method_name)(event['request'], event['session'])
                except:
                    self.logger.error("Traceback Exception {0}".format(traceback.format_exc()))
                    self.logger.error("ERROR: _handle_amazon_intent: {0}".format(intent_method_name))
                    raise

            else:
                raise NotImplementedError("No method with name: {0} exists in class".format(intent_method_name))

        return response

    # processing error
    @abc.abstractmethod
    def on_processing_error(self, event, context, exc):
        """
        If an unexpected error occurs during the process_request method
        this handler will be invoked to give the concrete handler
        an opportunity to respond gracefully

        :param exc exception instance
        :return: the output of _build_response
        """
        pass

    # --------------------------------------------------------
    # --------------- Main Processing Entry Point  -----------
    # --------------------------------------------------------
    def process_request(self, event, context):
        """
        Helper method to process the input Alexa request and
        dispatch to the appropriate on_ handler
        :param event:
        :param context:
        :return: response from the on_ handler
        """
        self.logger.debug("process_request: event: {0}".format(event))

        try:
            request_type = event['request']['type']
            self.logger.debug("event[request][type]: {0}".format(request_type))
        except:
            request_type = None

        # if its a new session, run the new session code
        try:
            response = None
            # regardless of whether its new, handle the request type
            if request_type == "IntentRequest":
                # Only handle IntentRequest here... all others in the else block
                intent_name = self._get_intent_name(event['request'])
                if intent_name is not None and intent_name.startswith("AMAZON."):
                    response = self._handle_amazon_intent(event, context)
        except Exception as exc:
            self.logger.error("Error in process_request: {0}".format(traceback.format_exc()))
            response = self.on_processing_error(event, context, exc)

        return response


# Data Values for Testing. When using APIs, these are useless
data = [
    '10000 rupees',
    '50000 rupees',
    '100000 rupees',
    '1000 rupees',
    '4000 rupees',
    '5000 rupees',
]

dates = [
    'March 13, 2018',
    'January 1, 2018',
    'Feburary 20, 2018',
    'August 30, 2018',
    'March 15, 2018',
    'July 20, 2018',
    'June 10, 2018'
]

yes_no = [
    'yes you did',
    'no you did not',
]

numbers = [
    '5',
    '40',
    '100',
    '10',
    '15',
    '30',
    '45',
    '50',
    '80',
    '20',
]
