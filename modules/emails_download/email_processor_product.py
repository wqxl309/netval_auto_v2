
from .email_processor import email_processor

class email_processor_product(email_processor):
    """ download π¿÷µ±Ì for each product """
    def __init__(self,protocol,host,username,password,savepath,needSSL=True,product_kws={}):
        self._product_kws = product_kws
        super(email_processor_product,self).__init__(protocol,host,username,password,savepath,needSSL)

    def file_downloads(self):
        pass

    def download_imap4(self):
        pass

    def download_pop3(self):
        pass