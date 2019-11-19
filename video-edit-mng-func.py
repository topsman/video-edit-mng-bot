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
    mng_chat_username = event['message']['chat']['username']

    print("%s:%s:%s:%s\n" % (mng_cmd, mng_params, mng_chat_id, mng_chat_username))

    if mng_cmd not in mng_cmd_type:
        return

    res_msg = exec_mng_cmd(mng_cmd, mng_params, mng_chat_username)
    if res_msg != '':
        snd_telegram_msg(bot=mng_bot, chat_id=mng_chat_id, msg=res_msg)
        print(res_msg)


def exec_mng_cmd(mng_cmd, mng_params, mng_chat_username):
    ec2 = boto3.client('ec2')
    ec2_info = ec2.describe_instances()

    ec2_dict = {}
    res_msg = ''
    tag_name = ''
    tag_service2 = ''

    for item in ec2_info['Reservations']:
        for inst in item['Instances']:
            for tags in inst['Tags']:
                if tags['Key'] == 'Name':
                    tag_name = tags['Value']

                if tags['Key'] == 'Service2':
                    tag_service2 = tags['Value']

                if tags['Key'] == 'team':
                    tag_team = tags['Value']

            if tag_service2 == 'video-edit':
                ec2_dict[tag_name] = [tag_team, inst['State']['Name']]

    for item in sorted(ec2_dict):
        res_msg += "[%s : %s] %s\n" % (item, ec2_dict[item][0], ec2_dict[item][1])

    return res_msg


def snd_telegram_msg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)

