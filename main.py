import functions_framework
import os
import requests

from .controllers import HaikuController


def get_env_var(name, default=None):
    if (value := os.environ.get(name)) is None:
        print(f'Did not find env var {name=}')
        return default
    return value


def get_boolean_env_var(name, default=None):
    if (value := os.environ.get(name)) is None:
        print(f'Did not find boolean env var {name=}')
        return default
    return value.lower() == 'true'


def get_group_id_key(idx):
    return f'GROUP_ID_{idx}'


def get_bot_id_key(idx):
    return f'BOT_ID_{idx}'


def load_group_id_to_bot_id():
    group_id_to_bot_id = {}
    group_id = get_env_var('TEST_GROUP_ID')
    bot_id = get_env_var('TEST_BOT_ID')
    group_id_to_bot_id[group_id] = bot_id

    for i in range(1, int(get_env_var('BOT_COUNT', 0)) + 1):
        group_id_key = get_group_id_key(i)
        bot_id_key = get_bot_id_key(i)
        group_id = get_env_var(group_id_key)
        bot_id = get_env_var(bot_id_key)

        if not group_id or not bot_id:
            continue
        if group_id in group_id_to_bot_id:
            continue

        group_id_to_bot_id[group_id] = bot_id

    return group_id_to_bot_id


group_id_to_bot_id = load_group_id_to_bot_id()


def postMessage(bot_id, message):
    api_url = 'https://api.groupme.com/v3/bots/post'
    return requests.post(
        api_url,
        json={
            'bot_id': bot_id,
            'text': message
        }
    )


@functions_framework.http
def handle_http(request):
    """
    HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    query_params = request.args
    if word := query_params.get('word'):
        return (
            {
                'word': word,
                'syllable_count': HaikuController().syllables(word)
            },
            200
        )

    params = request.json
    if not (
        params.get('sender_type') == 'user' and
        (group_id := params.get('group_id')) and
        (bot_id := group_id_to_bot_id.get(group_id))
    ):
        return ('', 204)

    message = params.get('text')
    user_name = params.get('name')

    controller = HaikuController(
        user_name=user_name, message=message, verbose=get_boolean_env_var('RUN_VERBOSE', False)
    )
    if not (response_message := controller.get_response_message()):
        return ('', 204)

    postMessage(bot_id, response_message)
    return ('', 204)
