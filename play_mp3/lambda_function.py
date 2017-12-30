from __future__ import print_function
import logging
import json

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


# use this to play < 90s MP3s
# output should be: "<speak>Playing the sound now, <audio src='path to MP3'/></speak>"
def build_ssml_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }
    

# use this to play MP3s longer than 90s
# used REPLACE_ALL to avoid managing tokens
def build_audio_response(token, file_path):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': 'Playing the requested track'
        },
        'card': {
            'type': 'Simple',
            'title': 'Play Audio',
            'content': 'Playing the requested track'
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': ''
            }
        },
        'directives': [
            {
                'type': 'AudioPlayer.Play',
                'playBehavior': 'REPLACE_ALL',
                'audioItem': {
                    'stream': {
                        'token': token,
                        'url': file_path,
                        'offsetInMilliseconds': 0
                    }
                }
            }
        ],
        'shouldEndSession': True
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def build_dialog_response():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return {
        'version': '1.0',
        'response': message
    }    
    
    
# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to [INSERT:whatever]. " \
                    "Ask me to play or list the tracks."
    reprompt_text = "Ask me to play or list the tracks."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for listening to [INSERT:whatever]." 
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def play_track(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True
    # insert s3 path below, keep it publicly accessible
    # TODO: allow only Alexa skill to access files on s3
    s3_path = "https://s3..."

    if 'TrackName' in intent['slots']:
        track_name = intent['slots']['TrackName']['value']
        file_name = track_name + ".mp3"
        file_path = s3_path + file_name
        return build_response(session_attributes, build_audio_response(file_name, file_path))
    else:
        speech_output = "<speak>I'm not sure what track you want me to play.</speak>"
        reprompt_text = "<speak>I'm not sure what track you want me to play." \
                        "You can tell me a track to play by saying, " \
                        "play the [INSERT:one_of_the_track_names] track</speak>"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))


def list_tracks(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    speech_output = "The available tracks are: [INSERT:track_names]."
    reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    if intent_request.has_key("dialogState"):
        dialog_state = intent_request['dialogState']
        if dialog_state in ("STARTED", "IN_PROGRESS"):
            return build_dialog_response()

    intent = intent_request['intent']
    intent_name = intent['name']

    if intent_name == "PlayTrackIntent":
        return play_track(intent, session)
    elif intent_name == "ListTracksIntent":
        return list_tracks(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    #TODO: add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
   
    # uncomment to see contents of incoming event
    # helpful to see the structure
    # logging.warning(json.dumps(event, indent=2))
    
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.echo-sdk-ams.app.[INSERT:application_id]"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

