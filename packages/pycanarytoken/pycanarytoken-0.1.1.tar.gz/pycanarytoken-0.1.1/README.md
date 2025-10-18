# PyCanarytoken

مكتبة انشاء روابط ملغمه تكدر تعرف بيها ايبي الشخص هواي اشياء عن الجهاز

## Installation

```bash
pip install pycanarytoken
```

## Usage

```python
from pycanarytoken_lib import crtoken, getemail, exlink
email = getemail()
result = crtoken("d3aece8093b71007b5ccfedad91ebb11", "gitlab", email, "test_memo", "idp_app")
link = exlink(result)
print(link)
```

