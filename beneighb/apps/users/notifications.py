import logging
import requests

import firebase_admin

from firebase_admin import messaging
from firebase_admin.exceptions import InvalidArgumentError


logger = logging.getLogger(__name__)


def send_push_notification(recipient, body, title='', data=None):
    if not recipient.fcm_token:
        return

    msg_data = {
        'notification': messaging.Notification(
            title=title,
            body=body,
        ),
        'token': recipient.fcm_token,
    }

    if data:
        msg_data['data'] = data

    try:
        message = messaging.Message(**msg_data)
        response = messaging.send(message)
        logger.info('Successfully sent message:', response)
    except InvalidArgumentError:
        logger.exception(f'Invalid FCM token: {recipient.fcm_token}')
    except requests.exceptions.HTTPError:
        recipient.fcm_token = ''
        recipient.save()

        logger.info('Invalid FCM token has been erased')
    except (
        firebase_admin._messaging_utils.UnregisteredError
    ) as unregistered_error:
        recipient.fcm_token = ''
        recipient.save()

        logger.info(f'Unregistered errro: {unregistered_error}')
        logger.info('Invalid FCM token has been erased')
    except (
        firebase_admin._messaging_utils.SenderIdMismatchError
    ) as sender_id_mismatch_error:
        recipient.fcm_token = ''
        recipient.save()

        logger.info(f'Sender ID mismatch error: {sender_id_mismatch_error}')
        logger.info('Invalid FCM token has been erased')
    except Exception as e:
        recipient.fcm_token = ''
        recipient.save()

        logger.exception('Error:', e)
        logger.info('FCM token has been erased')
        logger.info('New fcm token:', recipient.fcm_token)
