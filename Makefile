# Makefile för Luna the FOX

.PHONY: run build clean

# Kör spelet
run:
	python3 main.py

# Bygg körbar fil (både Linux och Windows)
build:
	pyinstaller --onefile --name "Luna the FOX" --windowed --clean main.py

# Rensa byggfiler
clean:
	rm -rf build dist __pycache__ *.spec
