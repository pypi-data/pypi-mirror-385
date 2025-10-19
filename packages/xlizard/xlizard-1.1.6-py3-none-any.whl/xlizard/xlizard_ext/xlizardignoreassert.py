'''
This is an extension of xlizard, that ignores the CCN within
the assertion.
'''
from xlizard_languages.code_reader import CodeStateMachine
from .extension_base import ExtensionBase


class xlizardExtension(ExtensionBase):  # pylint: disable=R0903

    def __init__(self):
        super(xlizardExtension, self).__init__(None)

    def _state_global(self, token):
        if token in ("assert", "static_assert"):
            self._state = self.in_assertion

    @CodeStateMachine.read_inside_brackets_then("()", "_state_global")
    def in_assertion(self, token):
        if token in ("&&", "||", "?"):
            self.context.add_condition(-1)
