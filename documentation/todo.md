   
generic agents 


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
