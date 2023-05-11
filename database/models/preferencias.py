from ..db import db


class Preferencias(db.Model):
    __tablename__ = "Preferencias"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('User.id'),
                     nullable=False, unique=True)
    sp = db.Column(db.Integer, nullable=False)
    spv = db.Column(db.Integer, nullable=False)
    np = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Integer, nullable=False)
    ep = db.Column(db.Integer, nullable=False)
    rp = db.Column(db.Integer, nullable=False)
    ic = db.Column(db.Integer, nullable=False)
    iap = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.Integer, nullable=False)
    ipv = db.Column(db.Integer, nullable=False)
    imp = db.Column(db.Integer, nullable=False)
    ipp = db.Column(db.Integer, nullable=False)
    pp = db.Column(db.Integer, nullable=False)
    pap = db.Column(db.Integer, nullable=False)
    os = db.Column(db.Integer, nullable=False)
    oip = db.Column(db.Integer, nullable=False)

    def __init__(self, user, sp=1, spv=1, np=1, data=1, ep=1, rp=1, ic=1, iap=1, ip=1, ipv=1, imp=1, ipp=1, pp=1, pap=1, os=1, oip=1):
        self.user = user
        self.sp = sp
        self.spv = spv
        self.np = np
        self.data = data
        self.ep = ep
        self.rp = rp
        self.ic = ic
        self.iap = iap
        self.ip = ip
        self.ipv = ipv
        self.imp = imp
        self.ipp = ipp
        self.pp = pp
        self.pap = pap
        self.os = os
        self.oip = oip

    def __repr__(self):
        return '<Tipo Estructura %r>' % self.tipo

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'user': self.user,
            'sp': self.sp,
            'spv': self.spv,
            'np': self.np,
            'data': self.data,
            'ep': self.ep,
            'rp': self.rp,
            'ic': self.ic,
            'iap': self.iap,
            'ip': self.ip,
            'ipv': self.ipv,
            'imp': self.imp,
            'ipp': self.ipp,
            'pp': self.pp,
            'pap': self.pap,
            'os': self.os,
            'oip': self.oip

        }