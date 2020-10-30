# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import datetime
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)



# Customisable bits

PET_NAME = ""
PET_ID = ""
AUTH_TOKEN = ""
HOUSEHOLD = ""




API_URL = f"https://app.api.surehub.io/api/pet/{PET_ID}/position"

def getCatLocation() -> str:
    """Get cat location is invoked to get the location of the pet. it uses the url above
        with the included pet id to the position endpoint. this returns some json with the location value.
        1 is inside, 0 is outside."""

    location = ""

    LOGGER.debug("Making request to API URL %s", API_URL)

    response = requests.get(
        API_URL,
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"})

    if not response.ok:
        message = response.content.decode('utf-8')

        raise RuntimeError(
            f"Failed to GET pet location: {response.status_code}: {message}"
        )


    json_data = response.json()

    LOGGER.debug("JSON Response: %s", json_data)

    if json_data['data']:
        if json_data['data']['where'] == 1:
            return "inside"
        
        return "outside"

    return "in a different dimension"


def setCatLocation(cats_location):
    """Function to set the cats location,
        takes his location from the voice input of alexa from the slot value,
            and sends it to teh api for updating the state. 1 = inside, 0 = outside.
            """

    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second

    since_datetime = "{}-{}-{}T{}:{}:{}+00:00".format(year, month, day, hour, minute, second)

    url = "https://app.api.surehub.io/api/pet/{}/position".format(PET_ID)
    if cats_location == "inside" or cats_location == "home" or cats_location == "in":
        location_code = 1
    if cats_location == "outside" or cats_location == "out":
        location_code = 2

    body = {'where': location_code, 'since': since_datetime}

    resp = requests.post(url, headers={"Authorization": "Bearer {}".format(AUTH_TOKEN), "Content-Type": "application/json"}, data=json.dumps(body))

    json_data = resp.json()
    if json_data['data']['where'] == location_code:
        worked = True
    else:
        worked = False
    return worked



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can say Hello or Help. Which would you like to try?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

#write handlers code below?

class GetLocationOfCatIntentHandler(AbstractRequestHandler):
    """Handler for Cat Location."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GetLocationOfCatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        location = getCatLocation()
        speak_output = f"{PET_NAME} is currently {location}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class SetLocationOfCatIntentHandler(AbstractRequestHandler):
    """Handler for Cat Location."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SetLocationOfCatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        slot = ask_utils.request_util.get_slot(handler_input, "inout")
        location = slot.value
        
        if setCatLocation(location):
            speak_output = f"Ok, setting {PET_NAME}'s location to {location}"
        else:
            speak_output = f"Something has gone wrong, unable to update {PET_NAME}'s location to {location}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

    

###

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Ask me where your cat is, or if they are in or out"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        LOGGER.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
#custom below
sb.add_request_handler(GetLocationOfCatIntentHandler())
sb.add_request_handler(SetLocationOfCatIntentHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
