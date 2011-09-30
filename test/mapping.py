#-*- coding: utf-8
import unittest

import odml
import odml.tools.treemodel.mixin
import odml.tools.gui.commands as commands
import odml.terminology
import odml.tools.dumper as dumper
import samplefile

import odml.mapping as mapping

import re

def parse(data):
    #pat = re.compile(r'(?P<name>\w+)(\[(?P<type>\w+)\])?(\s+mapping \[(?P<dsttype>\w+)(:(?P<dstname>\w+))?\])?')
    lines = data.strip(" ").strip("\n").split("\n")
    offset = len(re.compile('(\s*)').match(lines[0]).group())
    pat = re.compile(r'(?P<name>\w+)(\[(?P<type>\w+)\])?(\s+mapping \[(?P<dst>[\w:]+)\])?(\s+linked to (?P<link>[\w/]+))?')
    parents = [odml.Document(), None]
    for line in lines:
        line = line[offset:]
        while len(parents) > 1:
            parpref =(len(parents)-2)*2
            if line.startswith(" " * parpref):
                line = line[parpref:]
                break
            parents.pop()

        if line.startswith('- '):
            line = line[2:]
        else:
            parents.pop()

        try:
            m = pat.match(line).groupdict()
        except:
            print "error parsing", repr(line)
            raise
        if m['type'] is None:
            obj = odml.Property(name=m['name'], value="[val]")
        else:
            obj = odml.Section(name=m['name'], type=m['type'])
        if m['dst'] is not None:
            obj.mapping = 'map#%s' % m['dst']
        if m['link'] is not None:
            obj._link = m['link']
        parents[-1].append(obj)
        parents.append(obj)
    return parents[0]

