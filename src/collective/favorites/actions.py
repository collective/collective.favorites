from datetime import datetime
from json.encoder import JSONEncoder

from Products.Five.browser import BrowserView

from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from collective.favorites import FavoritesMessageFactory as _
from .interfaces import IFavoriteStorage
from plone.app.layout.navigation.root import getNavigationRootObject
from Products.CMFCore.interfaces._content import IFolderish
from zope.i18n import translate


class BaseFavoriteActions(BrowserView):


    def add(self):
        request = self.request
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        view = request.get('view', '')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        site = getNavigationRootObject(self.context, portal)
        IFavoriteStorage(site).add_favorite(user.getId(),
                id=IUUID(self.context),
                type='uid',
                view=view,
                date=datetime.now())

    def remove(self):
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        site = getNavigationRootObject(self.context, portal)
        IFavoriteStorage(site).remove_favorite(user.getId(),
                                               IUUID(self.context))


class FavoriteActions(BaseFavoriteActions):

    def add(self):
        request = self.request
        view = request.get('view', '')
        super(FavoriteActions, self).add()

        statusmsg = IStatusMessage(request)
        if IFolderish.providedBy(self.context):
            statusmsg.add(_("The folder has been added to your favorites"))
        else:
            statusmsg.add(_("The document has been added to your favorites"))

        request.response.redirect(self.context.absolute_url() + '/' + view)

    def remove(self):
        super(FavoriteActions, self).remove()

        statusmsg = IStatusMessage(self.request)
        if IFolderish.providedBy(self.context):
            statusmsg.add(_("The folder has been removed from your favorites"))
        else:
            statusmsg.add(_("The document has been removed from your favorites"))

        self.request.response.redirect(self.context.absolute_url())


def json(method):

    def json_method(*arg, **kwargs):
        value = method(*arg, **kwargs)
        return JSONEncoder().encode(value)

    return json_method


class AjaxFavoriteActions(BaseFavoriteActions):

    @json
    def add(self):
        super(AjaxFavoriteActions, self).add()

        if IFolderish.providedBy(self.context):
            msg = _("The folder has been added to your favorites")
        else:
            msg = _("The document has been added to your favorites")

        return {'status': 'favorite-on',
                'msg': translate(msg, context=self.request)}

    @json
    def remove(self):
        super(AjaxFavoriteActions, self).remove()

        if IFolderish.providedBy(self.context):
            msg = _("The folder has been removed from your favorites")
        else:
            msg = _("The document has been removed from your favorites")

        return {'status': 'favorite-off',
                'msg': translate(msg, context=self.request)}

