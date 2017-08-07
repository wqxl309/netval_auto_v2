
import email
import email.parser
import io
import imaplib
import re
import os
import poplib
import time


class email_processor:
    def __init__(self,protocol,host,username,password,savepath):
        self._protocol = protocol
        self._host = host
        self._username = username
        self._password = password
        self._portdict = {'pop':110,'pop3':110,'imap':143,'imap4':143}
        self._port = self._portdict[self._protocol.lower()]
        self._savepath = savepath

    def imap4(self,mailbox='INBOX',searchtype='ALL',attachpatterns=None,savecontent=False,order=('Date','From')):
        """ process emails in mailbox with imap4 protocal """
        M = imaplib.IMAP4(self._host)
        M.login(user=self._username, password=self._password)
        result,message = M.select(mailbox)
        print(result,message)
        typ,allmails = M.search(None, searchtype)  # 找到邮件 arg2 'UNSEEN'
        emailids = allmails[0].decode().split()
        for emlid in emailids:
            tp,emldata = M.fetch(emlid, '(RFC822)') # 提取 byte 格式
            msg = self.email_parse(emldata=emldata,ftype='bytes')
            emlinfo = self.email_info(msg=msg,elements=('Date','From','Subject'))
            newpath = os.path.join(self._savepath,emlinfo[order[0]],emlinfo[order[1]])  # save email based on order ex.date/from
            if not os.path.exists(newpath):
                os.system('mkdir %s' %newpath)
            self.email_process(msg=msg,pth=newpath,attachpatterns=attachpatterns,savecontent=savecontent)
        M.close()  # close the currently selected mailbox
        M.logout()

    def pop3(self,attachpatterns=None,savecontent=False,order=('Date','From')):
        pop_conn = poplib.POP3(host=self._host)
        pop_conn.user(self._username)
        pop_conn.pass_(self._password)
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
            raise BaseException('Unrecognized emldata type!')
        return msg

    def email_info(self,msg,elements=('Date','Time','From','Subject')):
        emailinfo = {}
        if 'Subject' in elements:
            # get subject
            sub = msg.get('Subject')
            subh= email.header.decode_header(sub)
            try:
                substr = subh[0][0].decode(subh[0][1])
            except AttributeError:
                substr = subh[0][0]
            emailinfo['Subject'] = substr
        if 'Date' in elements:  # can not take Time only without date !
            # get date and time
            dttm = msg.get('Date')
            dttm = dttm.strip().replace(',','').split(' ')
            dates = ' '.join(dttm[0:3])
            try:
                datestr = time.strftime('%Y%m%d',time.strptime(dates,'%d %b %Y'))
            except:
                t=1
            emailinfo['Date'] = datestr
            if 'Time' in elements:
                timestr = dttm[3]
                emailinfo['Time'] = timestr
        if 'From' in elements:
            # get sender's email
            fromh = email.header.decode_header(msg.get('From'))
            for fh in fromh:
                if fh[1] is None:
                    try:
                        fromstr = fh[0].decode()
                    except AttributeError:
                        fromstr = fh[0]
                    matched = re.search('<[\w\W]+@[\w\W]+>',fromstr)
                    if matched is not None:
                        fromstr = matched.group()[1:-1]
                    break
            else:
                fromstr = None
            emailinfo['From'] = fromstr
        return emailinfo

    def email_process(self,msg,pth,attachpatterns=None,savecontent=False):
        """
            process single email, save the contents
            if attachtype==None, then download all attachments
        """
        emailinfo = self.email_info(msg=msg,elements=('Date','From','Subject'))
        subject = emailinfo['Subject']
        ctcount = 0 # for saving text contents of the email
        for part in msg.walk():
            result_file = None
            if not part.is_multipart():
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                if filename:  # Attachment
                    dh = email.header.decode_header(filename)
                    if dh[0][1] is not None:
                        filenm = dh[0][0].decode(dh[0][1])
                    else:
                        filenm = dh[0][0]
                    if attachpatterns:
                        for pat in attachpatterns: # all patterns must be matched
                            if pat not in filenm:
                                print("[-]Warning : required pattern: {0} not found in attachment name: {1}".format(pat,filenm))
                            break
                    else:  # attchement name passed required check
                        result_file = os.path.join(pth, filenm)
                else:
                    if savecontent:
                        cname = ''.join([subject,'_content_',str(ctcount),'.html'])
                        result_file = os.path.join(pth,cname)
                if result_file:  # file that need to be writen exists
                    try:
                        with open(result_file, "wb") as f:
                            f.write(content)
                    except BaseException as e:
                        print("[-]Warning : Write file of email {0} failed: {1}".format(subject, e))


if __name__=='__main__':
    username='wqxl309@126.com'
    password = 'Wqxl7309'
    protocol = 'pop3'
    host = 'pop.126.com'
    savepath = r'E:\netval_auto_v2.0\modules\emails_download\test126'

    processor = email_processor(protocol=protocol,host=host,username=username,password=password,savepath=savepath)
    #processor.imap4(mailbox='INBOX',searchtype='ALL',attachpatterns=None,savecontent=True)
    processor.pop3(attachpatterns=None,savecontent=True)