
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_BUTTON
from wx import EVT_LISTBOX
from wx import EVT_LISTBOX_DCLICK
from wx import LB_SINGLE

from wx import Button
from wx import CommandEvent
from wx import ListBox

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from umlshapes.enhancedlistbox.AdvancedListCallbacks import AdvancedListCallbacks
from umlshapes.enhancedlistbox.CallbackAnswer import CallbackAnswer
from umlshapes.enhancedlistbox.DownCallbackData import DownCallbackData
from umlshapes.enhancedlistbox.EnhancedListBoxItems import EnhancedListBoxItems
from umlshapes.enhancedlistbox.UpCallbackData import UpCallbackData


class EnhancedListBox(SizedPanel):
    """
    Initially, this was not really a UI component.  Rather, it was a way of creating the
    interrelated UI controls in a parent SizedPanel;  My initial thinking is why create
    yet another component within a component;
    I chose to make it a full-fledged UI component when I realized that it would
    depend on the parent SizedPanel to be of SizerType 'vertical'

    The general strategy is that the users of this class manipulate the data model and
    this component manipulates the UI.

        * The data needs to have a string representation.
        * The data order needs to match the order in the UI.
        * This component "calls back" to the component consumer to manipulate the data
        and provide the changes via specific methods with specific type signatures that return
        eventHandler specific typed data

    """
    def __init__(self, parent: SizedPanel, title: str, callbacks: AdvancedListCallbacks):
        super().__init__(parent)
        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=2)   # SizeProps is a mixin

        self._callbacks: AdvancedListCallbacks = callbacks

        self.logger: Logger = getLogger(__name__)

        self._itemList:  ListBox = cast(ListBox, None)
        self._btnAdd:    Button  = cast(Button, None)
        self._btnEdit:   Button  = cast(Button, None)
        self._btnRemove: Button  = cast(Button, None)
        self._btnUp:     Button  = cast(Button, None)
        self._btnDown:   Button  = cast(Button, None)

        self._layoutListBox(title=title)
        self._layoutButtonPanel()

        self._bindEventHandlers()

    def setItems(self, items: EnhancedListBoxItems):
        for item in items:
            self._itemList.Append(item)

    def _layoutListBox(self, title: str):
        sizedStaticBox: SizedStaticBox = SizedStaticBox(self, label=title)
        sizedStaticBox.SetSizerProps(expand=True, proportion=1)
        sizedStaticBox.SetSizerType('vertical')

        self._itemList = ListBox(sizedStaticBox, choices=[], style=LB_SINGLE)  # size=(-1, 125)
        self._itemList.SetSizerProps(expand=True, proportion=1)

    def _layoutButtonPanel(self):
        btnPanel: SizedPanel = SizedPanel(self)
        btnPanel.SetSizerType('horizontal')

        self._btnAdd    = Button(btnPanel, label='&Add')
        self._btnEdit   = Button(btnPanel, label='&Edit')
        self._btnRemove = Button(btnPanel, label='&Remove')
        self._btnUp     = Button(btnPanel, label='&Up')
        self._btnDown   = Button(btnPanel, label='&Down')

        self._fixButtons()

    def _bindEventHandlers(self):

        self.Bind(EVT_LISTBOX_DCLICK, self._onListDoubleClick, self._itemList)

        self.Bind(EVT_LISTBOX, self._onListSelectionChange, self._itemList)
        self.Bind(EVT_BUTTON,  self._onAdd,                 self._btnAdd)
        self.Bind(EVT_BUTTON,  self._onEdit,                self._btnEdit)
        self.Bind(EVT_BUTTON,  self._onRemove,              self._btnRemove)
        self.Bind(EVT_BUTTON,  self._onUp,                  self._btnUp)
        self.Bind(EVT_BUTTON,  self._onDown,                self._btnDown)

    # noinspection PyUnusedLocal
    def _onListSelectionChange(self, event):
        """
        Called when the end-user clicks on the item list.
        """
        self._fixButtons()
        self.logger.debug('Fix the buttons')

    # noinspection PyUnusedLocal
    def _onListDoubleClick(self, event: CommandEvent):
        """
        Called when the end-user double clicks on the item list.
        """
        self.logger.debug(f'Invoke the edit eventHandler')
        self._onEdit(event)

    # noinspection PyUnusedLocal
    def _onAdd(self, event: CommandEvent):
        self.logger.debug(f'Invoke the add eventHandler')

        answer: CallbackAnswer = self._callbacks.addCallback()
        if answer.valid is True:
            self._itemList.Append(answer.item)

    # noinspection PyUnusedLocal
    def _onEdit(self, event: CommandEvent):
        self.logger.debug(f'Invoke the edit eventHandler')
        selection: int = self._itemList.GetSelection()
        answer: CallbackAnswer = self._callbacks.editCallback(selection)
        if answer.valid:
            self._itemList.SetString(selection, answer.item)

    # noinspection PyUnusedLocal
    def _onRemove(self, event: CommandEvent):
        self.logger.debug(f'Remove from list and invoke the remove eventHandler')
        selection: int = self._itemList.GetSelection()
        self._callbacks.removeCallback(selection)
        self._itemList.Delete(selection)
        self._fixButtons()

    # noinspection PyUnusedLocal
    def _onUp(self, event: CommandEvent):
        self.logger.debug(f'Invoke the up eventHandler, then move item up in list ')
        selection:      int            = self._itemList.GetSelection()
        upCallbackData: UpCallbackData = self._callbacks.upCallback(selection)

        self._itemList.SetString(selection, upCallbackData.currentItem)
        self._itemList.SetString(selection - 1, upCallbackData.previousItem)
        self._itemList.SetSelection(selection - 1)

        self._fixButtons()

    # noinspection PyUnusedLocal
    def _onDown(self, event: CommandEvent):
        self.logger.debug(f'Invoke the down eventHandler, then move item down in list')
        selection:        int              = self._itemList.GetSelection()
        downCallbackData: DownCallbackData = self._callbacks.downCallback(selection)

        self._itemList.SetString(selection, downCallbackData.currentItem)
        self._itemList.SetString(selection + 1, downCallbackData.nextItem)
        self._itemList.SetSelection(selection + 1)

        self._fixButtons()

    def _fixButtons(self):
        """
        Enable/Disable the buttons depending on the selected item
        """
        selection: int = self._itemList.GetSelection()
        self._btnUp.Enable(selection > 0)

        enableEditRemove: bool = selection != -1
        self._btnEdit.Enable(enableEditRemove)
        self._btnRemove.Enable(enableEditRemove)

        self._btnDown.Enable(enableEditRemove and selection < self._itemList.GetCount() - 1)
