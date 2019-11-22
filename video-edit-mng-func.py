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
    mng_user_id = str(event['message']['from']['id'])

    if mng_cmd not in mng_cmd_type:
        return

    res_msg = exec_mng_cmd(mng_cmd, mng_params, mng_user_id)
    if res_msg != '':
        snd_telegram_msg(bot=mng_bot, chat_id=mng_chat_id, msg=res_msg)
        print(res_msg)


def exec_mng_cmd(mng_cmd, mng_params, mng_user_id):
    ec2 = boto3.client('ec2')
    ec2_info = ec2.describe_instances()

    ec2_dict = {}
    tag_name, tag_service2, tag_team, tag_user_id = '', '', '', ''
    for item in ec2_info['Reservations']:
        for inst in item['Instances']:
            for tags in inst['Tags']:
                tag_name = tags['Value'] if tags['Key'] == 'Name' else tag_name
                tag_service2 = tags['Value'] if tags['Key'] == 'Service2' else tag_service2
                tag_team = tags['Value'] if tags['Key'] == 'team' else tag_team
                tag_user_id = tags['Value'] if tags['Key'] == 'user_id' else tag_user_id

            if tag_service2 == 'video-edit':
                ec2_dict[tag_name] = {
                    'instance-id': inst['InstanceId'], 'state': inst['State']['Name'],
                    'team': tag_team, 'user_id': tag_user_id,
                    'ip-address': inst['NetworkInterfaces'][0]['Association']['PublicIp']
                }

    res_msg = ''
    if mng_cmd in ['/list']:
        for item in sorted(ec2_dict):
            res_msg += "[%s][%s] %s\n" % (item, ec2_dict[item]['team'], ec2_dict[item]['state'])
    elif mng_cmd in ['/start', '/stop'] and mng_params:
        ec2_name = mng_params[0]
        allowed_user_id_list = ec2_dict[ec2_name]['user_id'].replace(' ', '').split(',') if ec2_name in ec2_dict else []
        allowed_user_id_list += str(os.environ['ADMIN_USER_ID']).replace(' ', '').split(',')
        if (ec2_name in ec2_dict) and (mng_user_id in allowed_user_id_list):
            if mng_cmd in ['/start']:
                ec2.start_instances(InstanceIds=[ec2_dict[ec2_name]['instance-id']])
                res_msg = "[%s][%s] 서버가 곧 시작됩니다. (%s)\n" \
                          % (ec2_name, ec2_dict[ec2_name]['team'], ec2_dict[ec2_name]['ip-address'])
            elif mng_cmd in ['/stop']:
                ec2.stop_instances(InstanceIds=[ec2_dict[ec2_name]['instance-id']])
                res_msg = "[%s][%s] 서버가 곧 중지됩니다.\n" % (ec2_name, ec2_dict[ec2_name]['team'])
        else:
            res_msg = "[%s] 권한이 없거나 등록되지 않은 서버입니다.\n" % ec2_name

    return res_msg


def snd_telegram_msg(bot, chat_id, msg):
    bot.sendMessage(chat_id=chat_id, text=msg)
