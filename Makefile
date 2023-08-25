setup:
	pip install -r requirements.txt

clean:
	rm -vf src/output/*.png
	rm -vrf src/__pycache__/
