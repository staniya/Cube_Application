import logging
import os
import datetime
import time

from flask import Flask, json, render_template
from flask_ask import Ask, request, session, question, statement

import requests
import random
import string
import sys

from Cube_Skill.Cube_Application import remove_digits, find_the_value, \
    AlexaBaseHandler, mutual_funds_api, money_details, bills_api, get_expenses_dict, \
    get_bill_amount_dict, string_addition_expenses, string_addition_bill, find_the_value_html
from Cube_Skill.ask import alexa

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def lambda_handler(request_obj):
    """
    This is the main function to enter to enter into this code.
    If you are hosting this code on AWS Lambda, this should be the entry point.
    Otherwise your server can hit this code as long as you remember that the
    input 'request_obj' is JSON request converted into a nested python object.
    """
    logging.info("Executing alexa_handler for AlexaDeploymentHandler")

    # if you are testing this in lambda, comment out the two lines below because it won't work
    if app.config['ASK_APPLICATION_ID'] != "amzn1.ask.skill.1c281255-10e6-41c7-abd8-5309b8b2152c":
        raise ValueError("Invalid Application ID")

    else:
        return alexa.route_request(request_obj)


@alexa.default
def default_handler(request):
    """ The default handler gets invoked if no handler is set for a request type """
    return launch_request_handler(request)


@alexa.request("LaunchRequest")
def launch_request_handler(request):
    ''' Handler for LaunchRequest '''
    # TODO I have to pass the authentication page here
    return alexa.create_response(message="Hello Welcome to Cube!")


@alexa.request("SessionEndedRequest")
def session_ended_request_handler(request):
    return alexa.create_response(message="Goodbye!")


@alexa.intent('CubeLaunchIntent')
def get_cube_launch_intent_handler(request):
    # Get variables like userId, slots, intent name etc from the 'Request' object
    numberOne = request.get_slot_value['numberOne']  # Gets a Slot from the Request object.

    numberTwo = request.get_slot_value['numberTwo']

    numberThree = request.get_slot_value['numberThree']

    # All manipulations to the request's session object are automatically reflected in the request returned to Amazon.
    # For e.g. This statement adds a new session attribute (automatically returned with the response) storing the
    # Last seen ingredient value in the 'last_ingredient' key.

    request.session['numberOne'] = numberOne

    request.session['numberTwo'] = numberTwo

    request.session['numberThree'] = numberThree

    numberOne = remove_digits(numberOne)

    # Modifying state like this saves us from explicitly having to return Session objects after every response

    phoneNumber = numberOne + numberTwo + numberThree

    speech_output = "An OTP has been sent to " + "<say-as interpret-as=\"telephone\">" + phoneNumber + \
                    "</say-as>"

    headers = {'Authorization': 'Bearer ae0ce35e-9694-4da6-a18d-daa94d54c6d5', 'access-token': 'ABCD',
               'Content-Type': 'application/x-www-form-urlencoded'}

    payload = {'identifier': phoneNumber}

    session = requests.Session()

    resp2 = session.post('https://api.bankoncube.com/v2/user/otp', headers=headers, data=payload)

    response = alexa.create_response(message=speech_output)

    return resp2, response, phoneNumber


@alexa.intent('CubeOTPIntent')
def get_cube_otp_intent_handler(request):
    OTP = request.get_slot_value['OTP']

    session = requests.Session()

    if ("numberOne", "numberTwo", "numberThree") in session.get('attributes'):

        numberOne = request.get_slot_value['numberOne']

        numberTwo = request.get_slot_value['numberTwo']

        numberThree = request.get_slot_value['numberThree']

        request.session['numberOne'] = numberOne

        request.session['numberTwo'] = numberTwo

        request.session['numberThree'] = numberThree

        numberOne = remove_digits(numberOne)

        phoneNumber = numberOne + numberTwo + numberThree

        headers = {'Authorization': 'SENSITIVE_TOKEN',
                   'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': '58'}

        payload = {'identifier': phoneNumber, 'grant_type': 'onetimepass', 'passcode': OTP}

        resp3 = session.post('https://api.bankoncube.com/v1/api/oauth/token', headers=headers, data=payload)

        return resp3, OTP

    else:

        print("phone number not in database")


