# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.twitter.portlets import twsearch
from collective.twitter.portlets.testing import INTEGRATION_TESTING


class PortletTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        name = 'collective.twitter.portlets.TwitterSearchPortlet'
        portlet = getUtility(IPortletType, name=name)
        self.assertEqual(portlet.addview, name)

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = twsearch.Assignment(tw_account=u"test",
                                      search_string=u"Test",
                                      show_avatars=False,
                                      max_results=20)

        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        name = 'collective.twitter.portlets.TwitterSearchPortlet'
        portlet = getUtility(IPortletType, name=name)
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add
        # form.
        # Note: if the portlet has a NullAddForm, simply call
        # addview() instead of the next line.
        addview.createAndAdd(data={'tw_account': u"test",
                                   'search_string': u"Test",
                                   'show_avatars': False,
                                   'max_results': 20})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(isinstance(mapping.values()[0], twsearch.Assignment))

    def test_invoke_edit_view(self):
        # NOTE: This test can be removed if the portlet has no edit form
        mapping = PortletAssignmentMapping()
        request = self.request

        mapping['foo'] = twsearch.Assignment(tw_account=u"test",
                                             search_string=u"Test",
                                             show_avatars=False,
                                             max_results=20)

        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.assertTrue(isinstance(editview, twsearch.EditForm))

    def test_obtain_renderer(self):
        context = self.portal
        request = self.request
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = twsearch.Assignment(tw_account=u"test",
                                         search_string=u"Test",
                                         show_avatars=False,
                                         max_results=20)

        renderer = getMultiAdapter((context, request, view, manager, assignment),
                                   IPortletRenderer)
        self.assertTrue(isinstance(renderer, twsearch.Renderer))


class RenderTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
                                        name='plone.rightcolumn',
                                        context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment
        # constructor.
        assignment = assignment or twsearch.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        # TODO: Pass any keyword arguments to the Assignment constructor.
        r = self.renderer(context=self.portal,
                          assignment=twsearch.Assignment(tw_account=u"test",
                                                         search_string=u"Test",
                                                         show_avatars=False,
                                                         max_results=20))
        r = r.__of__(self.portal)
        r.update()
        #output = r.render()
        # TODO: Test output


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