class TestMapping(unittest.TestCase):

    def check(self, src, dst):
        map = mapping.create_mapping(src)
        if map != dst:
            dumper.dumpDoc(map)
            print "---- vs ----"
            dumper.dumpDoc(dst)
        self.assertEqual(map, dst)
        self.assertEqual(dst, map) # do the vice versa test too

    def test_parse(self):
        s = """
        s1[t1] mapping [T1]
        - p1 mapping [T2:P2]
        - s2[t2] mapping [T2]
          - p3
          - p4 mapping [T3:P1]
        s2[t1]
        - s21[t2] linked to /s1/s2
        """
        doc = parse(s)
        #for sec in doc:
        #    dumper.dumpSection(sec)

    def test_rule1(self):
        """
        1. Sections und Properties koennen Mapping Information tragen. Wenn keine
           vorhanden ist, kann diese auch in einer eventuell angegebenen Terminologie
           zu finden sein.
        1. Enthält eine Section ein Mapping, dann ändert sich der Typ der Section,
           der Name wird übernommen.
           s1[t1] mapping [T1] --> s1[T1]
        """
        odml.terminology.terminologies['map'] = parse("S1[T1]")
        odml.terminology.terminologies['term'] = parse("SX[t1] mapping [T1]")
        src = parse("s1[t1]")
        dst = parse("s1[T1]")
        src.repository = 'term'
        dst.repository = 'term' # dst needs to be equal to src for the comparism
        self.check(src, dst)

    def test_rule2(self):
        """
        2. Enthält eine Section kein Mapping und es gibt auch keines in der
           Terminologie, dann bleibt alles beim alten
        """
        src = parse("s1[t1]")
        dst = parse("s1[t1]")
        self.check(src, dst)

        odml.terminology.terminologies['map'] = parse("""
        S1[T1]
        S11[T11]
        S21[T21]
        """)
        src = parse("""
        s1[t1] mapping [T1]
        - s11[t11] mapping [T11]
        - s12[t12]
        s2[t2]
        - s21[t21] mapping [T21]
        """)
        dst = parse("""
        s1[T1]
        - s11[T11]
        - s12[t12]
        s2[t2]
        - s21[T21]
        """)
        self.check(src, dst)

    def test_rule3(self):
        """
        3: Enthält eine Property kein Mapping und es ist auch keines in der
           Terminologie vorhanden, so bleibt alles beim Alten. Die Property landet
           in der Section, in die sein Elternteil gemappt wurde.
        """
        odml.terminology.terminologies['map'] = parse("S1[T1]")
        src = parse("""
        s1[t1] mapping [T1]
        - p1
        """)
        dst = parse("""
        s1[T1]
        - p1
        """)
        self.check(src, dst)

        src = parse("""
        s1[t1]
        - p1
        """)
        dst = src.clone()
        self.check(src, dst)

    def map_rule4(self):
        """
        set up the terminology for rule4 tests
        """
        odml.terminology.terminologies['map'] = parse("""
        S1[T1]
        - P2
        S2[T2]
        - P1
        S3[T3]
        - P1
        - P2
        - P3
        """)

    def test_rule4c(self):
        """
        4. Wenn ein mapping vorhanden ist, dann gilt es verschiedenes zu überprüfen.
           Hier muss beachtet werden, ob es eine Abhängigkeit gibt die beachtet
           werden und erhalten werden müssen...
        4c: Ist der Zieltyp gleich dem der Elternsection, oder nicht?
            Wenn ja, dann einfach hinzufügen. (s3.p1 und s3.p2)
        """
        self.map_rule4()
        src = parse("""
        s3[t3] mapping [T3]
        - p1 mapping [T3:P2]
        - p2 mapping [T3:P3]
        """)
        dst = parse("""
        s3[T3]
        - P2
        - P3
        """)
        self.check(src, dst)

    def test_rule4d1(self):
        """
        4d: Wenn dem nicht so ist (Elternsection != Zieltyp), dann wird zunächst
            überprüft, ob eine Kindsection der gemappten Elternsection dem
            geforderten Typ entspricht.
        4d1: Wenn ja, dann dahin (wenn eindeutig TODO) weil dies die stärkste Verwandschaftsbeziehung darstellt.
        """
        self.map_rule4()
        src = parse("""
        s1[t1]
        - s2[t2] mapping [T2]
        - p2 mapping [T2:P1]
        """)
        dst = parse("""
        s1[t1]
        - s2[T2]
          - P1
        """)
        self.check(src, dst)

    def test_rule4d2(self):
        """
        4d2: Wenn nicht (mehrere Kinder des Typs), MappingError
        """
        self.map_rule4()
        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        - s2[t2] mapping [T2]
        - s3[T2]
        """)
        dst = parse("""
        s1[t1]
        - s2[T2]
        - s3[T2]
        S2[T2]
        - P1
        """)
        with self.assertRaises(mapping.MappingError):
            self.check(src, dst)

    def test_rule4e1(self):
        """
        4d3: Wenn nicht (keine Kinder des Typs), dann gehe ich im Moment nur
             einen Schritt nach oben und überprüfe,
        4e:  ob eine Geschwistersection der gemappten Elternsection dem Property
             Zieltypen entspricht.
        4e1: Wenn ja und diese nur eine related-section des Typs der gemappten
             Elternsection hat, dort hinzufügen
        """
        self.map_rule4()
        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        s2[t2] mapping [T2]
        """)
        dst = parse("""
        s1[t1]
        s2[T2]
        - P1
        """)
        self.check(src, dst)

    def test_rule4e2(self):
        """
        4e2: Wenn ja und diese mehrere related-section des Typs der gemappten
             Elternsection hat, die Section mit einem link erstellen
        """
        self.map_rule4()
        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        s2[t2] mapping [T2]
        s3[t1]
        """)
        dst = parse("""
        s1[t1]
        - s2[T2] linked to /s2
          - P1
        s2[T2]
        s3[t1]
        """)
        self.check(src, dst)

        # nochmal das selbe mit entfernterer verwandtschaft
        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        s2[t2] mapping [T2]
        - s3[t1]
        """)
        dst = parse("""
        s1[t1]
        - s2[T2] linked to /s2
          - P1
        s2[T2]
        - s3[t1]
        """)
        self.check(src, dst)

    def test_rule4f(self):
        """
        4f: Wenn nicht (kein Geschwister des Typs),
            dann erstelle eine entsprechende Section, füge sie mit Property der
            Elternsection hinzu
            (TODO oder auch nur wenn nicht mehr als eine related section der gemappten Elternsection?)
        """
        self.map_rule4()
        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        """)
        dst = parse("""
        s1[t1]
        - S2[T2]
          - P1
        """)
        self.check(src, dst)


        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        s2[t1]
        """)
        dst = parse("""
        s1[t1]
        - S2[T2]
          - P1
        s2[t1]
        """)
        self.check(src, dst)

    def test_multiple(self):
        self.map_rule4()
        src = parse("""
s1[t1] mapping [T1]
- p1 mapping [T2:P1]
- p2 mapping [T1:P2]
- p3
- p4 mapping [T3:P1]
s2[t1] mapping [T1]
- p1 mapping [T2:P1]
- p2 mapping [T1:P2]
- p3
- p4 mapping [T3:P1]
s3[t3] mapping [T3]
- p1 mapping [T3:P2]
- p2 mapping [T3:P3]
        """)
        dst = parse("""
s1[T1]
- P2
- p3
- S2[T2]
  - P1
- s3[T3] linked to /s3
  - P1
s2[T1]
- P2
- p3
- S2[T2]
  - P1
- s3[T3] linked to /s3
  - P1
s3[T3]
- P2
- P3
        """)
        self.check(src, dst)

    def test_editing(self):
        self.map_rule4()
        src = parse("""
        s1[t1]
        - p2 mapping [T2:P1]
        s2[t2] mapping [T2]
        """)

        src['s1'].properties['p2'].mapping = 'map#T3:P1'
        dst = parse("""
        s1[t1]
        - S3[T3]
          - P1
        s2[T2]
        """)
        self.check(src, dst)

        src['s1'].properties['p2'].mapping = 'map#T2:P1'
        dst = parse("""
        s1[t1]
        s2[T2]
        - P1
        """)
        self.check(src, dst)

        with self.assertRaises(mapping.MappingError):
            src['s2'].mapping = 'map#T3'

        src['s1'].properties['p2'].mapping = ''
        dst = parse("""
        s1[t1]
        - p2
        s2[T2]
        """)
        self.check(src, dst)

        src['s1'].mapping = 'map#T1'
        dst = parse("""
        s1[T1]
        - p2
        s2[T2]
        """)
        self.check(src, dst)

if __name__ == '__main__':
    unittest.main()
