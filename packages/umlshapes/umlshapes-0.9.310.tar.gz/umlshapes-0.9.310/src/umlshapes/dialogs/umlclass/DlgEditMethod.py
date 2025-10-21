
from typing import cast

from logging import Logger
from logging import getLogger

from copy import deepcopy

from wx import EVT_BUTTON
from wx import EVT_TEXT
from wx import ID_ANY

from wx import OK
from wx import RA_SPECIFY_ROWS

from wx import Colour
from wx import RadioBox
from wx import CommandEvent
from wx import DefaultSize
from wx import Size
from wx import StaticText
from wx import TextCtrl
from wx import Point
from wx import Button

from wx.lib.sized_controls import SizedPanel

from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutMethod import SourceCode
from pyutmodelv2.PyutMethod import PyutParameters

from pyutmodelv2.PyutParameter import PyutParameter
from pyutmodelv2.PyutType import PyutType

from pyutmodelv2.enumerations.PyutVisibility import PyutVisibility

from umlshapes.dialogs.BaseEditDialog import BaseEditDialog
from umlshapes.dialogs.BaseEditDialog import CustomDialogButton
from umlshapes.dialogs.BaseEditDialog import CustomDialogButtons
from umlshapes.dialogs.umlclass.DlgEditCode import DlgEditCode
from umlshapes.dialogs.umlclass.DlgEditMethodModifiers import DlgEditMethodModifiers
from umlshapes.dialogs.umlclass.DlgEditParameter import DlgEditParameter
from umlshapes.enhancedlistbox.AdvancedListCallbacks import AdvancedListCallbacks

from umlshapes.enhancedlistbox.CallbackAnswer import CallbackAnswer
from umlshapes.enhancedlistbox.DownCallbackData import DownCallbackData
from umlshapes.enhancedlistbox.EnhancedListBox import EnhancedListBox
from umlshapes.enhancedlistbox.EnhancedListBoxItems import EnhancedListBoxItems
from umlshapes.enhancedlistbox.UpCallbackData import UpCallbackData


