# Formal Verifications of Bayesian Network Classifiers 

## **Setup**

1. Cloning the repository
	```bash
	git clone --recursive git@github.com:autonlab/bnc-formal-verification.git
	```

2. Check if submodules are cloned
There should be directory src/bnc_sdd. If not, run
	```bash
	git submodule update --init --recursive
	```

3. Install dependencies
	```bash
	python3 -m pip install -r requirements.txt
	```

4. Create pysmile_license.py under src/ directory and paste the license key. It should look like this:
	```python
	import pysmile

	pysmile.License((
		b"SMILE LICENSE XXXXXXXX XXXXXXXX XXXXXXXX "
		b"THIS IS AN ACADEMIC LICENSE AND CAN BE USED "
		b"SOLELY FOR ACADEMIC RESEARCH AND TEACHING, "
		b"AS DEFINED IN THE BAYESFUSION ACADEMIC "
		b"SOFTWARE LICENSING AGREEMENT. "
		b"Serial #: .................. "
		b"Issued for: Michael Jackson (mjackson@la.edu) "
		b"Academic institution: Some Institution "
		b"Valid until: 2023-12-04 "
		b"Issued by BayesFusion activation server"
		),[
		XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,
		XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,
		XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,
		XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX,XXXX])

	```
***

## **Current workflow**
(Assuming that you're in the /src directory.)

### **To convert a Bayesian Network that is saved in pysmile format .xdsl to .net format, run**
This requires:
1. A .xdsl file that contains the Bayesian Network
```bash
python3 scripts/convert_to_shih.py --input_file <input_file> --output_file <output_file>
# e.g. python scripts/convert_to_shih.py --input_file models/simple_weather_model.xdsl --output_file bnc_networks/weather.net
```

### **To build Ordered Decision Diagrams (ODDs) from a .net file, run:**
This requires:
1. A .net file that contains the Bayesian Network
2. A .json file that contains the configuration of the Bayesian Network
```bash
python3 convert_net_to_odd.py --netconfigpath <netconfigpath> --netfilepath <netfilepath>
# e.g. python convert_net_to_odd.py --netconfigpath "bnc_configs/weather.json" --netfilepath bnc_networks/weather.net
```

### **To parse and display ODD(or OBDD) from .odd file, run:**
This requires:
1. A .odd file that contains the ODD
```bash
python3 shih_to_obdd --filepath <filepath> (optional: --plot <True/False, default=True>)
# e.g. python shih_to_obdd.py --filepath odd_models/weather/weather_1.odd
```


***
## License
tbd