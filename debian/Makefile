all: python-odml.install python-odml-gui.install
	cd ..; debian/rules clean

tmp:
	cd ..; fakeroot debian/rules install

python-odml.install: tmp
	find tmp -type f | egrep -v -e "(gui|pixmap|desktop)" | sed s~tmp~~ > $@

python-odml-gui.install: tmp
	find tmp -type f | egrep -e "(gui|pixmap|desktop)" | sed s~tmp~~ > $@
