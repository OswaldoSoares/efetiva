from rolepermissions.roles import AbstractUserRole


cria_minuta = 'cria_minuta'
edita_minuta = 'edita_minuta'

class Diretor(AbstractUserRole):
    available_permissions = {
        cria_minuta: True,
        edita_minuta: True,
    }

class Secretaria(AbstractUserRole):
    available_permissions = {
        cria_minuta: True,
        edita_minuta: True,
    }

class Motorista(AbstractUserRole):
    available_permissions = {
        edita_minuta: True,
    }
