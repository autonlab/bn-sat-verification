# Formal Verifications of Bayesian Network Classifiers 

## Setup

1. Cloning the repository
```
git clone --recursive git@github.com:autonlab/bnc-formal-verification.git
```

2. Check if submodules are cloned
There should be directory src/bnc_sdd. If not, run
```
git submodule update --init --recursive
```

3. Install dependencies
```
python3 -m pip install -r requirements.txt
```

4. Create pysmile_license.py under src/ directory and paste the license key. It should look like this:
```
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