import unittest
import odml.tools.event
from test.samplefile import parse
import odml
from odml.tools import proxy


class TestProxy(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.doc = parse("""
        s1[t1]
        - s2[t2]
          - p1
        """)

    def test_private_events(self):
        event_log = []

        def record(context):
            event_log.append((context.obj, context.action, context.val))

        p = odml.Property(name="p", value="1")
        p.add_change_handler(record)
        p.value = "2"
        p.value = "1"

        log1 = event_log
        event_log = []

        pp = proxy.PropertyProxy(p)
        pp.value = "2"
        pp.value = "1"

        self.assertEqual(log1, event_log)

        p.remove_change_handler(record)
        pp.add_change_handler(record)
        event_log = []

        pp.value = "2"
        pp.value = "1"

        self.assertEqual(log1, event_log)

    def test_section_events(self):
        s = odml.Section("sec1")
        p = odml.Property(name="p", value="1")
        s.append(p)

        event_log = []

        def record(context):
            event_log.append((context.obj, context.action, context.val))

        s.add_change_handler(record)
        p.value = "2"
        p.value = "1"

        log1 = event_log
        event_log = []

        s.remove_change_handler(record)

        ps = proxy.NonexistantSection("psec")
        pp = proxy.PropertyProxy(p)
        ps.append(pp)

        ps.add_change_handler(record)
        p.value = "2"
        p.value = "1"
        self.assertEqual(log1, event_log)

    def test_proxy_equality(self):
        p = odml.Property(name="p", value="1")
        pp = proxy.PropertyProxy(p)
        self.assertTrue(p == pp)

        s = odml.Section(name="sec1")
        ps = proxy.MappedSection(s)
        s.append(p)
        self.assertEqual(s, ps)

    def test_section_proxy(self):
        s = odml.Section("sec1")
        p = odml.Property(name="p", value="1")
        s.append(p)

        ps = proxy.MappedSection(s)

        # forward attributes
        ps.name = "sec2"
        self.assertEqual(s.name, "sec2")

        p2 = odml.Property(name="p2", value="2")

        # append to proxy section, creates a proxy in ps
        # and the original object in s
        ps.append(p2)

        self.assertIn(p2, s)
        self.assertIn(p2, ps)
        self.assertIs(s.contains(p2), p2)
        self.assertIsInstance(ps.contains(p2), proxy.Proxy)

        # removing from proxy section, removes both
        ps.remove(p2)
        self.assertNotIn(p2, s)
        self.assertNotIn(p2, ps)

        # appending to section, creates a proxy in ps
        s.append(p2)
        self.assertIn(p2, s)
        self.assertIn(p2, ps)
        self.assertIs(s.contains(p2), p2)
        self.assertIsInstance(ps.contains(p2), proxy.Proxy)

        # removing removes from ps too
        s.remove(p2)
        self.assertNotIn(p2, s)
        self.assertNotIn(p2, ps)

        # appending creates in both, removing in ps removes in both
        s.append(p2)
        ps.remove(p2)
        self.assertNotIn(p2, s)
        self.assertNotIn(p2, ps)

        # append a proxy to ps, both original and proxy compare to
        # be 'in' ps
        pp = proxy.PropertyProxy(p)
        # you can use proxy_append to add an explicit proxy obj (without affecting
        # the original section) or you can append the object to the original section
        # so that the proxy object is created in the proxy section, too
        ps.proxy_append(pp) # this one is only in ps
        self.assertIn(pp, ps)
        self.assertIn(p, ps) # as p == pp, this also holds true

        # even if the name is changed
        ps.name = "p3"
        self.assertEqual(p.name, "p") # does not change the name of p
        self.assertEqual(ps.name, "p3") # but the one of ps

        self.assertIn(pp, ps) # both are in ps though
        self.assertIn(p, ps)

        # and we can remove it again
        ps.remove(p)
        self.assertNotIn(p, ps)
        self.assertNotIn(pp, ps)
        self.assertNotIn(p, s)

        s2 = odml.Section("sec3")
        # a mapped section added to another mapped section
        # will only appear there
        ps2 = proxy.MappedSection(s2)
        ps.proxy_append(ps2)

        self.assertIn(ps2, ps)
        self.assertIn(s2, ps)
        self.assertNotIn(s2, s)

        # and we can remove it again
        ps.remove(s2)
        self.assertNotIn(ps2, ps)
