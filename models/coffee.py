from orator import Model


class Coffee(Model):
    __fillable__ = ['client_id','username','caff_type','caff_amt']
    __table__ = 'caffeine'
    #__timestamps__ = False
    pass
