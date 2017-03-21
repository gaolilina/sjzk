#! /usr/bin/env python
# coding=utf-8
import json
import logging

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from .models import User, Team
from django.test import TestCase
from rongcloud import RongCloud
from .utils import send_message, identity_verify, picture_verify

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


class ExampleTestCase(TestCase):
    def setUp(self):
        # app_key = os.environ['APP_KEY']
        # app_secret = os.environ['APP_SECRET']
        # self.rcloud = RongCloud(app_key, app_secret)
        self.rcloud = RongCloud()
        
    def log(self, title, message):
        logging.info('{0}: {1}'.format(title, message))
    """
    def test_picture_verify(self):
        picture_url = 'test_data/yellow.png'
        code = picture_verify(picture_url)
        self.assertEqual(code, 0)

    def test_sendMessage_new(self):
        # phone_number = '18811611286'
        phone_number = '13051391335'
        code = '123456'
        tpl_value = "#code#=431515"
        send_message(phone_number, tpl_value)
    """

    def test_identityVerify_wrong(self):
        id_number = '430723199212023303'
        real_name = '赵强'
        res = identity_verify(id_number, real_name)
        print(res)

    def test_identityVerify_right(self):
        id_number = '430723199212023812'
        real_name = '赵强'
        res = identity_verify(id_number, real_name)
        print(res)

    '''
    def test_sendMessage(self):
        # phone_number = '18811611286'
        phone_number = '13051391335'
        code = '123456'
        data = {"mobile": phone_number, "content":
            "您本次的验证码为：" + code + "，如非本人操作，请忽略！【创易】"}
        send_message(data)

    def test_identityVerify(self):
        id_number = '430723199212023303'
        res = identity_verify(id_number)
        print(res)
        error_code = res['error_code']
        print(error_code)
        if error_code == 203801:
            print('请输入正确的15或18位身份证')
        elif error_code == 203802:
            print('错误的身份证或无结果')
        elif error_code == 203803:
            print('身份证校验位不正确')
        elif error_code == 203804:
            print('查询失败')
        else:
            print('验证成功')

    def test_getToken(self):
        r = self.rcloud.User.getToken(
            userId='userId1',
            name='username',
            portraitUri='http://www.rongcloud.cn/images/logo.png')
        self.log('getToken', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_refresh(self):
        r = self.rcloud.User.refresh(
            userId='userId1',
            name='username',
            portraitUri='http://www.rongcloud.cn/images/logo.png')
        self.log('refresh', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_checkOnline(self):
        r = self.rcloud.User.checkOnline(userId='userId1')
        self.log('checkOnline', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_block(self):
        r = self.rcloud.User.block(userId='userId4', minute='10')
        self.log('block', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_unBlock(self):
        r = self.rcloud.User.unBlock(userId='userId2')
        self.log('unBlock', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_queryBlock(self):
        r = self.rcloud.User.queryBlock()
        self.log('queryBlock', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_addBlacklist(self):
        r = self.rcloud.User.addBlacklist(
            userId='userId1', blackUserId='userId2')
        self.log('addBlacklist', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_queryBlacklist(self):
        r = self.rcloud.User.queryBlacklist(userId='userId1')
        self.log('queryBlacklist', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_removeBlacklist(self):
        r = self.rcloud.User.removeBlacklist(
            userId='userId1', blackUserId='userId2')
        self.log('removeBlacklist', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_publishPrivate(self):
        r = self.rcloud.Message.publishPrivate(
            fromUserId='userId1',
            toUserId='{"userId2","userid3","userId4"}',
            objectName='RC:VcMsg',
            content="{\"content\":\"hello\",\"extra\":\"helloExtra\",\"duration\":20}",
            pushContent='thisisapush',
            pushData='{\"pushData\":\"hello\"}',
            count='4',
            verifyBlacklist='0',
            isPersisted='0',
            isCounted='0')
        self.log('publishPrivate', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_publishTemplate(self):
        r = self.rcloud.Message.publishTemplate(
            templateMessage=json.load(open('jsonsource/TemplateMessage.json')))
        self.log('publishTemplate', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_PublishSystem(self):
        r = self.rcloud.Message.PublishSystem(
            fromUserId='userId1',
            toUserId='{"userId2","userid3","userId4"}',
            objectName='RC:TxtMsg',
            content="{\"content\":\"hello\",\"extra\":\"helloExtra\"}",
            pushContent='thisisapush',
            pushData='{\"pushData\":\"hello\"}',
            isPersisted='0',
            isCounted='0')
        self.log('PublishSystem', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_publishSystemTemplate(self):
        r = self.rcloud.Message.publishSystemTemplate(
            templateMessage=json.load(open('jsonsource/TemplateMessage.json')))
        self.log('publishSystemTemplate', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_publishGroup(self):
        r = self.rcloud.Message.publishGroup(
            fromUserId='userId',
            toGroupId='{"groupId1","groupId2","groupId3"}',
            objectName='RC:TxtMsg',
            content="{\"content\":\"hello\",\"extra\":\"helloExtra\"}",
            pushContent='thisisapush',
            pushData='{\"pushData\":\"hello\"}',
            isPersisted='1',
            isCounted='1')
        self.log('publishGroup', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_publishDiscussion(self):
        r = self.rcloud.Message.publishDiscussion(
            fromUserId='userId1',
            toDiscussionId='discussionId1',
            objectName='RC:TxtMsg',
            content="{\"content\":\"hello\",\"extra\":\"helloExtra\"}",
            pushContent='thisisapush',
            pushData='{\"pushData\":\"hello\"}',
            isPersisted='1',
            isCounted='1')
        self.log('publishDiscussion', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_publishChatroom(self):
        r = self.rcloud.Message.publishChatroom(
            fromUserId='userId1',
            toChatroomId='{"ChatroomId1","ChatroomId2","ChatroomId3"}',
            objectName='RC:TxtMsg',
            content="{\"content\":\"hello\",\"extra\":\"helloExtra\"}")
        self.log('publishChatroom', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_broadcast(self):
        r = self.rcloud.Message.broadcast(
            fromUserId='userId1',
            objectName='RC:TxtMsg',
            content="{\"content\":\"哈哈\",\"extra\":\"hello ex\"}",
            pushContent='thisisapush',
            pushData='{\"pushData\":\"hello\"}',
            os='iOS')
        self.log('broadcast', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_getHistory(self):
        r = self.rcloud.Message.getHistory(date='2014010101')
        self.log('getHistory', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_deleteMessage(self):
        r = self.rcloud.Message.deleteMessage(date='2014010101')
        self.log('deleteMessage', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_add(self):
        r = self.rcloud.Wordfilter.add(word='money')
        self.log('add', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_delete(self):
        r = self.rcloud.Wordfilter.delete(word='money')
        self.log('delete', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_getList(self):
        r = self.rcloud.Wordfilter.getList()
        self.log('getList', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_create(self):
        r = self.rcloud.Group.create(
            # userId='{"userId1","userid2","userId3"}',
            userId='userId10',
            groupId='groupId10',
            groupName='groupName10')
        self.log('create', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_refresh1(self):
        r = self.rcloud.Group.refresh(
            groupId='groupId10', groupName='newGroupName10')
        self.log('refresh', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_join(self):
        r = self.rcloud.Group.join(
            userId='9',
            groupId='groupId10',
            groupName='newGroupName10')
        self.log('join', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_quit(self):
        r = self.rcloud.Group.quit(
            userId='{"userId2","userid3","userId4"}', groupId='groupId10')
        self.log('quit', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)


    def test_sync(self):
        groupInfo = [("groupId1", "groupName1"), ("groupId2", "groupName2"),
                     ("groupId3", "groupName3")]
        r = self.rcloud.Group.sync(userId='userId1', groupInfo=groupInfo)
        self.log('sync', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_refresh1(self):
        r = self.rcloud.Group.refresh(
            groupId='groupId1', groupName='newGroupName')
        self.log('refresh', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_join(self):
        r = self.rcloud.Group.join(
            userId='{"userId2","userid3","userId4"}',
            groupId='groupId1',
            groupName='TestGroup')
        self.log('join', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_queryUser(self):
        r = self.rcloud.Group.queryUser(groupId='groupId1')
        self.log('queryUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_quit(self):
        r = self.rcloud.Group.quit(
            userId='{"userId2","userid3","userId4"}', groupId='TestGroup')
        self.log('quit', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_addGagUser(self):
        r = self.rcloud.Group.addGagUser(
            userId='userId1', groupId='groupId1', minute='1')
        self.log('addGagUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_lisGagUser(self):
        r = self.rcloud.Group.lisGagUser(groupId='groupId1')
        self.log('lisGagUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_rollBackGagUser(self):
        r = self.rcloud.Group.rollBackGagUser(
            userId='{"userId2","userid3","userId4"}', groupId='groupId1')
        self.log('rollBackGagUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_dismiss(self):
        r = self.rcloud.Group.dismiss(userId='userId1', groupId='groupId1')
        self.log('dismiss', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_create1(self):
        chatRoomInfo = [("chatroomId1", "chatroomName1"),
                        ("chatroomId2", "chatroomName2"),
                        ("chatroomId3", "chatroomName3")]
        r = self.rcloud.Chatroom.create(chatRoomInfo=chatRoomInfo)
        self.log('create', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_join1(self):
        r = self.rcloud.Chatroom.join(
            userId='{"userId2","userid3","userId4"}', chatroomId='chatroomId1')
        self.log('join', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_query(self):
        r = self.rcloud.Chatroom.query(
            chatroomId='{"chatroomId1","chatroomId2","chatroomId3"}')
        self.log('query', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_queryUser1(self):
        r = self.rcloud.Chatroom.queryUser(
            chatroomId='chatroomId1', count='500', order='2')
        self.log('queryUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_stopDistributionMessage(self):
        r = self.rcloud.Chatroom.stopDistributionMessage(
            chatroomId='chatroomId1')
        self.log('stopDistributionMessage', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_resumeDistributionMessage(self):
        r = self.rcloud.Chatroom.resumeDistributionMessage(
            chatroomId='chatroomId1')
        self.log('resumeDistributionMessage', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_addGagUser1(self):
        r = self.rcloud.Chatroom.addGagUser(
            userId='userId1', chatroomId='chatroomId1', minute='1')
        self.log('addGagUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_ListGagUser(self):
        r = self.rcloud.Chatroom.ListGagUser(chatroomId='chatroomId1')
        self.log('ListGagUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_rollbackGagUser(self):
        r = self.rcloud.Chatroom.rollbackGagUser(
            userId='userId1', chatroomId='chatroomId1')
        self.log('rollbackGagUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_addBlockUser(self):
        r = self.rcloud.Chatroom.addBlockUser(
            userId='userId1', chatroomId='chatroomId1', minute='1')
        self.log('addBlockUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_getListBlockUser(self):
        r = self.rcloud.Chatroom.getListBlockUser(chatroomId='chatroomId1')
        self.log('getListBlockUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_rollbackBlockUser(self):
        r = self.rcloud.Chatroom.rollbackBlockUser(
            userId='userId1', chatroomId='chatroomId1')
        self.log('rollbackBlockUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_destroy(self):
        r = self.rcloud.Chatroom.destroy(
            chatroomId='{"chatroomId","chatroomId1","chatroomId2"}')
        self.log('destroy', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_addWhiteListUser(self):
        r = self.rcloud.Chatroom.addWhiteListUser(
            chatroomId='chatroomId',
            userId='{"userId1","userId2","userId3","userId4","userId5"}')
        self.log('addWhiteListUser', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_setUserPushTag(self):
        r = self.rcloud.Push.setUserPushTag(
            userTag=json.load(open('jsonsource/UserTag.json',
                                   'r', encoding='utf-8')))
        self.log('setUserPushTag', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_broadcastPush(self):
        r = self.rcloud.Push.broadcastPush(
            pushMessage=json.load(open('jsonsource/PushMessage.json',
                                       'r', encoding='utf-8')))
        self.log('broadcastPush', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_getImageCode(self):
        r = self.rcloud.SMS.getImageCode(appKey='app-key')
        self.log('getImageCode', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_sendCode(self):
        r = self.rcloud.SMS.sendCode(
            mobile='13500000000',
            templateId='dsfdsfd',
            region='86',
            verifyId='1408706337',
            verifyCode='1408706337')
        self.log('sendCode', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)

    def test_verifyCode(self):
        r = self.rcloud.SMS.verifyCode(sessionId='2312312', code='2312312')
        self.log('verifyCode', r)
        self.assertTrue('code' in r.result)
        self.assertEqual(r.result['code'], 200)
    '''
