import telegram
import boto3
import os

mng_cmd_type = ['/list', '/start', '/stop']


def video_edit_mng_handler(event, context):
    telegram_token = os.environ['TELEGRAM_TOKEN']
    mng_bot = telegram.Bot(token=telegram_token)

    mng_cmd = event['message']['text'].split()[0]
    mng_params = event['message']['text'].split()[1:]
    mng_chat_id = event['message']['chat']['id']

    if mng_cmd not in mng_cmd_type:
        return

    res_msg = exec_mng_cmd(mng_cmd, mng_params)
    if res_msg != '':
        snd_telegram_msg(bot=mng_bot, chat_id=mng_chat_id, msg=res_msg)


def exec_mng_cmd(mng_cmd, mng_params):
    ec2 = boto3.client('ec2')
    ec2_info = ec2.describe_instances()

    res_msg = ''
    for item in ec2_info['Reservations']:
        for inst in item['Instances']:
            list_item = inst['State']['Name']
            res_msg += list_item

    return res_msg


def snd_telegram_msg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)