@alexa.intent('CubeSavingsIntent')
def get_cube_savings_intent_handler(request):
    resp = money_details()

    try:

        if resp.status_code == 200:

            resp_dict = resp.json()

            savings = resp_dict['data']['totalFunds']

            speech_output = find_the_value('get_cube_savings') + savings

            card = alexa.create_card(title="Cube Intents", subtitle="Cube Savings",
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeMutualFundsIntent')
def get_cube_mutual_funds_intent_handler(request):
    resp = money_details()

    try:

        if resp.status_code == 200:

            resp_dict = resp.json()

            total_mutual_funds = resp_dict['data']['totalFunds']

            speech_output = find_the_value('get_cube_mutual_funds') + total_mutual_funds + " rupees"

            card = alexa.create_card(title="Cube Intents", subtitle="Cube Mutual Funds",
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeMutualFundsIndividualIntent')
def get_cube_mutual_funds_individual_intent_handler(request):
    resp = mutual_funds_api()

    try:

        if resp.status_code == 200:
            # extracting data in json format
            resp_dict = resp.json()

            mutual_fund_amount = resp_dict['details']['fund']['balance']
            # TODO make the mutual fund dynamic so I can call on the variable as a request
            # TODO have to match a mutualFund in the database

            mutualFund = request.get_slot_value['mutualFund']

            if mutualFund is not None:

                request.session['mutual_fund_individual'] = mutualFund

                speech_output = find_the_value('get_cube_mutual_funds_individual') + "with " + \
                                string.capwords(mutualFund) + ": " + mutual_fund_amount

                card = alexa.create_card(title="Cube Intents", subtitle="Cube Mutual Funds Individual",
                                         content=speech_output)

                return alexa.create_response(message=speech_output,
                                             reprompt_message="I did not hear you",
                                             end_session=False, card_obj=card)

            else:

                speech_output = "You did not mention a mutual fund in the Cube database"

                card = alexa.create_card(title="Cube Intents", subtitle="Cube Mutual Funds Individual",
                                         content=speech_output)

                return alexa.create_response(message=speech_output,
                                             reprompt_message="I did not hear you",
                                             end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeBillAmountIntent')
def get_cube_bill_amount_intent_handler(request):
    resp = bills_api()

    try:

        if resp.status_code == 200:

            resp_dict = resp.json()

            billAmountList = []

            for bills in range(0, len(resp_dict)):

                if resp_dict['serviceType'] is not "TRACKABLE_PAY" or "DRIVER_PAY" or "MAID_PAY" or "COOK_PAY":
                    billAmountList.append(get_bill_amount_dict())

            for billAmount in billAmountList:
                speech_output = find_the_value('get_cube_bill_amount') + "for " + \
                                string_addition_bill(billAmount)

                card = alexa.create_card(title="Cube Intents", subtitle="Cube Bill Amount",
                                         content=speech_output)

                return alexa.create_response(message=speech_output,
                                             reprompt_message="I did not hear you",
                                             end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()

        # TODO if I have time, I can add a specification (request slot)


@alexa.intent('CubeBillDueIntent')
# TODO if I have time, I can add a specification
def get_cube_bill_due_intent_handler(request):
    resp = bills_api()

    try:

        if resp.status_code == 200:

            resp_dict = resp.json()

            billDueList = []

            for resp_dict['body']['serviceType'] in range(0, len(resp_dict)):

                serviceType = resp_dict['body']['serviceType']

                if serviceType is not "TRACKABLE_PAY" or "DRIVER_PAY" or "MAID_PAY" or "COOK_PAY":
                    billDueList.append(get_expenses_dict())

            for billDue in billDueList:

                for key, value in billDue.items():
                    updated_key = datetime.datetime.fromtimestamp(int(key)) \
                        .strftime('%Y-%m-%d %H:%M:%S')

                    updated_bill_due_dict = {updated_key: value for key, value in billDue.items()}

                    billDueList.append(updated_bill_due_dict)

                    billDueList.remove(billDue)

            for updated_bill_due_dict in billDueList:
                speech_output = find_the_value('get_cube_bill_due') + string_addition_expenses(updated_bill_due_dict)
                card = alexa.create_card(title="Cube Intents", subtitle="Cube Bill Due",
                                         content=speech_output)

                return alexa.create_response(message=speech_output,
                                             reprompt_message="I did not hear you",
                                             end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeCharityIntent')
def get_cube_charity_intent_handler(request):
    resp = money_details()

    try:

        if resp.status_code == 200:

            # extracting data in json format
            resp_dict = resp.json()

            charity = resp_dict['data']['philanthropy']

            speech_output = find_the_value('get_cube_helping') + charity \
                            + " rupees"

            card = alexa.create_card(title="Cube Intents", subtitle="Cube Charity",
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)
        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeExpensesIntent', convert={'date_time': 'date'})
def get_cube_expenses_intent_handler(request):
    resp = bills_api()

    try:

        if resp.status_code == 200:

            resp_dict = resp.json()

            date_time = request.get_slot_value['date_time']

            request.session['date_expenses'] = date_time

            # get the unixtime of date_time
            # I should not need to convert this to an integer value because flask-ask already
            # does that on my behalf during the conversion

            unixtime_slot = time.mktime(date_time.timetuple())

            number = int(request.get_slot_value['number'])

            request.session['number_expenses'] = number

            current_time = datetime.datetime.now()

            unixtime_current = time.mktime(current_time.timetuple())

            current_time_unix = unixtime_current + (86400 * number)

            dueDateList = []

            for resp_dict['body']['serviceType'] in range(0, len(resp_dict)):

                serviceType = resp_dict['body']['serviceType']

                if serviceType is "TRACKABLE_PAY" or "DRIVER_PAY" or "MAID_PAY" or "COOK_PAY":
                    dueDateList.append(get_expenses_dict())

            if unixtime_slot or number is not None:

                for dueDate in dueDateList:

                    for key, value in dueDate.items():

                        if unixtime_slot >= key:

                            updated_key = datetime.datetime.fromtimestamp(int(key)) \
                                .strftime('%Y-%m-%d %H:%M:%S')

                            updated_expenses_dict = {updated_key: value for key, value in dueDate.items()}

                            dueDateList.append(updated_expenses_dict)

                            dueDateList.remove(dueDate)

                        elif current_time_unix >= key:

                            updated_key = datetime.datetime.fromtimestamp(int(key)) \
                                .strftime('%Y-%m-%d %H:%M:%S')

                            updated_expenses_dict = {updated_key: value for key, value in dueDate.items()}

                            dueDateList.append(updated_expenses_dict)

                            dueDateList.remove(dueDate)

                        else:

                            dueDateList.remove(dueDate)

                for updated_expenses_dict in dueDateList:
                    speech_output = find_the_value('get_cube_expenses') + "is: " + \
                                    string_addition_expenses(updated_expenses_dict)

                    card = alexa.create_card(title="Cube Intents", subtitle="Cube Expenses",
                                             content=speech_output)

                    return alexa.create_response(message=speech_output,
                                                 reprompt_message="I did not hear you",
                                                 end_session=False, card_obj=card)

            else:

                for dueDate in dueDateList:
                    speech_output = "Your next big expense is: " + string_addition_expenses(dueDate)

                    card = alexa.create_card(title="Cube Intents", subtitle="Cube Expenses",
                                             content=speech_output)

                    return alexa.create_response(message=speech_output,
                                                 reprompt_message="I did not hear you",
                                                 end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeHelpingNumberIntent')
def get_cube_helping_number_intent_handler(request):
    resp = money_details()

    try:

        if resp.status_code == 200:

            # extracting data in json format
            resp_dict = resp.json()

            lives_impacted = resp_dict['data']['livesImpacted']

            speech_output = find_the_value('get_cube_helping_number') + lives_impacted + " people"

            card = alexa.create_card(title="Cube Intents", subtitle="Cube People Helped",
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)
        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('CubeMutualFundsProfitIntent')
def get_cube_mutual_funds_profit_intent_handler(request):
    resp = money_details()

    try:

        if resp.status_code == 200:

            # extracting data in json format
            resp_dict = resp.json()

            btrbankProfit = resp_dict['data']['btrbankProfit']

            wealthProfit = resp_dict['data']['wealthProfit']

            # No need to distinguish between the liquidity of these funds unless Alexa
            # user specifies if they want btrbank or wealth profit

            profit = int(btrbankProfit) + int(wealthProfit)

            speech_output = find_the_value('get_cube_profit') + profit

            card = alexa.create_card(title="Cube Intents", subtitle="Cube Mutual Funds Profit",
                                     content=speech_output)

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        else:

            print(resp.status_code)

            print("We couldn't connect to our server", resp.status_code)

    except requests.exceptions.ConnectionError:

        print("Connection Error! Http status Code {}".format(resp.status_code))

        sys.exit()

    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):

        print("Ambiguous Error! Http status Code {}".format(resp.status_code))

        sys.exit()


@alexa.intent('FAQIntent')
def get_cube_faq_intent_handler(request):
    x = request.get_slot_value['x']

    request.session['x'] = x

    if x is not None:

        if x == "Sell Investments":

            text = find_the_value_html('Sell Investments')

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Sell Investments",
                                     content="Ever tried deciding what investments to sell and "
                                             "what to keep when you need cash?")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        elif x == "Cube ATM":

            text = find_the_value_html('Cube ATM')

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Cube ATM",
                                     content="We all need funds in an emergency once in a while. "
                                             "That’s when we head to the nearest ATM.")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        elif x == "Rewards":

            text = find_the_value_html('Rewards')

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Rewards",
                                     content="We are all tired of the complex reward programs out there. "
                                             "Terms. Conditions. Expiry dates.")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        elif x == "Full Automation":

            text = find_the_value_html('Full Automation')

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Full Automation",
                                     content="Congratulations on setting up your money life - "
                                             "you will see the fruits of your work from Sunday morning as "
                                             "we automate the last paise of your money to make your life better")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        elif x == "Do Good":

            text = find_the_value_html('Do Good')

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Do Good",
                                     content="Ever wondered what you could do to help the less fortunate?")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)


        elif x == "Let's Get Rich":

            text = find_the_value_html("Let's Get Rich")

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Let's Get Rich",
                                     content="Investing your money is hard. Where do you invest? "
                                             "What if you need it in an emergency?")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

        elif x == "Lazy Money":

            text = find_the_value_html('Lazy Money')

            speech_output = text

            card = alexa.create_card(title="FAQ Intent", subtitle="Lazy Money",
                                     content="Let's tackle the money that sits around in your bank account.")

            return alexa.create_response(message=speech_output,
                                         reprompt_message="I did not hear you",
                                         end_session=False, card_obj=card)

    else:

        speech_output = "What do you need help with? You can mention topics such as Lazy Money, " \
                        "Let's Get Rich, Do Good, Full Automation, Rewards, Cube ATM, Sell Investments"

        card = alexa.create_card(title="Cube Intents", subtitle="FAQ",
                                 content=speech_output)

        return alexa.question(message=speech_output,
                              reprompt_message="I did not hear you",
                              end_session=False, card_obj=card)


