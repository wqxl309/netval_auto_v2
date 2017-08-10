#coding=utf-8
import email
import email.parser
import io
import imaplib
import re
import os
import poplib
import time
from modules.emails_download.email_processor import email_processor


class email_processor_product(email_processor):
    """ download valuesheet for each product """
    @staticmethod
    def match_keywords(kwlist,targetlist,matchtype='ALL'):
        """ match keywords in kwlist to strs in targetlist"""
        if type(kwlist) is str:
            kwlist = [kwlist]
        if type(targetlist) is str:
            targetlist = [targetlist]
        matchall = True if matchtype.upper()=='ALL' else False
        matchresult = {}
        for target in targetlist:
            for keyword in kwlist:
                if (keyword in target) and (not matchall):
                    matchresult[target] = True
                    break
                elif (keyword not in target) and matchall:
                    matchresult[target] = False
                    break
            else: # no break for the loop
                matchresult[target] = True if matchall else False
        return matchresult

    def __init__(self,host,username,password,savepath,lastuidpath,protocol='imap4',needSSL=True,product_filters=None):
        """ product_filters : keywords dict containing kws to discern specified emails,
            ex:{'pname1':{'Subject':[kw1,kw2,...],'From':[add1,add2],'Attachment':[kw1,kw2,...]},...}
            """
        self._lastuidpath = lastuidpath
        self._product_filters = product_filters
        super(email_processor_product,self).__init__(protocol,host,username,password,savepath,needSSL)

    def download_imap4(self,downloadtype='UNFLAGGED'):
        """ downloadtype ALL/UNFLAGGED"""
        if self._protocol not in ('imap','imap4'):
            raise BaseException('Slected protocol {0} while using IMAP !'.format(self._protocol))
        if self._needSSL:
            M = imaplib.IMAP4_SSL(self._host)
        else:
            M = imaplib.IMAP4(self._host)
        result,message = M.login(user=self._username, password=self._password)
        if result=='NO':
            print('[+]{0} login failed : {1}'.format(self._username,message[0].decode()))
            return
        else:
            print('[+]{0} login Successfully !'.format(self._username))
        with open(self._lastuidpath,'r') as uid:
            lastuid = str(int(uid.readlines()[0].strip()))
        mailbox = 'INBOX'
        result,message = M.select(mailbox)
        if result=='NO':
            print('[+]Select mailbox {0} failed for {1}'.format(mailbox,message[0].decode()))
        # extract all mail ids from appointed mail types
        _,allmails = M.uid('search',None, downloadtype)
        emailids = allmails[0].decode().split()
        try:
            startpos = emailids.index(lastuid)
            idlist = emailids[(startpos+1):]
        except ValueError:
            idlist = emailids
        try:
            for emlid in idlist:
                tp,emldata = M.uid('fetch',emlid, '(RFC822)')
                msg = self.email_parse(emldata=emldata[0][1],ftype='bytes')
                emlinfo = self.email_info(msg=msg,elements=('From','Subject'))
                for pname in self._product_filters:
                    kwsub = self._product_filters[pname]['Subject']
                    foundsub = email_processor_product.match_keywords(kwlist=kwsub,targetlist=emlinfo['Subject'],matchtype='ALL')[emlinfo['Subject']]
                    if foundsub:  # subject filter passed,
                        # download
                        newpath = os.path.join(self._savepath,' '.join(['估值信息',pname]))
                        attachpatterns = {'keywords':self._product_filters[pname]['Attachment'],'matchtype':'ALL'}
                        if not os.path.exists(newpath):
                            os.system('mkdir %s' %newpath)
                        self.email_process(msg=msg,pth=newpath,attachpatterns=attachpatterns,savecontent=False)
        except:
            raise
        # save lastuid only when emails are processed
        else:
            if idlist: # make sure idlist is not empty
                with open(self._lastuidpath,'w') as uid:
                    uid.write(idlist[-1])
            else:
                print('[+]No email to download !')
        result,message = M.close()  # close the currently selected mailbox
        if result=='NO':
            print('[+]Close mailbox {0} failed for {1}'.format(mailbox,message[0].decode()))
        result,message = M.logout()
        if result=='NO':
            print('[+]{0} logout failed : {1}'.format(self._username,message[0].decode()))
        else:
            print('[+]{0} logout Successfully !'.format(self._username))

    def download_pop3(self):
        pass