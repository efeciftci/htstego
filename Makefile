setup:
	pip install -r requirements.txt

clean:
	rm -vf output/*.png
	rm -vrf __pycache__/
