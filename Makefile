run:
	python3 a_maze_ing.py config.txt

lint:
	mypy a_maze_ing.py config_parser.py

clean:
	rm -rf __pycache__ .mypy_cache