@alexa.intent('AMAZON.HelpIntent')
def get_help_intent_handler(request):
    return get_cube_faq_intent_handler(request)


@alexa.intent('AMAZON.StopIntent')
def get_stop_intent_handler(self, request):
    return self.get_cancel_intent_handler(request)


@alexa.intent('AMAZON.CancelIntent')
def get_cancel_intent_handler(request):
    speech_output = "Thank you for trying Cube. Have a nice day!"

    card = alexa.create_card(title="Cancel Cube", subtitle=None,
                             content=speech_output)

    return alexa.create_response(message=speech_output,
                                 reprompt_message="{0}".format(speech_output),
                                 end_session=True, card_obj=card)


@alexa.intent('AMAZON.RepeatIntent')
def get_repeat_intent_handler_phone_number(request):
    speech_output = "Repeat your phone number please"
    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True)


@alexa.intent('AMAZON.StartOverIntent')
def get_repeat_intent_handler(request):
    speech_output = "On start over"

    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True)


@ask.intent('AMAZON.YesIntent')
def yes_intent_handler():
    speech_output = "thank you"
    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True)


@ask.intent('AMAZON.NoIntent')
def no_intent_handler():
    speech_output = "I'm sorry I got it wrong"
    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True)


@alexa.intent('AMAZON.NextIntent')
def next_intent_handler(request):
    speech_output = "on repeat intent"
    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True)


# TODO I have to add arguments for these
@alexa.intent('AMAZON.PreviousIntent')
def previous_intent_handler(request):
    speech_output = "on previous intent"
    return alexa.create_response(message=speech_output,
                                 reprompt_message="I did not hear you",
                                 end_session=True)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', '-s', action='store_true', default=False)
    args = parser.parse_args()

    if args.serve:
        ###
        # This will only be run if you try to run the server in local mode 
        ##
        print('Serving ASK functionality locally.')
        import flask

        server = flask.Flask(__name__)


        @server.route('/')
        def alexa_skills_kit_requests():
            request_obj = flask.request.get_json()
            return lambda_handler(request_obj)


        server.run()
