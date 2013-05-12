
PHONY: clean flakes


clean:
	find -name \*.pyc -exec {} \;

flakes:
	pyflakes bin/* rssdigest tests
