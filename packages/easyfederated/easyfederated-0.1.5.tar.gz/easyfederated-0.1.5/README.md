## Easyfed

- Tell about architecture compatibility right now
- You should have access via ssh to the machines


### Pros:
 - True reproducibility with nix.
 - No need to install python, torch, etc, on the others machines, just works like magic!
 - Easier implementation of federated learning scatter and gather workflow
 - You can allways migrate your code to nvidia flare if you want!

 ## Fix:

Why hardcode on prod\_00/admin@pablofraile.net on the fed\_admin.json information, the :
admin: {
    ...
    username: "admin@pablofraile.net",
    ..
}
