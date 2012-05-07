all: clean python-odml.install python-odml-gui.install

.PHONY : clean
clean:
	cd ..; debian/rules clean
	rm python-odml.install python-odml-gui.install

tmp:
	cd ..; fakeroot debian/rules install

python-odml.install: tmp
	find tmp -type f | egrep -v -e "(gui|pixmap|desktop)" | sed s~tmp~~ | sort > $@

python-odml-gui.install: tmp
	find tmp -type f | egrep -e "(gui|pixmap|desktop)" | sed s~tmp~~ | sort > $@
