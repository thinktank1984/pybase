/proposal refactor_code refacore the code based on active record design pattern. 
    review each file and check if it is required
    check each class and check if it is required
    check each method and check if it is required
    check each function and check if it is required
    succinct is better

/proposal add_typing 
    add Pyright 
    first Use MonkeyType  uv pip install monkeytype
    then apply to each file
    <>Use MonkeyType
    pip install monkeytype
    Run your app/tests normally to collect runtime traces:
    python -m monkeytype run your_app.py
    Then apply inferred types:
    monkeytype apply your_module
    It inserts inferred annotations directly into the code based on runtime data — a great way to bootstrap typing for legacy projects.<>


/proposal add-realtime-pub-sub-support
<>
    / subscribe to changes in any record from the 'example' collection
    pb.collection('example').subscribe('*', function (e) {
        console.log(e.record);
    });
y default PocketBase sends realtime events only for Record create/update/delete operations (and for the OAuth2 auth redirect), but you are free to send custom realtime messages to the connected clients via the $app.subscriptionsBroker() instance.

$app.subscriptionsBroker().clients() returns all connected subscriptions.Client indexed by their unique connection id.

The current auth record associated with a client could be accessed through client.get("auth")    
<>
/proposal create a celery task that spawn agent
---

