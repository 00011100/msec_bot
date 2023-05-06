from orator import Model


class User(Model):
    __fillable__ = ['client_id','birds','carrots','currency',
    'last_curclaim','last_bird','last_carrot','slapped','username']
    pass
