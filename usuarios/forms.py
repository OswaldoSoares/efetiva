from django.contrib.auth.forms import AuthenticationForm


class MyLoginForm(AuthenticationForm):
    """Altera a class do form padrão do Django de autenticação."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control form-control-center",
                "placeholder": "Usuário",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control form-control-center",
                "placeholder": "Senha",
            }
        )
