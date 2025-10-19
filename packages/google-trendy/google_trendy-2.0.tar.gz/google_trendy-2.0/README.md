[![Generic badge](https://img.shields.io/badge/Licence-MIT-blue.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Maintained-yes-green.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Python-3.10-yellow.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/google_trendy-2.0-red.svg)](https://pypi.org/project/google-trendy/)
[![Build](https://github.com/michaelMondoro/google_trendy/actions/workflows/publish_pypi.yml/badge.svg)](https://github.com/michaelMondoro/google_trendy/actions/workflows/publish_pypi.yml)

## Package
Package for getting and analyzing tending Google searches

## Usage
```python
from google_trendy import *

tracker = GoogleTrends()
tracker.get_trends()
for trend in tracker.trends:
    print(trend)


# Example Output
GTrend(title='ole miss vs georgia', volume=500000, start=2025-10-18 07:00)
GTrend(title='no kings', volume=500000, start=2025-10-18 10:00)
GTrend(title='lsu vs vanderbilt', volume=500000, start=2025-10-18 03:50)
GTrend(title='tornado watch', volume=500000, start=2025-10-18 18:20)
GTrend(title='tennessee vs alabama', volume=200000, start=2025-10-18 07:30)
```