class DlgEditMethod(BaseEditDialog):

    def __init__(self, parent,  pyutMethod: PyutMethod, editInterface: bool = False):

        super().__init__(parent, title="Edit Method")

        self.logger:         Logger = getLogger(__name__)
        self._editInterface: bool   = editInterface

        self._pyutMethod:     PyutMethod = pyutMethod
        self._pyutMethodCopy: PyutMethod = deepcopy(pyutMethod)

        self._rdbVisibility:    RadioBox = cast(RadioBox, None)
        self._methodName:       TextCtrl = cast(TextCtrl, None)
        self._MethodReturnType: TextCtrl = cast(TextCtrl, None)
        self._btnModifiers:     Button   = cast(Button, None)

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')

        self._pyutParameters: EnhancedListBox = cast(EnhancedListBox, None)

        self._layoutMethodInformation(parent=sizedPanel)
        self._layoutParameterControls(parent=sizedPanel)

        self._btnOk:            Button = cast(Button, None)
        self._btnCancel:        Button = cast(Button, None)

        customDialogButton: CustomDialogButton = CustomDialogButton()
        customDialogButton.label    = 'C&ode...'
        customDialogButton.callback = self._onMethodCode
        self._layoutCustomDialogButtonContainer(parent=sizedPanel, customButtons=CustomDialogButtons([customDialogButton]))

        self._initializeDataInControls()

        self._normalNameBackgroundColour: Colour = self._methodName.GetBackgroundColour()

        self.Bind(EVT_TEXT, self._onMethodNameChange, self._methodName)

        self.Fit()
        self.SetMinSize(self.GetSize())

    def _initializeDataInControls(self):
        """
            Fill the text controls with PyutMethod data
        """
        self._methodName.SetValue(self._pyutMethodCopy.name)

        self._MethodReturnType.SetValue(str(self._pyutMethodCopy.returnType))

        if self._editInterface is False:
            self._rdbVisibility.SetStringSelection(str(self._pyutMethodCopy.visibility))

        parameterItems: EnhancedListBoxItems = EnhancedListBoxItems([])
        for pyutParameter in self._pyutMethodCopy.parameters:
            parameterItems.append(str(pyutParameter))     # Depends on a reasonable __str__ implementation

        self._pyutParameters.setItems(parameterItems)

    def _layoutMethodInformation(self, parent: SizedPanel):

        infoPanel: SizedPanel = SizedPanel(parent)
        infoPanel.SetSizerType('horizontal')
        self._layoutMethodVisibility(infoPanel)

        methodPanel: SizedPanel = SizedPanel(infoPanel)
        methodPanel.SetSizerType("grid", {"cols": 2})  # 2-column grid layout

        StaticText(methodPanel, label="Name")
        StaticText(methodPanel, label="Return type")

        self._methodName   = TextCtrl(methodPanel, value="", size=Size(125, -1))
        self._MethodReturnType = TextCtrl(methodPanel, value="", size=Size(125, -1))

        if self._editInterface is False:
            self._btnModifiers = Button(parent, label='&Modifiers...')
            self.Bind(EVT_BUTTON, self._onModifiers, self._btnModifiers)

    def _layoutMethodVisibility(self, parent: SizedPanel):

        if self._editInterface is False:
            self._rdbVisibility = RadioBox(parent, ID_ANY, "", Point(35, 30), DefaultSize, ["+", "-", "#"], style=RA_SPECIFY_ROWS)

    def _layoutParameterControls(self, parent: SizedPanel):
        """
        Args:
            parent:
        """
        callbacks: AdvancedListCallbacks = AdvancedListCallbacks()
        callbacks.addCallback    = self._parameterAddCallback
        callbacks.editCallback   = self._parameterEditCallback
        callbacks.removeCallback = self._parameterRemoveCallback
        callbacks.upCallback     = self._parameterUpCallback
        callbacks.downCallback   = self._parameterDownCallback

        self._pyutParameters = EnhancedListBox(parent=parent, title='Parameters:', callbacks=callbacks)

    def _parameterAddCallback (self) -> CallbackAnswer:
        # TODO Use default parameter name when available
        pyutParameter: PyutParameter  = PyutParameter(name='parameter1')
        answer:        CallbackAnswer = self._editParameter(pyutParameter=pyutParameter)
        if answer.valid is True:
            self._pyutMethodCopy.parameters.append(pyutParameter)

        return answer

    def _parameterEditCallback (self, selection: int) -> CallbackAnswer:

        pyutParameter: PyutParameter = self._pyutMethodCopy.parameters[selection]
        return self._editParameter(pyutParameter=pyutParameter)

    def _editParameter(self, pyutParameter: PyutParameter) -> CallbackAnswer:

        answer:        CallbackAnswer = CallbackAnswer()
        with DlgEditParameter(parent=self, parameterToEdit=pyutParameter) as dlg:
            if dlg.ShowModal() == OK:
                answer.valid = True
                answer.item  = str(pyutParameter)
            else:
                answer.valid = False

        return answer

    def _parameterRemoveCallback (self, selection: int):
        pyutParameters: PyutParameters = self._pyutMethodCopy.parameters
        pyutParameters.pop(selection)

    def _parameterUpCallback (self, selection: int) -> UpCallbackData:

        pyutParameters: PyutParameters = self._pyutMethodCopy.parameters
        pyutParameter:  PyutParameter  = pyutParameters[selection]
        pyutParameters.pop(selection)
        pyutParameters.insert(selection-1, pyutParameter)

        upCallbackData: UpCallbackData = UpCallbackData()
        upCallbackData.currentItem  = str(pyutParameters[selection])
        upCallbackData.previousItem = str(pyutParameters[selection-1])

        return upCallbackData

    # noinspection PyUnusedLocal
    def _parameterDownCallback (self, selection: int) -> DownCallbackData:

        parameters:    PyutParameters = self._pyutMethodCopy.parameters
        pyutParameter: PyutParameter  = parameters[selection]
        parameters.pop(selection)
        parameters.insert(selection + 1, pyutParameter)

        downCallbackData: DownCallbackData = DownCallbackData()
        downCallbackData.currentItem = str(parameters[selection])
        downCallbackData.nextItem    = str(parameters[selection+1])

        return downCallbackData

    # noinspection PyUnusedLocal
    def _onModifiers(self, event: CommandEvent):

        with DlgEditMethodModifiers(parent=self, pyutModifiers=self._pyutMethodCopy.modifiers) as dlg:
            if dlg.ShowModal() == OK:
                self._pyutMethodCopy.modifiers = dlg.pyutModifiers

    # noinspection PyUnusedLocal
    def _onMethodCode(self, event: CommandEvent):
        sourceCode: SourceCode = self._pyutMethodCopy.sourceCode
        with DlgEditCode(parent=self, wxID=ID_ANY, sourceCode=sourceCode) as dlg:
            if dlg.ShowModal() == OK:
                self.logger.debug(f'Answered Ok')
                self._pyutMethodCopy.sourceCode = dlg.sourceCode
            else:
                self.logger.debug(f'Do nothing code dialog cancelled')

    # noinspection PyUnusedLocal
    def _onMethodNameChange(self, event: CommandEvent):

        updatedName: str = self._methodName.GetValue().strip()
        self.logger.debug(f'{updatedName=}')
        if self._methodName.GetValue().strip() == '':
            self._indicateEmptyTextCtrl(name=self._methodName)
        else:
            self._indicateNonEmptyTextCtrl(name=self._methodName, normalBackgroundColor=self._normalNameBackgroundColour)

    # noinspection PyUnusedLocal
    def _onOk (self, event: CommandEvent):
        """
        Override base with additional behavior
        When the OK button from dlgEditMethod is clicked.

        Args:
            event:
        """
        self._pyutMethod.name = self._methodName.GetValue()

        self._pyutMethod.modifiers = self._pyutMethodCopy.modifiers

        returnType: PyutType = PyutType(self._MethodReturnType.GetValue())
        self._pyutMethod.returnType = returnType
        self._pyutMethod.parameters = self._pyutMethodCopy.parameters

        if self._editInterface is False:
            visStr:      str               = self._rdbVisibility.GetStringSelection()
            visibility: PyutVisibility = PyutVisibility.toEnum(visStr)
            self._pyutMethod.visibility = visibility

        self._pyutMethod.sourceCode = self._pyutMethodCopy.sourceCode

        super()._onOk(event)

    def _onCancel (self, event):
        self._onClose(event)
