/proposal refactor_code refacore the code based on active record design pattern. 
    review each file and check if it is required
    check each class and check if it is required
    check each method and check if it is required
    check each function and check if it is required
    succinct is better

/proposal add typing Pyright 
first Use MonkeyType  uv pip install monkeytype
then apply to each file
<>Use MonkeyType
pip install monkeytype
Run your app/tests normally to collect runtime traces:
python -m monkeytype run your_app.py
Then apply inferred types:
monkeytype apply your_module
It inserts inferred annotations directly into the code based on runtime data — a great way to bootstrap typing for legacy projects.<>


/proposal realtime pub sub support

/proposal create a celery task that spawn agent
---

