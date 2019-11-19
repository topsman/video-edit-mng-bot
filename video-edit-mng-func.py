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
    print("(event) %s:%s:%s:%s\n" % (mng_cmd, mng_params, mng_chat_id, mng_chat_username))

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
    tag_team = ''
    tag_username = ''

    for item in ec2_info['Reservations']:
        for inst in item['Instances']:
            for tags in inst['Tags']:
                if tags['Key'] == 'Name':
                    tag_name = tags['Value']

                if tags['Key'] == 'Service2':
                    tag_service2 = tags['Value']

                if tags['Key'] == 'team':
                    tag_team = tags['Value']

                if tags['Key'] == 'username':
                    tag_username = tags['Value']

            if tag_service2 == 'video-edit':
                ec2_dict[tag_name] = {'instance-id': inst['InstanceId'], 'state': inst['State']['Name'],
                                      'team': tag_team, 'username': tag_username}

    if mng_cmd in ['/list']:
        for item in sorted(ec2_dict):
            res_msg += "[%s : %s : %s] %s\n" % \
                       (item, ec2_dict[item]['team'], ec2_dict[item]['username'], ec2_dict[item]['state'])
    elif mng_cmd in ['/start']:
        if mng_params[0] in ec2_dict and mng_chat_username == ec2_dict[mng_params[0]]['username']:
            ec2.start_instances(InstanceIds=[ec2_dict[mng_params[0]]['instance-id']])
            res_msg = "[%s : %s] 서버가 곧 시작됩니다.\n" % (mng_params[0], ec2_dict[mng_params[0]]['team'])
        else:
            res_msg = "[%s : %s] 권한이 없습니다.\n" % (mng_params[0], ec2_dict[mng_params[0]]['team'])
    elif mng_cmd in ['/stop']:
        if mng_params[0] in ec2_dict and mng_chat_username == ec2_dict[mng_params[0]]['username']:
            ec2.stop_instances(InstanceIds=[ec2_dict[mng_params[0]]['instance-id']])
            res_msg = "[%s : %s] 서버가 곧 중지됩니다.\n" % (mng_params[0], ec2_dict[mng_params[0]]['team'])
        else:
            res_msg = "[%s : %s] 권한이 없습니다.\n" % (mng_params[0], ec2_dict[mng_params[0]]['team'])

    return res_msg


def snd_telegram_msg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)

