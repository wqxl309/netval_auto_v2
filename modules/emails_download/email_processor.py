
import email
import email.parser
import io
import imaplib
import re
import os
import poplib
import time
import base64

class email_processor:
    def __init__(self,protocol,host,username,password,savepath,needSSL=True):
        self._protocol = protocol.lower()
        self._host = host
        self._username = username
        self._password = password
        self._portdict = {'pop':110,'pop3':110,'imap':143,'imap4':143}
        self._port = self._portdict[self._protocol.lower()]
        self._needSSL = needSSL
        self._savepath = savepath
        if not os.path.exists(self._savepath):
            os.system('mkdir {0}'.format(savepath))

    def imap4(self,mailbox='INBOX',searchtype='ALL',attachpatterns=None,savecontent=False,order=('Date','From')):
        """ process emails in mailbox with imap4 protocol
            attachpatterns ex.{keywords:[k1,k2] , 'matchtype':'all' / 'any'}
        """
        if self._protocol not in ('imap','imap4'):
            raise BaseException('Slected protocol {0} while using IMAP !'.format(self._protocol))
        if self._needSSL:
            M = imaplib.IMAP4_SSL(self._host)
        else:
            M = imaplib.IMAP4(self._host)
        result,message = M.login(user=self._username, password=self._password)
        if result=='NO':
            print('[-]{0} login failed : {1}'.format(self._username,message[0].decode()))
            return
        else:
            print('[+]{0} login Successfully !'.format(self._username))
        result,message = M.select(mailbox)
        if result=='NO':
            print('[-]Select mailbox {0} failed for {1}'.format(mailbox,message[0].decode()))
        _,allmails = M.uid('search',None, searchtype)
        emailids = allmails[0].decode().split()
        for emlid in emailids:
            _,emldata = M.uid('fetch',emlid, '(RFC822)') # 提取 byte 格式
            msg = self.email_parse(emldata=emldata[0][1],ftype='bytes')
            emlinfo = self.email_info(msg=msg,elements=('Date','From','Subject'))
            newpath = os.path.join(self._savepath,emlinfo[order[0]],emlinfo[order[1]])  # save email based on order ex.date/from
            if not os.path.exists(newpath):
                os.system('mkdir %s' %newpath)
            self.email_process(msg=msg,pth=newpath,attachpatterns=attachpatterns,savecontent=savecontent)
        result,message = M.close()  # close the currently selected mailbox
        if result=='NO':
            print('[-]Close mailbox {0} failed for {1}'.format(mailbox,message[0].decode()))
        result,message = M.logout()
        if result=='NO':
            print('[-]{0} logout failed : {1}'.format(self._username,message[0].decode()))
        else:
            print('[+]{0} logout Successfully !'.format(self._username))

    def pop3(self,attachpatterns=None,savecontent=False,order=('Date','From')):
        """ attachpatterns ex.{keywords:[k1,k2] , 'matchtype':'all' / 'any'} """
        if self._protocol not in ('pop','pop3'):
            raise BaseException('[-]Slected protocol {0} while using IMAP !'.format(self._protocol))
        if self._needSSL:
            pop_conn = poplib.POP3_SSL(host=self._host)
        else:
            pop_conn = poplib.POP3(host=self._host)
        pop_conn.user(self._username)
        pop_conn.pass_(self._password)
        print('[+]{0} login Successfully !'.format(self._username))
        stat = pop_conn.stat()
        totnum = stat[0]
        for dumi in range(1,totnum+1):
            message = pop_conn.retr(dumi)
            ## with state
            buf = io.BytesIO()
            for line in message[1]:
                buf.write(line)
                buf.write(b'\n')
            buf.write(b'\n')
            buf.seek(0)
            msg = self.email_parse(emldata=buf.getvalue(),ftype='bytes')
            buf.close()
            # get msg info
            emlinfo = self.email_info(msg=msg,elements=('Date','From','Subject'))
            newpath = os.path.join(self._savepath,emlinfo[order[0]],emlinfo[order[1]])  # save email based on order ex.date/from
            if not os.path.exists(newpath):
                os.system('mkdir %s' %newpath)
            self.email_process(msg=msg,pth=newpath,attachpatterns=attachpatterns,savecontent=savecontent)
        pop_conn.quit()
        print('[+]{0} logout Successfully !'.format(self._username))

    def email_parse(self,emldata,ftype='bytes'):
        """ parese the email and generate msg"""
        if ftype=='bytes':
            msg = email.message_from_bytes(emldata)
        elif ftype=='strings':
            msg = email.message_from_string(emldata)
        elif ftype=='bfile':
            msg = email.message_from_binary_file(emldata)
        elif ftype=='file':
            msg = email.message_from_file(emldata)
        else:
            raise BaseException('[-]Unrecognized emldata type!')
        return msg

    def email_info(self,msg,elements=('Date','Time','From','Subject')):
        emailinfo = {}
        if 'Subject' in elements:
            # get subject
            sub = msg.get('Subject')
            subh= email.header.decode_header(sub)
            if subh[0][1] is None:
                substr = subh[0][0].decode() if type(subh[0][0]) is bytes else subh[0][0]
            else:
                try:
                    substr = subh[0][0].decode(subh[0][1])
                except AttributeError:
                    substr = subh[0][0]
            emailinfo['Subject'] = substr
        if 'From' in elements:
            # get sender's email
            fromh = email.header.decode_header(msg.get('From'))
            for fh in fromh:
                if fh[1] is None:
                    try:
                        fromstr = fh[0].decode()
                    except AttributeError:
                        fromstr = fh[0]
                    if '<' in fromstr and '>' in fromstr:
                        matched = re.search('<[\w\W]+@[\w\W]+>',fromstr)
                        if matched is not None:
                            fromstr = matched.group()[1:-1]
                            break
                    else:
                        matched = re.search('[\w\W]+@[\w\W]+',fromstr)
                        if matched is not None:
                            fromstr = matched.group()
                            break
            else:
                fromstr = None
            emailinfo['From'] = fromstr
        if 'Date' in elements:  # can not take Time only without date !
            # get date and time
            dttm = msg.get('Date')
            dttm = dttm.split(',')
            try:
                dttm = dttm.strip().split(' ')  # a string itself
            except AttributeError:
                dttm = dttm[-1].strip().split(' ')   # a list whith second as fulldate
            dates = ' '.join(dttm[0:3])
            datestr = time.strftime('%Y%m%d',time.strptime(dates,'%d %b %Y'))
            emailinfo['Date'] = datestr
            if 'Time' in elements:
                timestr = dttm[3]
                emailinfo['Time'] = timestr
        return emailinfo

    def get_filename(self,msg,default_decode='gbk'):
        # msg must NOT be multipart
        # realize similar functionality of msg.get_filename(),
        # with decoding types set for case when no avaliable decoding found in the header
        # see def of get_filename at https://docs.python.org/3.3/library/email.message.html
        assert not msg.is_multipart(),'[-]msg must NOT be multipart !'
        msgkeys = msg.keys()
        if 'Content-Disposition' in msgkeys:
            headers = email.header.decode_header(msg['Content-Disposition'])
            marker = 'filename='
        elif 'Content-Type' in msgkeys:
            headers = email.header.decode_header(msg['Content-Type'])
            marker = 'name='
        else:
            raise BaseException('[-]neither Content-Disposition nor Content-Type in msg !')
         # generate rawfile strings from headers
        rawfilename = ''
        for hd in headers:
            if hd[1] is None:  # need to deal with hd[0] is str
                hdstr = hd[0] if isinstance(hd[0],str) else hd[0].decode()
            else:   # need to deal with hd[1] is unknown decoding ex. 'unknown-8bit'
                hdstr = hd[0].decode(default_decode) if 'unknown' in hd[1] else hd[0].decode(hd[1])
            rawfilename = ''.join([rawfilename,hdstr.strip()])
        # to match
        if marker in rawfilename:
            rawfls = rawfilename.split('\"')
            return {'is_attachment':'attachment' in rawfilename, 'filename': rawfls[1]}
        else:
            return {'is_attachment':False, 'filename': None}

    def email_process(self,msg,pth,attachpatterns=None,savecontent=False,replace=False):
        """
            process single email, save the contents
            attachpatterns ex.{keywords:[k1,k2] , 'matchtype':'all' / 'any'}
            if attachpatterns==None, then download all attachments
        """
        emailinfo = self.email_info(msg=msg,elements=('Date','From','Subject'))
        subject = emailinfo['Subject']
        ctcount = 0 # for saving text contents of the email
        for part in msg.walk():
            result_file = None
            if not part.is_multipart():
                filename = self.get_filename(part)
                content = part.get_payload(decode=True)
                if filename['is_attachment']:
                    filenm = filename['filename']
                    if attachpatterns:  # 需要匹配附件关键字
                        matchtype = attachpatterns.get('matchtype')
                        matchtype = 'ALL' if matchtype is None else matchtype.upper()
                        for pat in attachpatterns['keywords']:
                            haspat =  pat in filenm
                            if matchtype=='ALL' and (not haspat):  # 需要完全匹配 有未匹配项,匹配失败
                                print("[-]Required pattern: {0} not found in attachment name: {1}".format(pat,filenm))
                                break  # 匹配失败 退出循环，没有可下载附件
                            elif matchtype=='ALL' and haspat: # 需要任一匹配 已有匹配项，匹配成功
                                #print("[+]Pattern: {0} found in attachment name: {1}".format(pat,filenm))
                                result_file = os.path.join(pth, filenm)
                                break  # 匹配成功 退出循环，可下载当前附件
                    else:  # 不需要匹配附件关键字，直接下载找到的附件
                        result_file = os.path.join(pth, filenm)
                else: # not found Attachment but filename found
                    if filename['filename'] is not None and savecontent: # save plain text as html
                        cname = ''.join([subject,'_content_',str(ctcount),'.html'])
                        result_file = os.path.join(pth,cname)
                if result_file:  # file that need to be writen exists
                    try:
                        if not os.path.exists(result_file) or replace:
                            print('[*]Wringting file ...')
                            with open(result_file, "wb") as f:
                                f.write(content)
                    except BaseException as e:
                        if os.path.exists(result_file):
                            os.system('del /Q %s' %result_file)
                        print('[-]Write file of email [Subject] = {0} failed: {1}'.format(subject, e))
                    else:
                        print('[+]Process email [Subject] = {0} finished! \n'.format(subject))


if __name__=='__main__':
    username = 'baiquaninvest@baiquaninvest.com'
    password = 'Baiquan1818'
    protocol = 'imap'
    host = 'imap.qiye.163.com'
    savepath = r'E:\netval_auto_v2.0\modules\emails_download\test_criterion'

    processor = email_processor(protocol=protocol,host=host,username=username,password=password,savepath=savepath)
    processor.imap4(mailbox='INBOX',searchtype='UNFLAGGED',attachpatterns=None,savecontent=True)
    #processor.pop3(attachpatterns=None,savecontent=True) (FROM "chunlin@eastmoney.com")